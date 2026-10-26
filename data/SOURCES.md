# Data som hostas av webbplatsen

- `dist/index.html` innehåller sidans statistikserier, geometrier och kartfunktionens data som inbäddade dataobjekt. De öppna datakorten för SMHI:s emissionsdatabas, luftkvalitet, meteorologiska observationer och Folkhälsomyndighetens valdeltagandetabell är endast källänkar; de laddas inte vid sidvisning och ingår inte som data i jämförelsekartorna.
- `dist/baninfo-jarnvagsnat.png` är en statisk PNG-ögonblicksbild av Trafikverkets BanInfo WMS, lager `Jarnvagsnat`, bbox `10.5,54.5,25,69.5`, 900 × 620 px, hämtad 2026-10-23. Ursprunglig WMS: https://geo-baninfo.trafikverket.se/mapservice/wms.axd/BanInfo_1_5. Trafikverkets metadata beskriver järnvägsdata-visningstjänsten som öppna data; ange Trafikverket som källa.
- SMHI:s data får enligt SMHI kopieras, distribueras och bearbetas enligt CC BY 4.0 SE med källa och uppgift om ändringar. Inga SMHI-dataset är inlästa i denna version.

- PTS-data från datasetserien [Mobiltäcknings- och bredbandskartläggning](https://www.dataportal.se/dataset-series/195_7646), via Koladas öppna API: fast bredband ≥100 Mbit/s (2009–2025), ≥1 Gbit/s totalt/tät-/glesbygd (2017–2025). Bredbandskollen/Internetstiftelsen: uppmätt fast och mobil nedladdningshastighet (2021–2025). Värden och metadata hämtades 2026-10-24 och bäddas in i `dist/index.html`; webbplatsen gör inga dataanrop vid sidvisning. Ange `Källa: Kolada` enligt [Koladas användarvillkor](https://www.kolada.se/om-oss/api/). PTS redovisar fast/trådlös bredbandstillgång aggregerad per kommun, län och riket; mobiltäckning samlas in i rutor och är inte en av de här sex kommun/länserierna.

- PTS mobile coverage is also included from the official [annual workbooks](https://statistik.pts.se/mobiltacknings-och-bredbandskartlaggning/dokument-rapporter): land-area coverage for all operators at ≥10 Mbit/s (2020–2025), a separate 5G ≥10 Mbit/s series (2020–2024), 2025 all-operator 5G coverage, and the 2025 share of populated areas with good mobile capacity. Values are embedded in `dist/index.html`; maps show PTS national, county and municipality aggregates. These are not person-level coverage percentages. PTS notes the grid resolution changed in 2020; the historical 5G threshold is kept separate from the 2025 snapshot because their definitions differ.

- SCB tätortsgränser are bundled from the official WFS GeoPackage layers for 1980, 1990, 1995, 2000, 2005, 2010, 2015, 2018 and 2020. The 2023 vintage was already included in the site data. Historical geometries are simplified for web display and transformed into the site's existing map coordinates; population and land area are retained per locality. They are loaded from local `dist/data/tatorter-*.json` files, never fetched from SCB at runtime. SCB publishes the data under CC0: [Statistiska tätorter](https://www.scb.se/vara-tjanster/oppna-data/oppna-geodata/statistiska-tatorter/) and [SCB terms for open data](https://www.scb.se/vara-tjanster/oppna-data/).


## Additional SCB WFS layers · retrieved 2026-10-24

Local files in dist/data/geodata; explorer at /geodata/.
Small localities: 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2023.
Urban green areas: 2010, 2015, 2020. Coverage/methods differ; regional aggregation uses the locality-code prefix, not municipal clipping.
Business areas: 2015, 2020. Older workplace areas outside urban localities: 2000, 2005, 2010; separate definitions and series.
DeSO: 2018, 2025. RegSO: 2020, 2025. Boundary vintages, not demographic observations.
Population kilometre grid: annually 2015–2025, total/men/women; disclosure protection can cause sums to differ. Grid geometry is reconstructed from SCB grid identifiers.
Source: https://geodata.scb.se/geoserver/stat/wfs
Definitions: https://www.scb.se/vara-tjanster/oppna-data/oppna-geodata/
Pipeline: data/fetch-scb-extra.py then data/build-scb-extra.py. Geometry simplified with 30 metre tolerance and rounded to metres in SWEREF99 TM. Ten regional indicators sum source attributes. Historical municipality codes retained. Large files split into local parts.

Original downloaded retail/holiday-area GeoJSON copies are losslessly compressed as .geojson.gz to fit the publication asset limit.


## Police classified areas · 2025 snapshot
Official source: https://polisen.se/om-polisen/polisens-arbete/utsatta-omraden/
Downloaded GeoJSON ZIP retained locally as dist/data/polisens-utsatta-omraden-2025.zip.
65 areas, including 19 particularly vulnerable areas. Municipality assignment matches ORT to municipality names, with Västra Frölunda mapped to Göteborg and Upplands Bro to Upplands-Bro. Counts refer to areas, not whole-municipality classifications, crime rates or individual risk. No historic backfill. Local polygons retain category, official names and source dates; viewed in Geodata. Aggregated counts appear in maps, county table and Focus, where category context is included. Retrieved 24 October 2026.
