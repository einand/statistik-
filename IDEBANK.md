# Idébank – Sverige i siffror

Idéer är förslag, inte beslut om implementation.

## Kommunernas digitala service och fler vardagsmått

**Sparad:** 26 oktober 2026  
**Status:** Idé, inte implementerad.

### Idé

Komplettera officiell statistik med egna, öppet redovisade tester av kommunernas webbplatser. Visa hur lätt det är att hitta information och använda kommunens digitala service. Presentera resultaten med enkla bilder och mycket lätt svenska.

### Egna tester – ”Vår granskning”

- **Digital tillgänglighet:** kontraster, bildbeskrivningar, rubriker, formulärfält, tangentbordsnavigation och skärmläsare.
- **Mobilvänlighet:** knapparnas storlek, läsbar text, menyer och innehåll som hamnar utanför skärmen.
- **Laddningstid:** upprepade mätningar med samma simulerade mobil och uppkoppling.
- **Hitta information:** samma uppgifter hos alla kommuner, exempelvis kontakt, skolmatsedel, bygglov och felanmälan. Mät om uppgiften går att lösa och hur många steg som krävs.
- **Begripligt språk:** svåra ord och långa meningar, kompletterat med manuell bedömning. Ett läsbarhetstal är inte ett bevis på begriplighet.
- **Trasiga länkar:** länkar till sidor och dokument som inte fungerar.
- **Dokument:** sökbar text, dokumentstruktur och läsordning i ett jämförbart urval PDF-filer.
- **Stabilitet:** upprepade kontroller av om webbplatsen svarar under en tydligt angiven mätperiod. Skilj lokal mätstörning från bekräftad otillgänglighet.

### Metod och presentation

- Använd jämförbara urval: startsida, kontakt, skola, bygglov, felanmälan och ett dokument. Redovisa saknade eller otillgängliga tester separat.
- Automatiska tillgänglighetstester kompletteras med manuella tester. Inga upptäckta fel betyder inte att webbplatsen är fullt tillgänglig.
- Redovisa testade adresser, datum, verktyg och version, inställningar, testomfattning samt vilka fynd som är manuellt bekräftade.
- Dokumentera testmiljö, upprepningar, felmarginaler och bedömningsregler. Jämför inte resultat från olika metoder utan förklaring.
- Spara resultat över tid och redovisa förbättringar eller försämringar bara när jämförelsen är giltig.
- Visa konkreta hinder och resultat, inte ett obestyrkt totalbetyg eller påstående om att lagkraven uppfylls.
- Granska endast offentliga sidor och vanliga läsflöden. Skicka inte formulär eller riktiga ärenden och kör inga belastnings- eller intrångstester.
- Märk resultaten **Vår granskning** och skilj dem från myndighetsstatistik.
- Låt resultaten vara separata från boendepoängen tills metoden är stabil och täckningen jämförbar. En eventuell poängändring kräver ett dokumenterat metodbeslut.
- Vid implementation ska relevanta resultat även beskrivas i fokusvyn och omfattas av dess språk- och källregler.

### Ytterligare data att utreda

| Område | Uppgifter och möjlig användning | Källa / begränsning |
|---|---|---|
| Bibliotek | Öppettider, besök, lån och aktiviteter i förhållande till folkmängden | KB:s öppna biblioteksstatistik; kontrollera definitioner och täckning. |
| Badvatten | Provresultat och utveckling vid registrerade badplatser | HaV; alla badplatser ingår inte. |
| Luftkvalitet | Partiklar och andra luftföroreningar över tid | Naturvårdsverket/SMHI; en station representerar inte automatiskt hela kommunen. |
| Bilar och drivmedel | Fordonsbestånd och fördelning mellan drivmedel | Trafikanalys; kontrollera geografisk nivå och historik. |
| Byggnaders energi | Energiklass och deklarerad energiprestanda | Boverket; gratis API beskrivs som riktat till företag och kräver avtal. Åtkomst och användningsvillkor behöver utredas. |

### Föreslagen första etapp

Webbtillgänglighet, mobilvänlighet, hitta information och biblioteksstatistik. Börja med ett litet kommunurval för att prova metoden innan alla kommuner jämförs.

### Källor till idén

- Digg, förenklad övervakning och begränsningar i automatisk granskning: https://www.digg.se/analys-och-uppfoljning/lagen-om-tillganglighet-till-digital-offentlig-service-dos-lagen/forenklad-overvakning
- Diggs webbriktlinjer: https://www.digg.se/webbriktlinjer/
- KB:s biblioteksstatistik: https://bibstat.kb.se/
- HaV:s API för badplatser och badvatten: https://www.havochvatten.se/data-kartor-och-rapporter/data-och-statistik/data-och-apier/api-badplatser-och-badvatten.html
- Naturvårdsverkets luftkvalitetsdata: https://www.naturvardsverket.se/amnesomraden/luft/statistik--utslapp-och-halter/luftkvaliteten-i-realtid-och-preliminar-statistik/webbtjanster-luftkvalitetsdata/
- Trafikanalys, fordon: https://www.trafa.se/vagtrafik/fordon/
- Boverkets API för energideklarationer: https://www.boverket.se/sv/om-boverket/oppna-data/publikt-api-for-energideklarationer/

Källor granskade i samband med förslaget. Kontrollera aktuell åtkomst, licens och definition före implementation.

## Jämför kommunernas ekonomi, skola, omsorg och vård

**Sparad:** 26 oktober 2026  
**Status:** Idéer att utreda; komplettera befintliga mått utan att dubblera dem.

### Föreslagna jämförelser

| Område | Mått att undersöka | Huvudkällor |
|---|---|---|
| Kommunens ekonomi | Ekonomiskt resultat, skulder, investeringar och verksamheternas kostnader; relevanta belopp per invånare | SCB:s räkenskapssammandrag och Kolada |
| Grundskola och gymnasium | Betyg, gymnasiebehörighet, lärarbehörighet, elever per lärare och kostnad per elev | Skolverket och Kolada |
| Förskola | Barngrupper, bemanning, personalens utbildning och kostnader | Skolverket och Kolada |
| Äldreomsorg | Upplevd trygghet, bemötande, nöjdhet och verksamheternas arbetssätt | Socialstyrelsen och Kolada |
| Kommunal hälso- och sjukvård | Samverkan, patientsäkerhetsarbete och tillgängliga registerbaserade mått | Socialstyrelsens öppna jämförelser |
| Regional sjukvård, separat redovisning | Väntetider till specialistbesök och operationer där jämförbar statistik finns | Socialstyrelsen; redovisa faktisk geografisk nivå |

### Presentation att utforska

Visa **kostnad, resultat och invånarnas upplevelse sida vid sida**, där jämförbara uppgifter finns:

- Skolan: kostnad per elev tillsammans med skolresultat och lärarbehörighet.
- Äldreomsorgen: kostnad tillsammans med trygghet, bemötande och nöjdhet.
- Kommunens ekonomi: ekonomiskt resultat tillsammans med skulder och investeringar.
- Vården: kommunala vårdmått separat från regionens väntetider.
- Visa både utveckling över tid och jämförelse med Sverige samt liknande kommuner. Dokumentera hur gruppen av liknande kommuner väljs; använd områdesanpassade jämförelsegrupper när sådana finns.

### Regler för jämförbarhet

- Kontrollera definition, år, population, huvudman, geografisk nivå och täckning för varje mått före införande.
- Skilj elever som bor i kommunen från elever som går i skolor där, och kommunala skolor från samtliga huvudmän.
- Skilj kommunens ekonomi från kommunkoncernens när bolag ingår.
- Invånarnas ålder, behov och kommunens bebyggelse kan påverka kostnaderna. Hög kostnad bevisar inte hög kvalitet; låg kostnad bevisar inte effektivitet.
- Regionens väntetid får aldrig visas som kommunens eget resultat. Uppgifter på region-, sjukhus- eller mottagningsnivå ska märkas med sin verkliga nivå.
- Redovisa bortfall, sekretess, metodbyten, osäkerhet och brutna tidsserier. Saknat värde är inte noll.
- Behåll ursprungliga observationsår, inklusive jämförbara tidigare år. Utred hämtning och självhosting enligt projektets vanliga regler.
- Nya mått ska vid implementation ingå i fokusvyns lättlästa text och exakta datafält samt i Enkelt sagt där de passar.
- Bedöm eventuell användning i boendepoängen genom ett dokumenterat metodbeslut; lägg inte automatiskt till kostnader eller överlappande index.

### Källor

- Kolada: https://www.kolada.se/
- SCB, räkenskapssammandrag: https://www.scb.se/hitta-statistik/statistik-efter-amne/offentlig-ekonomi/finanser-for-den-kommunala-sektorn/rakenskapssammandrag-for-kommuner-och-regioner/
- Skolverkets statistikdatabas: https://www.skolverket.se/statistik-och-utvarderingar/statistik-om-forskola-och-skola/sok-statistik-om-forskola-skola-och-vuxenutbildning
- Socialstyrelsen, äldreomsorg: https://www.socialstyrelsen.se/statistik-och-data/oppna-jamforelser/socialtjanst/aldreomsorg/
- Socialstyrelsen, kommunal hälso- och sjukvård: https://www.socialstyrelsen.se/statistik-och-data/oppna-jamforelser/kommunal-halso-och-sjukvard/
- Socialstyrelsen, vårdens väntetider: https://www.socialstyrelsen.se/statistik-och-data/statistik/alla-statistikamnen/lagesbild-och-statistik-tillganglighet-vantetider-och-vardgaranti-i-halso-och-sjukvard/


## Kommunernas egen inrapportering och invånarnas upplevelser

**Sparad:** 26 oktober 2026  
**Status:** Idéer att utreda, inte beslut om implementation.

### Prioriterade källor

| Källa | Vad vi kan undersöka | Viktigt vid jämförelser |
|---|---|---|
| Kommunens Kvalitet i Korthet, KKiK / RKA / Kolada | Kommunernas egna insamlade verksamhetsmått, bland annat bygglov, väntetider till särskilt boende och individ- och familjeomsorg | Följ respektive formulärs urval, definition och mätperiod. Alla kommuner och år behöver inte ha värden. |
| Boverkets bostadsmarknadsenkät | Kommunens bedömning av bostadsbrist, balans eller överskott; situationen för unga, studenter, äldre, nyanlända och personer med funktionsnedsättning; bostadsbyggande och service till bostadssökande | Kommunens bedömning ska skiljas från uppmätta bostadsantal och faktiska kötider. Frågor kan ha ändrats mellan år. |
| SCB:s medborgarundersökning | Invånarnas upplevelser av skola, omsorg, boendemiljö, trygghet, inflytande och förtroende | Detta är invånarsvar, inte kommunens egen kvalitetsbedömning. Bara deltagande kommuner kan jämföras; redovisa svarsbortfall och osäkerhet. |
| SKR:s servicemätning Insikt | Erfarenheter av kommunens myndighetsservice efter avslutade ärenden, främst bland företag; även upphandling där uppgifter finns | Deltagandet varierar. Resultaten gäller dem som haft ärenden och ska inte beskrivas som alla invånares åsikter eller en fullständig företagsklimatbedömning. Kontrollera åtkomst och återanvändningsvillkor. |
| IVO:s statistik och kommunernas uppföljning | Beslut om stöd och omsorg som ännu inte har genomförts, uppdelat efter verksamhet där aggregerad statistik finns | Kontrollera att kommunnivå går att hämta innan införande. Skilj beslut, ärenden, personer, periodens nya ärenden och återrapportering. Summera inte överlappande kategorier. Ingen individinformation ska ingå. |
| SKR:s sjukfrånvaroredovisning | Sjukfrånvaro bland kommunens anställda och utveckling över tid | Arbetsgivarens personalmått, inte sjukfrånvaro bland kommunens alla invånare och inte Försäkringskassans sjukpenningtal. |

### Möjlig presentation

- **Så beskriver kommunen sin service:** egenrapporterade verksamhetsmått och bedömningar.
- **Så upplever invånarna och företagen den:** enkätresultat med rätt målgrupp.
- **Så ser de uppmätta resultaten ut:** registerdata och verksamhetsutfall.
- Visa dessa sida vid sida och håll skillnaden tydlig i lätt svenska.
- Exempel: väntan till äldreboende tillsammans med äldres upplevelser och omsorgens kostnader; bostadsmarknadsbedömning tillsammans med färdigbyggda bostäder och befolkningsutveckling.
- Undersök årsredovisningar, kvalitetsrapporter och kommunala öppna dataportaler för kompletteringar. Lokala mått får jämföras först när definitioner och perioder matchar.
- Spara historik och faktiska mätperioder. Kontrollera vad som redan finns i projektet före nya importer.
- Vid implementation ska nya uppgifter omfattas av fokusvyns text, datafält och övriga befintliga regler. Nya mått ändrar inte boendepoängen utan metodbeslut.

### Källor att återvända till

- KKiK, nyckeltal: https://rka.nu/radetforframjandeavkommunalaanalyser/koladastod/nyckeltalforkkik.44786.html
- KKiK, insamlingsformulär: https://rka.nu/radetforframjandeavkommunalaanalyser/koladastod/publicerastatistikikolada/formularinrapporteringforkkik.44880.html
- Boverkets öppna bostadsmarknadsenkät: https://www.boverket.se/sv/om-boverket/oppna-data/bostadsmarknadsenkaten/
- SCB:s medborgarundersökning: https://www.scb.se/vara-tjanster/bestall-data-och-statistik/regionala-statistikprodukter/medborgarundersokningen/
- SKR, Insikt: https://skr.se/samhalleochnaringsliv/naringslivochforetagsklimat/servicematningeninsikt.7680.html
- IVO, statistik: https://www.ivo.se/statistik/ej-verkstallda-beslut/
- SKR, sjukfrånvaroredovisning: https://skr.se/arbetsgivarrollen/analysstatistikochuppfoljning/sjukfranvaroredovisningen.8105.html
