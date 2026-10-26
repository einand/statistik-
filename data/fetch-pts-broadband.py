"""Download and embed selected PTS broadband series published via Kolada.

The static site reads these rows from its inline JSON payload. Browsers do not
make requests to Kolada or PTS at runtime.
"""
from __future__ import annotations

import json
import math
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent
SITE = ROOT.parent / "dist" / "index.html"
YEARS = ",".join(str(year) for year in range(2007, 2026))
SPECS = [
    ("broadband100", "N07900", "Tillgång till fast bredband ≥100 Mbit/s", "%", "Bredband"),
    ("broadbandGbit", "N07918", "Tillgång till ≥1 Gbit/s eller fiber i närheten", "%", "Bredband"),
    ("broadbandGbitUrban", "N07919", "≥1 Gbit/s · tätbebyggda områden", "%", "Bredband"),
    ("broadbandGbitRural", "N07920", "≥1 Gbit/s · glesbebyggda områden", "%", "Bredband"),
    ("fixedDownload", "N90002", "Bredbandskollen · nedladdning fast bredband", "Mbit/s", "Uppmätta hastigheter"),
    ("mobileDownload", "N90004", "Bredbandskollen · nedladdning mobilt", "Mbit/s", "Uppmätta hastigheter"),
]
PTS_METRICS = {
    "mobile10Area": {
        "label": "Mobil yttäckning ≥10 Mbit/s · alla operatörer",
        "unit": "%", "group": "Mobiltäckning",
        "description": "Andel landyta som täcks av minst en operatör med minst 10 Mbit/s. Historik 2020–2024 avser samlad 3G/4G/5G-täckning; 2025 är PTS:s aktuella mått för alla operatörer. Grundnivå (0 dB). Beräknat på yta, inte befolkning. Sjöytorna Vänern, Vättern, Mälaren och Östersjön är borträknade.",
        "years": list(range(2020, 2026)), "source": "PTS · Mobiltäcknings- och bredbandskartläggning",
    },
    "mobile5g10": {
        "label": "5G yttäckning ≥10 Mbit/s",
        "unit": "%", "group": "Mobiltäckning",
        "description": "Andel landyta med 5G-täckning för minst 10 Mbit/s. Grundnivå (0 dB). PTS redovisar denna historiska definition 2020–2024; den har inte slagits ihop med 2025 års separata 5G-mått.",
        "years": list(range(2020, 2025)), "source": "PTS · Mobiltäcknings- och bredbandskartläggning",
    },
    "mobile5g2025": {
        "label": "5G yttäckning · PTS 2025",
        "unit": "%", "group": "Mobiltäckning",
        "description": "Andel landyta med 5G-täckning från alla operatörer, enligt PTS:s tabellbilaga 2025. Grundnivå (0 dB). PTS anger inte samma hastighetströskel som i den historiska 5G-serien.",
        "years": [2025], "source": "PTS · Mobiltäcknings- och bredbandskartläggning",
    },
    "mobileGoodPop2025": {
        "label": "Befolkade områden med god mobiltäckning · 2025",
        "unit": "%", "group": "Mobiltäckning",
        "description": "Andel befolkade områden med mobiltäckning motsvarande god kapacitet, enligt PTS delmålsbilaga 2025.",
        "years": [2025], "source": "PTS · Mobiltäcknings- och bredbandskartläggning",
    },
}


def get_json(url: str, attempts: int = 4) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "SverigesBefolkningStatistik/1.0"})
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                return json.load(response)
        except Exception:
            if attempt + 1 == attempts:
                raise
            time.sleep(1 + attempt)
    raise RuntimeError(url)


def fetch_one(spec: tuple[str, str, str, str, str]) -> tuple[str, dict]:
    key, code, label, unit, group = spec
    metadata = get_json(f"https://api.kolada.se/v3/kpi/{code}")["values"][0]
    rows = []
    for region_type in ("municipality", "region"):
        url = (f"https://api.kolada.se/v3/data/kpi/{code}/year/{YEARS}"
               f"?region_type={region_type}&per_page=5000")
        while url:
            page = get_json(url)
            rows.extend(page.get("values", []))
            url = page.get("next_url")
    result = {
        "code": code,
        "label": label,
        "unit": unit,
        "group": group,
        "metadata": metadata,
        "retrieved": "2026-10-24",
        "url": f"https://api.kolada.se/v3/kpi/{code}",
        "rows": rows,
    }
    (ROOT / f"{code}.json").write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return key, result


def embed(downloaded: dict[str, dict]) -> None:
    html = SITE.read_text()
    tag = '<script type="application/json" id="data">'
    start = html.index(tag) + len(tag)
    end = html.index("</script>", start)
    data = json.loads(html[start:end])
    metadata = data.setdefault("extraMetadata", {})
    social = data.setdefault("social", {})
    for key, code, label, unit, group in SPECS:
        raw = downloaded[key]
        series: dict[str, dict[str, float]] = {}
        for row in raw["rows"]:
            geo = str(row["municipality"])
            year = str(row["period"])
            selected = next((value for value in row["values"] if value.get("gender") == "T"), None)
            if not selected or selected.get("isdeleted"):
                continue
            value = selected.get("value")
            if not isinstance(value, (int, float)) or not math.isfinite(value):
                continue
            if geo == "0000":
                geo = "00"
            elif geo.startswith("00") and geo[2:] in data["names"]:
                geo = geo[2:]
            elif geo not in data["municipalities"]:
                continue
            series.setdefault(year, {})[geo] = value
        if not series:
            raise ValueError(f"No observations for {code}")
        if unit == "%":
            for year, places in series.items():
                for geo, value in places.items():
                    if not 0 <= value <= 100:
                        raise ValueError(f"Out-of-range percentage: {code} {year} {geo} {value}")
        social[key] = series
        kpi = raw["metadata"]
        is_pts = code.startswith("N079")
        years = sorted(map(int, series))
        metadata[key] = {
            "code": code,
            "label": label,
            "unit": unit,
            "group": group,
            "definition": kpi.get("description", ""),
            "sourceTitle": kpi.get("title", label),
            "source": "Kolada · underliggande källa: PTS" if is_pts else "Kolada · Bredbandskollen/Internetstiftelsen",
            "url": "https://www.dataportal.se/dataset-series/195_7646" if is_pts else raw["url"],
            "retrieved": "24 oktober 2026",
            "years": years,
            "country": any("00" in places for places in series.values()),
            "county": any(any(code in data["names"] for code in places) for places in series.values()),
            "municipality": any(any(code in data["municipalities"] for code in places) for places in series.values()),
            "count": sum(len(places) for places in series.values()),
        }
    # PTS publishes the mobile coverage tables as downloadable workbooks.
    # Codes match the county and municipality codes used by the site.
    def pct(value):
        if isinstance(value, str) and value.startswith(">99,99"):
            return 99.99
        if isinstance(value, (int, float)) and math.isfinite(value):
            return round(value * 100, 4)
        return None

    def geo_code(raw):
        code = str(raw or "").strip()
        if code.lower() in ("0000", "riket"): return "00"
        if code.startswith("00") and code[2:] in data["names"]: return code[2:]
        if code in data["municipalities"] or code in data["names"]: return code
        return None

    def add_value(target, year, code, value):
        code = geo_code(code); value = pct(value)
        if code and value is not None:
            target.setdefault(str(year), {})[code] = value

    mobile = load_workbook(ROOT / "pts-mobile-2025.xlsx", read_only=False, data_only=True)
    historic = load_workbook(ROOT / "pts-mobile-history-2020-2024.xlsx", read_only=False, data_only=True)
    mobile_hist = historic["Yttäckning - aggregerad"]
    historic_cols = {"mobile10Area": 126, "mobile5g10": 84}
    for key, first_col in historic_cols.items():
        series = {}
        for col in range(first_col, mobile_hist.max_column + 1, 3):
            raw_year = mobile_hist.cell(4, col).value
            if isinstance(raw_year, int) and 2020 <= raw_year <= 2024:
                for row in range(6, mobile_hist.max_row + 1):
                    add_value(series, raw_year, mobile_hist.cell(row, 2).value, mobile_hist.cell(row, col).value)
        if key == "mobile10Area":
            # 2025 PTS table: all operators, at least 10 Mbit/s, 0 dB.
            ws = mobile["Yttäckning 2025"]
            for row in range(4, ws.max_row + 1):
                add_value(series, 2025, ws.cell(row, 2).value, ws.cell(row, 3).value)
        social[key] = series

    # Current 5G coverage: column 15 is all operators, 0 dB.
    series = {}
    ws = mobile["Yttäckning 2025"]
    for row in range(4, ws.max_row + 1):
        add_value(series, 2025, ws.cell(row, 2).value, ws.cell(row, 15).value)
    social["mobile5g2025"] = series

    # PTS's latest indicator for populated areas with good mobile capacity.
    series = {}
    ws = mobile["Delmål 2025"]
    for row in range(4, ws.max_row + 1):
        add_value(series, 2025, ws.cell(row, 2).value, ws.cell(row, 5).value)
    social["mobileGoodPop2025"] = series

    for key, m in PTS_METRICS.items():
        series = social[key]
        metadata[key] = {
            "code": "PTS 2025" if len(m["years"]) == 1 else "PTS historik 2020–2025",
            "label": m["label"], "unit": m["unit"], "group": m["group"],
            "definition": m["description"], "sourceTitle": m["label"],
            "source": m["source"],
            "url": "https://statistik.pts.se/mobiltacknings-och-bredbandskartlaggning/dokument-rapporter",
            "retrieved": "24 oktober 2026", "years": sorted(map(int, series)),
            "country": any("00" in places for places in series.values()),
            "county": any(any(code in data["names"] for code in places) for places in series.values()),
            "municipality": any(any(code in data["municipalities"] for code in places) for places in series.values()),
            "count": sum(len(places) for places in series.values()),
        }
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    SITE.write_text(html[:start] + payload + html[end:])


if __name__ == "__main__":
    cached = {}
    if "--fetch" in sys.argv:
        with ThreadPoolExecutor(max_workers=6) as pool:
            jobs = [pool.submit(fetch_one, spec) for spec in SPECS]
            for future in as_completed(jobs):
                key, result = future.result()
                cached[key] = result
                print(f"Hämtade {key} ({len(result['rows'])} råa rader)", flush=True)
    else:
        for key, code, *_ in SPECS:
            cached[key] = json.loads((ROOT / f"{code}.json").read_text())
    embed(cached)
    print("PTS/Bredbandskollen-data inbäddad i dist/index.html")
