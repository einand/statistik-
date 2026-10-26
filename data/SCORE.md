# Boendepoäng, metod 1.0.0

`dist/assets/score-engine.js` innehåller den gemensamma beräkningen för alla kommuner. `data/build-score.mjs` läser befintlig kommundata i `dist/index.html`, tar bara relevanta källmått och bygger lokala poängfiler. Inga externa API-anrop görs i besökarens webbläsare.

## Omräkning

Kör `python data/prepare-public.py`. Den kör poängbygget före paketering. Relevant indata och motorkod kontrollsummeras. Om data eller beräkning ändrats sparas en ny oföränderlig standardutgåva i `dist/data/score-history/`. Oförändrad indata skapar inte en ny utgåva. Historiken innehåller poäng, placering, täckning, kommentarer, metodparametrar och kontrollsumma från 2010 till publiceringsåret. Detta är en historisk jämförelse med dagens tillgängliga källutgåvor, inte ett påstående om vad webbplatsen visade vid den historiska tidpunkten.

Nya statistiska observationer i modellens valda serier slår automatiskt igenom. Nya sorters mått ska först metodbedömas: riktning, geografisk nivå, överlapp, aktualitet och täckning. Byt metodversion när urval, viktregler, åldersgränser eller poängformel ändras. Uppdatera även fokusvyns förklaring.

## Urval och avvägningar

Se `BESLUT.md` och metoden som visas på `/score/`. Modellen är ett uttalat värderingsval, ingen officiell kvalitetsbedömning. Tillgång till kommunala miljö-/resmått är otillräcklig i aktuellt underlag. Vardagstemat visar därför bara bredband och heter Vardag och uppkoppling. Hög bostadsproduktion är en proxy för utbud, inte ett mått på pris eller faktisk bostadstillgång. Äldres trivsel utomhus beskriver en del av omsorgen, inte hela omsorgskvaliteten. Hälsan påverkas av befolkningens sammansättning; modellen fastställer inga lokala orsaker.

Percentilpoäng beräknas inom ett måtts kommunurval med medelrang för lika värden; nollbaserad rang delas med antal minus ett och multipliceras med hundra. Negativ riktning vänds. Teman använder medel av tillgängliga delpoäng. Ingen imputering eller läns-/riksersättning sker. Poäng kräver minst åttio procent täckning och minst hälften av måtten i varje aktivt tema. Den redovisade täckningen gäller just valda vikter.

Standardresultatet i fokusvyn kommer från samma motor. Det har en lättläst, sifferfri kommentar och ett separat numeriskt datafält. Kommunlänkar från listan använder verifierad kommunkod och valt år.

## Kontroller

`node tests/score-engine.cjs` verifierar riktning, rangbindning, historisk tidsgräns, för gamla observationer, saknade teman, livslängdsmåttet, viktval, täckning och verklig kommunindata. Poängsidans laddning, sökning utan accent, oförändrad nationell placering vid sökning, källdetaljer, nollvikter, återställning och årbyte kontrollerades också genom exekvering av den riktiga sidkoden med lokal data.
