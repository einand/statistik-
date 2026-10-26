# Projektregler – Sveriges statistikwebbplats

Läs även BESLUT.md. Där finns de samlade överenskommelserna från sessionen om sidstruktur, siffror, språk, trender, källor, kartor, sökning, mobilanvändning, hosting och datatyper. Reglerna gäller vid alla framtida ändringar.

## Obligatoriskt när statistik läggs till eller ändras

Varje ny statistikuppgift, nytt mått, nytt geografiskt lager eller ny statistikutgåva ska även omfattas av löptexten på `/focus/`. En statistikändring är inte färdig förrän både löptexten och de detaljerade datafälten har uppdaterats och kontrollerats.

### Fokussidans löptext

- Skriv för personer som inte vill eller kan bearbeta stora mängder siffror.
- Använd inte siffror, procentsatser, årtal eller korrelationskoefficienter i den synliga löptexten. Beskriv nivåer med begripliga ord, exempelvis ”lite högre”, ”mycket lägre” eller ”ungefär samma nivå”.
- Beskriv utvecklingen med ord, exempelvis ”ökat lite”, ”minskat tydligt” eller ”varit ungefär oförändrad”. Jämför faktiska, tillgängliga observationer fram till valt år. Hitta inte på trender för mått med bara en observation.
- Använd tydliga och rimliga jämförelser. Inkomst och andelar kan jämföras med motsvarande riksuppgift; råa områdesantal ska inte jämföras med rikets total som om det vore ett normalvärde för en kommun. Redovisa vilken jämförelse som används.
- Bedöm inte automatiskt en ökning som en förbättring eller en minskning som en försämring. Beakta måttets innebörd, sekretesskydd, metodändringar, inflation och förändrade områdesgränser där det är relevant.
- Samtliga tillgängliga mått ska täckas. Skriv sammanhållna stycken under tydliga ämnesrubriker. Gruppera mått med samma jämförelse eller trend i gemensamma meningar. Undvik upprepade standardmeningar för varje mått och dubblerade inledningar. Alla teman ska vara läsbara direkt. Nya mått ska få begripliga benämningar och tillhöra ett relevant tema.
- Skriv uttryckligen när jämförbara uppgifter saknas. Ersätt inte saknad lokal statistik med kommunens eller länets värden utan att tydligt skilja nivåerna åt.
- Beskriv samband utan att påstå att korrelation bevisar orsak. Möjliga förklaringar ska ha verifierade källänkar och skiljas från bevisade lokala orsaker.
- Polisens klassningar gäller de officiellt avgränsade områdena och rätt utgåva, inte hela kommunen, länet eller invånarna. Områdesnamn och kategorier ska omfattas av texten där geografisk koppling kan göras säkert.
- Uppgifter från valda geografiska kartobjekt ska också kunna beskrivas i fokusvyn. Gör inte obestyrkta påståenden om att objektet tillhör en administrativ region bara för att det syns i kartans utsnitt.

### Detaljerade data under löptexten

- Visa exakta värden, enheter, faktiska mätår, källa och relevanta definitionsbegränsningar.
- Visa både vald plats och motsvarande riksuppgift när sådana finns. Visa saknade uppgifter som saknade.
- Håll numeriska detaljer i datafälten, inte i den lättlästa löptexten.

### Kontroll innan statistikändringen är färdig

1. Kontrollera att det nya måttet finns i fokusvyns datafält och i rätt löptexttema.
2. Kontrollera nivåjämförelsen och trendbeskrivningen mot underliggande observerade värden.
3. Byt plats och år och kontrollera att både text och värden uppdateras.
4. Kontrollera fall med saknad statistik och otillräcklig historik.
5. Kontrollera att den synliga löptexten är sifferfri och att källor och exakta siffror finns där de ska.

## Sidornas roller

- `/`: samtliga kartor, inklusive geografiska objekt, med möjlighet att visa och dölja kartor.
- `/focus/`: en karta, platssökning, lättläst sammanfattning samt alla relevanta datafält för vald plats. Värden ligger bredvid kartan på större skärmar och under den på mobil.
- `/lan/`: länväljare och tabell, inga kartor.
- Den tidigare separata geodatasidan är ersatt av kartor på startsidan och i fokusvyn.

### Fast skrivstil för samtliga kommuner

Det godkända Härryda-exemplets ämnesindelade, sammanhållna stil gäller samtliga kommuner. Väv ihop nivå, jämförelse och utveckling inom respektive tema. Behåll även uppgifter som avviker från den övriga bilden; förenkla språket utan att förenkla bort fakta. Gruppera bara mått som har förenliga jämförelser och perioder. Nya mått ska vävas in i rätt stycke och omfattas av samma regler, inte läggas till som en separat upprepad standardmening. Alla mått ska antingen beskrivas eller namnges som otillgängliga för valt område och period.

- Ange en gång i början av fokusvyns löptext att jämförelserna gäller riket om inget annat anges. Upprepa inte ”än i riket” eller ”som i riket” vid varje mått. Andra jämförelsegrunder, exempelvis genomsnittet för kommunerna, ska fortfarande anges där de används.

## Fast språkregel: mycket lätt svenska i fokusvyn

Löptexten ska skrivas på mycket lätt svenska. Använd korta meningar och vanliga, konkreta ord. Förklara nödvändiga fackord direkt, eller använd ett enklare ord. Undvik krångliga formler, matematiska uttryck och dubbla negationer. Använd raka påståenden som gör innebörden lätt att förstå. Exakta siffror, enheter, formler och tekniska definitioner hör hemma i datafälten och källnoterna under löptexten. Behåll alla relevanta mått, jämförelser, verkliga förändringar och begränsningar genom att förklara dem enkelt och gruppera sådant som hör ihop. Denna regel gäller hela den befintliga löptexten och varje nytt statistiktillägg.

## Boendepoäng och /score

- `/score/` är en kommunlista med fyra huvudkolumner: Plats, Kommun, Score och Kommentar till varför. Behåll sökning, sortering och länkar till rätt kommun i fokusvyn.
- Poäng bygger på uttalade val, inte en officiell eller objektiv bedömning av var alla människor bör bo. Visa metoden och vikterna. Besökaren får ändra vikterna.
- Kör `python data/prepare-public.py` inför varje publicering. Den bygger om poängunderlaget från sidans aktuella kommunstatistik och sparar nya historiska standardresultat när underlaget/metoden ändrats.
- Varje statistikändring ska även bedömas för score-modellen. Nya observationer i modellens mått räknas om automatiskt. Nya slags mått förs in genom en dokumenterad metodändring; lägg inte automatiskt in varje ny tabell, råantal eller dubblerat index.
- Behåll metodversion, kontrollsumma, äldre standardresultat och aktuella källor/mätperioder. Ändra aldrig en sparad historisk utgåva i efterhand.
- Poäng får bara räknas från kommunvärden. Saknad kommunstatistik får inte ersättas med län/riket. Inga framtida värden eller modelluppskattningar får smygas in som observationer.
- Minst åttio procent av viktat underlag och minst hälften av måtten i varje aktivt tema krävs för placering. Likvärdiga poäng med en decimal ger delad placering. En sökning ändrar inte den nationella placeringen.
- Fokusvyn ska visa standardpoängens lättlästa kommentar samt exakta poäng, placering, täckning, valt år och metod i ett separat datafält. De vanliga reglerna om mycket lätt svenska och sifferfri löptext gäller kommentarerna.

- Vikterna på `/score/` väljs med pekvänliga sliders med exakt tio nivåer, från Oviktigt till Viktigt. Den första nivån tar bort temat ur poängen. Poäng och kommentarer uppdateras direkt när reglagen flyttas. Återställning ska behålla standardvikterna och deras inbördes förhållanden.

- Visa ett litet årsdiagram under kommunpoängen på /score/ och i fokusvyn. Poängsidans diagram följer valda vikter, fokusvyn använder standardvikter. Visa endast år med beräkningsbar poäng i diagrammet och dess årslista. Årsväljaren på /score/ ska bara innehålla år där minst en kommun har beräkningsbar poäng med valda vikter. Behåll valt år när det finns kvar, välj annars senaste giltiga året. Ge en åtkomlig lista med exakta årsvärden. Använd samma metod och vikter genom hela serien. En ändrad relativ poäng är inte säkert en förbättring eller försämring.

## /boring/ – Enkelt sagt

En egen mobilanpassad väg in i statistiken, med mycket lätt svenska, enkla jämförelsebilder, en snabb överblick och en gissningsfråga. Alla befintliga skalära kommunmått ska vara sökbara och grupperade i ämnen. Exakta värden och källor öppnas per kort. Huvudtexten använder vanliga ord. Jämför bara samma mått och mätår, och bara jämförbara andelar eller värden per enhet med Sverige. Jämför inte kommunala råantal med rikets total. Visa saknade lokala värden som saknade; använd aldrig riksdata som lokal ersättning. Saknad statistik är inte noll. Mer eller mindre betyder inte automatiskt bättre eller sämre. Ingen humor på invånares eller utsatta gruppers bekostnad. Bygg underlaget med data/build-boring.py vid varje publicering; skriptet körs från prepare-public.py. Behåll länkar till fullständiga kartor, fokus, poäng och källtabeller.

## Gemensam design från /boring/

Hela projektet använder stilen från Enkelt sagt: varm ljus bakgrund, mörk grön text, stora tydliga rubriker, mjuka gröna/lila/aprikosa ytor, luftiga kort och stora tryckytor. Gemensamt tema finns i dist/assets/site-theme.css. Alla huvudsidors navigation har samma struktur och aktiva markering. Även lokala kartkomponenter och statistikfördjupningar ska följa temat. Behåll sidornas roller, statistik, kartfunktioner, sökning, filter, tidsreglage och sticky-regler. Ändra inte kartornas dataskalor för att byta visuell stil.

## GitHub och Codex Cloud

Utvecklingsrepo: https://github.com/einand/statistik-.git. Repot är redan kopplat till Codex Cloud. Spara framtida kod, regler och idéer där. Läs och synkronisera aktuellt GitHub-läge innan ändringar, bevara andra ändringar och använd arbetsgren/PR när lämpligt. Sites-repot används fortsatt för publicering på samma adress; en GitHub-commit publicerar inte automatiskt webbplatsen. Kontrollera att GitHub och Sites använder samma källäge inför publicering. Ändra inte .openai/hosting.json till ett nytt projekt. Skriv aldrig GitHub- eller Sites-credentials i filer.

## Aktiv hosting: GitHub Pages

Från 26 oktober 2026 är https://einand.github.io/statistik-/ den aktiva adressen. Den tidigare Sites-adressen ska endast omdirigera dit. Fortsatt utveckling och publicering av själva appen sker för GitHub Pages. Återpublicera inte appen på Sites; där finns ett separat litet omdirigeringspaket. Beakta /statistik-/ som basväg för resurser, länkar och dataanrop. Tidigare instruktioner om att publicera den aktiva statistikappen via Sites är ersatta av detta beslut.
