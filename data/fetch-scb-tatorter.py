"""Fetch and simplify SCB's public tätort boundary vintages for local hosting."""
from __future__ import annotations

import json
import math
import sqlite3
import struct
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "dist" / "data"
YEARS = (1980, 1990, 1995, 2000, 2005, 2010, 2015, 2018, 2020)
TARGET = (106.718, 48.087, 406.202, 739.415)  # same local SVG space as the current 2023 town geometry
REFERENCE_BOUNDS_2023 = (276999.1231, 6133891.7294, 916901.5446, 7611042.9010)
SIMPLIFY_METRES = 35.0
BASE = "https://geodata.scb.se/geoserver/stat/wfs"


def download(year: int) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = Path(f"/tmp/scb-tatorter-{year}.gpkg")
    query = urllib.parse.urlencode({
        "REQUEST": "GetFeature", "TYPENAMES": f"stat:Tatorter_{year}",
        "outputFormat": "geopackage", "service": "WFS", "version": "1.1.0",
    })
    request = urllib.request.Request(BASE + "?" + query, headers={"User-Agent": "SwedishHistoricalMaps/1.0"})
    with urllib.request.urlopen(request, timeout=240) as response, path.open("wb") as output:
        while chunk := response.read(1024 * 1024):
            output.write(chunk)
    return path


def read_u32(data: bytes, offset: int, endian: str) -> tuple[int, int]:
    return struct.unpack_from(endian + "I", data, offset)[0], offset + 4


def read_f64(data: bytes, offset: int, endian: str) -> tuple[float, int]:
    return struct.unpack_from(endian + "d", data, offset)[0], offset + 8


def read_wkb(data: bytes, offset: int = 0):
    byte_order = data[offset]
    endian = "<" if byte_order == 1 else ">"
    offset += 1
    geom_type, offset = read_u32(data, offset, endian)
    has_z = geom_type >= 1000 and geom_type < 2000 or geom_type & 0x80000000 != 0
    kind = geom_type % 1000 if geom_type < 10000 else geom_type & 0xFF
    dimensions = 3 if has_z else 2
    if kind == 3:  # Polygon
        ring_count, offset = read_u32(data, offset, endian)
        rings = []
        for _ in range(ring_count):
            count, offset = read_u32(data, offset, endian)
            ring = []
            for _ in range(count):
                x, offset = read_f64(data, offset, endian)
                y, offset = read_f64(data, offset, endian)
                if dimensions == 3: _, offset = read_f64(data, offset, endian)
                ring.append((x, y))
            rings.append(ring)
        return [rings], offset
    if kind == 6:  # MultiPolygon
        count, offset = read_u32(data, offset, endian)
        polygons = []
        for _ in range(count):
            polygon, offset = read_wkb(data, offset)
            polygons.extend(polygon)
        return polygons, offset
    raise ValueError(f"Unsupported WKB geometry type {geom_type}")


def gpkg_polygons(blob: bytes):
    if blob[:2] != b"GP":
        raise ValueError("Invalid GeoPackage geometry header")
    flags = blob[3]
    envelope = (flags >> 1) & 7
    sizes = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}
    return read_wkb(blob, 8 + sizes[envelope])[0]


def point_segment_distance_sq(point, start, end):
    dx, dy = end[0] - start[0], end[1] - start[1]
    if dx == 0 and dy == 0:
        return (point[0]-start[0])**2 + (point[1]-start[1])**2
    t = max(0.0, min(1.0, ((point[0]-start[0])*dx + (point[1]-start[1])*dy) / (dx*dx + dy*dy)))
    x, y = start[0] + t*dx, start[1] + t*dy
    return (point[0]-x)**2 + (point[1]-y)**2


def simplify(points, tolerance_sq):
    if len(points) <= 4:
        return points
    closed = points[0] == points[-1]
    work = points[:-1] if closed else points
    if len(work) <= 3:
        return points
    # Split a closed ring at the point farthest from the first point so the
    # Douglas-Peucker pass preserves both sides of the ring.
    if closed:
        far = max(range(1, len(work)), key=lambda i: (work[i][0]-work[0][0])**2 + (work[i][1]-work[0][1])**2)
        pieces = [work[:far+1], work[far:] + [work[0]]]
        simplified = []
        for piece in pieces:
            part = simplify(piece, tolerance_sq)
            simplified.extend(part if not simplified else part[1:])
        if simplified[0] != simplified[-1]: simplified.append(simplified[0])
        return simplified
    keep = {0, len(work)-1}
    stack = [(0, len(work)-1)]
    while stack:
        start, end = stack.pop()
        best_i, best_d = None, tolerance_sq
        for i in range(start + 1, end):
            distance = point_segment_distance_sq(work[i], work[start], work[end])
            if distance > best_d:
                best_i, best_d = i, distance
        if best_i is not None:
            keep.add(best_i)
            stack.extend(((start, best_i), (best_i, end)))
    return [work[i] for i in sorted(keep)]


def load_features(path: Path):
    db = sqlite3.connect(path)
    table = db.execute("SELECT table_name FROM gpkg_contents WHERE data_type='features'").fetchone()[0]
    rows = db.execute(f'SELECT tatortskod,tatort,kommun,lan,area_ha,bef,sp_geometry FROM "{table}"')
    features = []
    bounds = [math.inf, math.inf, -math.inf, -math.inf]
    for code, name, municipality, county, area, population, geom in rows:
        polygons = gpkg_polygons(geom)
        for polygon in polygons:
            for ring in polygon:
                for x, y in ring:
                    bounds[0] = min(bounds[0], x); bounds[1] = min(bounds[1], y)
                    bounds[2] = max(bounds[2], x); bounds[3] = max(bounds[3], y)
        features.append((code, name, municipality, county, area, population, polygons))
    db.close()
    return features, bounds


def transform_ring(ring, bounds):
    min_x, min_y, max_x, max_y = bounds
    tx0, ty0, tx1, ty1 = TARGET
    width, height = max_x-min_x, max_y-min_y
    result = []
    for x, y in simplify(ring, SIMPLIFY_METRES**2):
        sx = tx0 + (x-min_x)/width*(tx1-tx0)
        sy = ty0 + (max_y-y)/height*(ty1-ty0)
        result.append((sx, sy))
    return result


def encode(features, bounds, year):
    grouped = {}
    for code, name, municipality, county, area, population, polygons in features:
        pieces = []
        xs, ys = [], []
        for polygon in polygons:
            for ring in polygon:
                points = transform_ring(ring, bounds)
                if len(points) < 4: continue
                xs.extend(x for x, _ in points); ys.extend(y for _, y in points)
                pieces.append("M" + "L".join(f"{x:.3f},{y:.3f}" for x, y in points) + "Z")
        if not pieces: continue
        item = {"id": code, "name": name, "d": "".join(pieces),
                "b": [round(min(xs), 3), round(min(ys), 3), round(max(xs), 3), round(max(ys), 3)],
                "population": population, "areaHa": area}
        grouped.setdefault(str(municipality), []).append(item)
    return grouped


def main():
    # 2023 is already bundled in the site's town layer. Its EPSG:3006 extent
    # is the reference used to align the historical snapshots with that map.
    reference_bounds = REFERENCE_BOUNDS_2023
    jobs = {}
    with ThreadPoolExecutor(max_workers=3) as pool:
        for year in YEARS:
            jobs[pool.submit(download, year)] = year
        for job in as_completed(jobs):
            year = jobs[job]
            path = job.result()
            features, bounds = load_features(path)
            grouped = encode(features, reference_bounds, year)
            output = OUT / f"tatorter-{year}.json"
            output.write_text(json.dumps(grouped, ensure_ascii=False, separators=(",", ":")))
            print(f"{year}: {len(features)} tätorter, {sum(len(v) for v in grouped.values())} kartobjekt, {output.stat().st_size:,} byte", flush=True)
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
