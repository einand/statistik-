# Beslut och krav från arbetssessionen

Sammanställt den 24 oktober 2026. Dessa beslut ska bevaras vid fortsatta ändringar. Senare uttryckliga användarinstruktioner har företräde. Se även AGENTS.md för obligatoriska arbetsregler.

## Grundprinciper

- Vidareutveckla den befintliga webbplatsen och behåll dess publika adress: https://sveriges-lansbefolkning-1749-2025.einand.chatgpt.site/.
- Behåll befintlig data och fungerande funktioner vid tillägg. Ta inte bort kartor för att minska visuellt kludd.
- Webbplatsen ska vara logisk och lätt att använda, med mobil som utgångspunkt och fungerande användning på iPad och dator.
- Kartförändringar är ett separat, ofärdigt projekt. Länkar och menyval till det ska vara borttagna tills användaren vill visa det igen.
- Förslag på nya datakällor innebär inte automatiskt implementation. Implementera när användaren begär det.

## Sidstruktur och meny

### Startsidan `/`

- Alla statistikkartor ska finnas kvar här och visas parallellt.
- Detaljerade geodatalager ska också finnas som kartor bland de andra kartorna, inte kräva en separat geodatasida.
- Behåll platssökning, årsväljare och kartfilter.
- Visa och dölj kartor ska fungera, både för ämnesgrupper och enskilda kartor. ”Visa alla” och ”Dölj alla” ska även omfatta geografiska objekt.
- Urvalet av kartor ska sparas i webbläsaren, enligt den befintliga funktionen.
- Länväljaren med texten ”Visa län” ska inte finnas på startsidan.

### Länssidan `/lan/`

- Visa en länväljare och en tabell. Inga kartor.
- Byte i dropdownen ska uppdatera tabellen till det valda länets uppgifter.
- Länväljaren ska vara lätt att nå och vara sticky när man skrollar förbi dess vanliga plats.
- Tabellen ska visa senaste tillgängliga värde per mått och vilket faktiskt år det avser; olika mått kan ha olika år.

### Fokussidan `/focus/`

- Visa en enda karta och samma typ av platssökning som startsidan.
- Användaren ska kunna koncentrera sig på en plats och se alla relevanta statistikfält för den.
- På större skärmar ligger data och sammanfattning bredvid kartan. På mobil ligger de under kartan.
- Man ska kunna välja vilket statistikmått eller geografiskt lager den enda kartan visar.
- Geodatalagren ska vara tillgängliga även här. Valda kartobjekts uppgifter ska kunna visas.
- Ovanför datafälten ska finnas en begriplig sammanfattning i löptext.
- Varje statistikändring ska samtidigt uppdatera fokussidans löptext och numeriska datafält. Detta är ett obligatoriskt färdigställandekrav, inte en valfri förbättring.

### Tidigare geodatasida `/geodata/`

- Den separata användarsidan är borttagen och dess kartor flyttade till startsidan och fokusvyn.
- Gamla länkar kan omdirigeras till kartorna på startsidan.
- Interna kartkomponenter och statiska visningsfiler kan finnas som implementationsdetaljer, utan ett separat menyval för geodatasidan.

### Meny

- Mobilanpassad och tydlig navigation mellan kartor, länstabell och platsfokus.
- Behåll lättåtkomliga vägar till platssökning, årtal och kartfilter.
- Visa inte menyval till det ofärdiga kartförändringsprojektet.

## Siffror, språk och läsbarhet i fokusvyn

### Löptextens målgrupp

- Skriv för personer som inte vill eller kan bearbeta stora mängder siffror.
- Löptexten ska vara sifferfri: inga numeriska värden, procentsatser, årtal, intervall eller korrelationskoefficienter i den synliga texten.
- Använd ord såsom ”lite högre”, ”mycket lägre”, ”ungefär samma nivå”, ”ökat lite” och ”minskat tydligt”.
- Exempel på önskat tonläge: ”I Härryda är medianinkomsten mycket högre än i riket.” Beskriv vad måttet faktiskt mäter, inte generell förmögenhet eller varje invånares situation.
- Använd det godkända Härryda-exemplets sammanhållna, ämnesindelade stil för alla kommuner. Alla teman visas direkt. Gruppera liknande jämförelser och trender i gemensamma meningar; undvik en upprepad standardmening per mått.
- Återgå inte till att rada upp exakta siffror i löptexten. Intresserade ska kunna skrolla till detaljerna.

### Detaljerna under texten

- Här ska alla exakta värden, enheter, faktiska mätår, källor och förklaringar finnas.
- Visa vald plats och motsvarande riksuppgift där dessa finns.
- Valår, parti, statistisk period och geografisk nivå ska framgå där det är relevant.
- Blanda inte medianinkomst, kommunanställdas lön, hushållsinkomst och generell förmögenhet som om de vore samma sak.
- Löptext och datafält ska bygga på samma mått, plats och period; om olika mätår används ska det vara tydligt i detaljerna.

## Jämförelser, utveckling och korrelation

- Löptexten ska beskriva både nivå och utveckling, där jämförbar historik finns.
- Jämför med föregående tillgängliga observerade mätår, inte ett påhittat värde för föregående kalenderår.
- Vid tillräcklig historik kan flera mätningar beskrivas med ord. Ett par intervall är inte automatiskt en långsiktig trend.
- Skriv inte att något blivit bättre eller sämre bara för att ett tal ökat eller minskat. Bedöm måttets innebörd och begränsningar.
- Inkomstökning i löpande priser innebär inte i sig ökad köpkraft.
- Minskade anmälda brott bevisar inte minskad faktisk brottslighet; anmälningsbenägenhet och polisens arbete kan påverka.
- Sjukpenningtal mäter ersatta dagar per försäkrad, inte antalet sjukskrivna eller all ohälsa.
- Grönområdesyta mäter inte antalet träd, tillgänglighet, kvalitet eller användning av grönområden.
- För en enda observation ska ingen trend hittas på.
- Håll olika definitioner, geografiska nivåer och områdesgränser isär. Metod- och gränsändringar kan göra serier olämpliga att jämföra direkt.
- Använd rimlig referens: rikets motsvarande andel eller inkomstmått där det är lämpligt. Kommunala råantal ska inte jämföras med rikets total som om totalen vore ett kommunalt normalvärde.
- Korrelation ska beräknas från jämförbara observerade värden under samma period. Prognoser ska inte behandlas som observationer.
- Beskriv korrelation med begripliga ord i löptexten; numeriska detaljer hör till datan.
- Korrelation innebär inte orsak. Skriv inte att exempelvis lite grönyta orsakar en viss kommuns sjukfrånvaro utifrån samvariation i kartorna.

## Förklaringar och källor

- Försök hitta verifierbara källor till möjliga bakomliggande faktorer.
- Använd officiella data och primära källor för mått och definitioner. Länka till källorna.
- Skilj generella forskningsresultat från belagda orsaker i den valda kommunen.
- Förklaringar från exempelvis Folkhälsomyndigheten och Försäkringskassan får ge sammanhang men ska inte framställas som en genomförd lokal orsaksanalys.
- Ange saknade uppgifter som saknade; konstruera inte statistik eller tidsserier för att fylla grå kartor.
- Ersätt inte saknad statistik för RegSO, tätort eller annan mindre yta med kommunvärden utan tydlig skillnad mellan nivåerna.

## Platssökning och kartor

- Behåll sökfunktionen på startsidan och i fokusvyn. Den ska inte försvinna när layouten ändras.
- Sök bland de platser som faktiskt finns i datan: riket, län, kommuner, tätorter och statistiska områden enligt det befintliga indexet.
- Val av sökträff ska zooma kartan till platsen och uppdatera platsens värden.
- Var tydlig med vilken geografisk nivå och områdesutgåva som visas.
- En kartas utsnitt är inte bevis på att alla synliga objekt tillhör den valda kommunen. Gör ingen obestyrkt geografisk tilldelning.
- Startsidan får ha flera parallella kartor; fokusvyn ska visa en karta åt gången.

## Årsslider, sticky-läge och pekskärmar

- Huvudtidslinjen ska kunna gå till och med 2026.
- Valår ska hamna på rätt kalenderår i tidslinjen. Valdata är diskreta valår, inte en årlig serie som ska fyllas ut med påhittade observationer.
- Visa faktisk tillgänglig statistikutgåva när mått har glesare uppdateringar eller senaste året saknas.
- Geodatautgåvor kopplas till närmast föregående tillgängliga utgåva. Visa inte en senare utgåva som historisk sanning före dess första år.
- Årsreglaget ska vara lätt att komma åt vid skrollning.
- I årssliderns sticky-läge ska endast slider och aktuellt år visas, inte övriga instruktioner eller text.
- Reglagen ska vara lätta att träffa på mobil och iPad, med stor tryckyta och tydligt handtag.
- Länsidans sticky-dropdown hör bara till länsidan.

## Mobil layout och bredd

- Mobil först. Kontrollera även iPad och större skärmar.
- Ingen horisontell sidskroll. Fält, tabeller och kartor ska rymmas på tillgänglig bredd och vid behov staplas.
- Menyval, sliders, dropdowns och knappar ska vara lätta att trycka på.
- Layoutändringar får inte förstöra kartornas interaktion, årsslidern, sökningen eller visa/dölj-funktionen.

## Datahosting och geografiska utgåvor

- Statistik och geodata ska vara nedladdade och hostade på webbplatsen. Undvik beroende av externa datatjänster vid besökarnas sidvisning.
- Källhänvisningar får länka externt; själva visningsdatan ska ligga lokalt.
- Stora lager får delas upp, komprimeras och laddas vid behov för att hålla mobilupplevelsen rimlig.
- Bevara källhänvisning, definition, faktisk utgåva och kända begränsningar.
- Kartutgåvor är statistiska ögonblicksbilder. Första förekomst i ett register eller en utgåva är inte ett bevis på när en ort, gata, byggnad eller verksamhet uppstod.
- Flyg- och satellitbildsidén från Lantmäteriet avbröts. Återinför inte den som ett överenskommet krav.

## Införda datatyper som ska bevaras

- Befolkning och befolkningsförändring på de nivåer och år där data finns.
- Födda, döda, flyttningar, ålder, hushåll, utbildning, sysselsättning, inkomst, bostäder, brott, trygghet, hälsa och valdeltagande enligt tillgänglig källdata.
- Valmyndighetens valdata, med rätt valår och valtyp samt parti där det är relevant, inklusive tillgängliga uppgifter för 2026.
- Digital infrastruktur: bredband och mobiltäckning enligt införda källor och utgåvor.
- SCB:s tätorter och historiska tätortsutgåvor.
- Handelsområden: antal och yta i införda utgåvor.
- Fritidshusområden: antal och yta i införda utgåvor. Detta är inte all fritidshusbebyggelse eller faktisk sommarbefolkning. Hitta inte på antal hus om fältet saknas i den använda källan.
- Småorter, grönområden i tätorter, verksamhetsområden, äldre arbetsplatsområden, DeSO, RegSO och befolkning i kilometerrutor.
- Arbetsplatsområden och verksamhetsområden ska vara separata serier eftersom definitionerna skiljer sig.
- Grönområdesutgåvors ändrade täckning och metod ska inte tolkas som säker lokal förändring av all grönyta.
- Befolkningsrutornas sekretesskydd kan göra att delsummeringar avviker från totalerna.

## Polisens utsatta områden

- Använd Polisens officiella lista, områdesgränser och kategorier med rätt utgåva.
- Uppgifterna ska finnas i startsidans kartor och i relevanta delar av länstabellen och fokusvyn, inklusive löptexten.
- Namnge klassificerade områden och deras kategorier där kopplingen är säker.
- Klassningen gäller avgränsade områden, inte hela kommunen, länet eller invånarna.
- Antal klassificerade områden är inte ett mått på brottsfrekvens eller individuell brottsrisk.
- Noll områden i en lista är inte en allmän bedömning att en kommun är trygg eller fri från brott.
- Skriv inte tillbaka en ny polislista till äldre år och hitta inte på en trend från en enda inläst lista.

## Färdigställandekrav vid framtida ändringar

- Kontrollera att varje nytt mått omfattas av både löptext, rätt tema och detaljerade datafält i fokusvyn.
- Kontrollera värden, jämförelser och trender mot källan.
- Prova byte av plats, år och kartmått samt fall med saknad data.
- Kontrollera sifferfri löptext och att exakta siffror finns under den.
- Bevara startsidans kartor och länsidans tabellroll.
- Fortsätt publicera webbplatsändringar på samma befintliga adress och med bibehållen publik åtkomst. Rent dokumenterade projektregler ändrar inte i sig webbplatsens användargränssnitt.

## Beständig skrivregel för nya statistikuppgifter

Samtliga kommuner ska följa samma lättlästa, ämnesindelade stil som det godkända Härryda-exemplet. Varje ny statistikuppgift ska vävas in i sitt relevanta stycke tillsammans med befintliga jämförelser och utveckling. Alla tillgängliga mått ska täckas, även sådana som ger en annan bild än övriga uppgifter. Saknade mått namnges utan att presenteras som noll. Gruppering får inte blanda olika jämförelsegrunder eller dölja olika mätperioder. Löptexten ska vara sifferfri, medan exakta värden, mätår, definitioner och källor finns nedanför. Kontrollera detta vid varje framtida dataändring.

- Ange en gång i början av fokusvyns löptext att jämförelserna gäller riket om inget annat anges. Upprepa inte ”än i riket” eller ”som i riket” vid varje mått. Andra jämförelsegrunder, exempelvis genomsnittet för kommunerna, ska fortfarande anges där de används.

## Tillagda källor: tolv beställda datamängder

- Daglig tobaksrökning: Folkhälsomyndighetens flerårsmedelvärden på riks- och länsnivå. Lägg perioden vid dess slutår och visa hela mätperioden i detaljer. Kommunvärden saknas; länskontext måste märkas separat. Överlapp, urval och definitionsändringar gör att ingen säker trend påstås.
- Måltidspersonalens utbildning: U50105 redovisar kategorikoder för andelsintervall, inte exakta procent. Visa intervallet och beräkna inga aritmetiska riks-/länsmedel av koderna. Undersökningsår är vart tredje år.
- Politisk representation: håll kommunpolitiker och regionpolitiker isär. Mellanår som återpublicerar en tidigare undersökning får inte framstå som nya mätningar. Inkomstmåtten är inte arvoden eller löner.
- Fysiska elflöden: lokalt hostade observationer från Svenska kraftnät. Elområden är inte administrativa län eller kommuner. Kartan är ett tydligt märkt schema, inte områdesgränser. Jämför riktningar vid samma mättillfälle. Saknad post är inte säkert noll. MW är effekt, inte energiförbrukning. Pågående år är ofullständigt.
- AI-ackrediteringar: Swedacs aktuella registeruttag är en ögonblicksbild och mäter inte lokal AI-användning. Ett verifierat tomt registerutfall får inte beskrivas som att AI-företag eller AI-verksamhet saknas. Inget historiskt innehåll eller geografisk fördelning ska konstrueras. Ange källa och att sammanställningen är fristående från Swedac.
- Även dessa källor ska omfattas av fokusvyns sifferfria, ämnesgrupperade löptext vid framtida dataändringar.

## Kvalitetsindex kommunal gymnasieskola

U17401 är ett relativt normaliserat index för kommunala gymnasieskolor. Det är inte en procentandel eller ett mått på alla kommuninvånares gymnasieutbildning. Skalan och klippta yttervärden ska förklaras. Riks- och länsvärden ska inte konstrueras. Om egen kommunjämförelse används ska den uttryckligen avse kommunerna med uppgift. En ändrad indexpoäng får inte automatiskt beskrivas som förbättrad eller försämrad skolkvalitet. Fokusvyn ska omfatta måttet i utbildningstemat och ange saknade uppgifter som saknade.

## Skola, uppväxt och kommunal ekonomi – utökning 25 oktober 2026

- Håll skolornas kvalitetsindex, resursindex och effektivitetsindex isär. Högt resursindex betyder lägre relativa kostnader; det är inte mer resurser eller bevisat hög kvalitet. Relativa index ska inte få en automatisk förbättrings-/försämringstrend.
- Faktiska kostnader, intäkter, modellberäknad referenskostnad, behovsnivå och produktionsförutsättningar har olika innebörd. Skilj kronor per invånare från kronor per elev och hemkommun från skolkommun. Ange löpande priser.
- Balanstalet för utrikes födda bland skolpersonal jämför med befolkningens andel, med ett som balanspunkt. Detta är inte ett procenttal eller en kvalitetsbedömning av personalen.
- CSN:s indragna studiehjälp avser stöd som dragits in på grund av ogiltig frånvaro. Det är inte all frånvaro eller alla gymnasieelever. Följ folkbokföringen och ange faktisk läsårsperiod; placera den vid slutåret.
- FHM:s nationella gruppuppdelningar efter ekonomi, ålder, födelseland, utbildning och socioekonomisk områdestyp är inte kommunvärden. Regionala och nationella urval kan ha olika vikter. Visa konfidensintervall där de finns och förväxla inte registeruppgifter med urvalsundersökningar.
- Fullständiga flerdimensionella tabeller finns i en lokalt hostad fördjupning på startsidan och fokusvyn; länssidan länkar dit men ska fortsätta vara enbart tabell. Alla tabelluppdelningar behöver inte få ett påhittat geografiskt kartlager.
- Äldre verksamhetsköp från 1998–2013, kommunala huvudverksamhetsköp från 2011–2025 och nationell utförarstatistik från 2016–2024 ska förbli separata källserier. Definitionen förändrades 2011. Ingen trend över definitionsbrottet ska konstrueras.
- Källtabellen för mobbning efter socioekonomisk områdestyp (525_13902) kunde inte hämtas. Visa detta som källvärden saknas, inte som noll eller som värden hämtade från andra grupper. Uppdatera både fördjupningen och fokusvyns löptext när källan blir tillgänglig.

## Förskola på RegSO-nivå

FHM:s InskForskRegso är en separat lokal fördjupning med alla redovisade kön och år. Delområdesvärden ska inte användas som kommunvärden. Koppla inte tabellens RegSO-koder till kartgeometrier utan verifierad indelningsversion. Fokusvyn förklarar begränsningen och länkar genom den befintliga fördjupningen till exakta värden. Inga kommun- eller riksmedel konstrueras från områdesandelar.

## Fast språkregel: mycket lätt svenska i fokusvyn

Löptexten ska skrivas på mycket lätt svenska. Använd korta meningar och vanliga, konkreta ord. Förklara nödvändiga fackord direkt, eller använd ett enklare ord. Undvik krångliga formler, matematiska uttryck och dubbla negationer. Använd raka påståenden som gör innebörden lätt att förstå. Exakta siffror, enheter, formler och tekniska definitioner hör hemma i datafälten och källnoterna under löptexten. Behåll alla relevanta mått, jämförelser, verkliga förändringar och begränsningar genom att förklara dem enkelt och gruppera sådant som hör ihop. Denna regel gäller hela den befintliga löptexten och varje nytt statistiktillägg.

## Senaste källornas betydelse

- Försäkringskassans sjukpenningtal med olika definitioner ska vara separata serier. Månadens mottagare och sjukfall är inte unika årspersoner. Ange faktisk månad; pågående år är ofullständigt.
- IAF:s ersättningstagare är inte alla arbetslösa. Nationella handläggningstider blir inte kommunvärden.
- Rot/rut ska skilja köpare från utförare och betalningsperiod från godkänd period. Skattereduktion per köpare är inte per invånare. Taxeringshyror för värdeområden är inte faktisk kommunal bostadshyra.
- Skatteverkets median av fastställd skatt är inte inkomst, skattesats eller kommunbudget. Samma synliga grupp kan innehålla flera källrader; bevara dessa separat och konstruera inga kartvärden vid konflikt.
- Ekonomiska index ska jämföras inom rätt geografisk nivå och samma index. Kvinnors och mäns separat normaliserade index får inte subtraheras till ekonomiskt könsgap. Endast observerade indexår visas.
- Enkät om ekonomisk kris beskriver svårigheter med löpande utgifter och flerårsmedel. Kommunal nettokostnad för totalförsvar är inte uppmätt beredskapsförmåga.
- Turistpunkter är ett aktuellt redaktionellt register. Registrerings-/ändringsdatum är inte etableringsdatum. Adressort eller kartutsnitt bevisar inte kommuntillhörighet.
- Grundvattenförekomster är avgränsningar i separata förvaltningscykler. De visar inte dagens vattennivå, vattenbrist eller kemiska status. INSPIRE-representationen ska inte dubbelräknas som nya vattenresurser.

## Boendepoäng – beslutad första metod

- Egen tabellsida `/score/`, tillagd i menyn. Alla kommuner visas, även de med för lite underlag. Fyra huvudkolumner: Plats, Kommun, Score, Kommentar till varför. Underlag och källor kan öppnas per rad.
- Standardsumma av teman: ekonomi/arbete tjugo procent, trygghet tjugo, skola/omsorg tjugo, hälsa femton, boende femton, vardag/uppkoppling tio. Egna vikter tillåts. Den sistnämnda delen omfattar initialt bredband; jämförbara kommunmått för miljö och resor saknas i modellen och ersätts inte med råa grönyteantal eller länsdata.
- Varje mått omvandlas till poäng efter kommunernas inbördes rang, med medelrang vid lika värden. Lägre värden ger högre poäng för otrygghet, låg ekonomisk standard och trångboddhet. Aktiva teman vägs samman. Mått inom ett tema väger lika.
- Ekonomi: sysselsättning, medianinkomst, låg ekonomisk standard. Trygghet: upplevd otrygghet kvällstid. Skola/omsorg: gymnasiebehörighet och äldres trivsel utomhus i särskilt boende. Hälsa: självskattad hälsa och snittet av kvinnors/mäns redovisade medellivslängd som ett jämförelsemått. Boende: trångboddhet och färdigställda bostäder per invånare. Vardag: hushållens tillgång till snabbt bredband.
- Ingen poäng för politiska val, ursprung, områdesklassningar eller stora råantal. Upplevd trygghet får inte ersättas av antalet brott. Stora sammanvägda index används inte samtidigt med sina grundmått.
- Senaste publicerade mått till och med valt år, högst fem år efter redovisningsåret. Mätperioder redovisas; flerårsmedel beskrivs inte som rena årsobservationer. Minst halva kommunbeståndet måste ha uppgift för ett mått. Båda livslängdsmåtten måste ha samma period.
- Minst åttio procent viktat underlag och minst hälften av måtten i varje aktivt tema krävs. Saknade värden är inte noll. Poäng avrundas till en decimal för placering; lika resultat ger delad plats.
- Kommentarerna berättar enkelt om verkliga bidrag från aktiva mått. De säger inte att modellen bevisar orsak eller var alla bör bo. Små skillnader och ändrade placeringar kan bero på osäkerhet, andra kommuners resultat och varierande täckning.
- Automatisk omräkning i publiceringsbygget och i poängsidans viktreglage. Historiska standardresultat sparas per kontrollsumma och metodversion. Exakt formel visas under metoden på `/score/`; fokusvyns löptext behåller lätt svenska utan siffror/formler.

- Vikterna på `/score/` väljs med pekvänliga sliders med exakt tio nivåer, från Oviktigt till Viktigt. Den första nivån tar bort temat ur poängen. Poäng och kommentarer uppdateras direkt när reglagen flyttas. Återställning ska behålla standardvikterna och deras inbördes förhållanden.

- Visa ett litet årsdiagram under kommunpoängen på /score/ och i fokusvyn. Poängsidans diagram följer valda vikter, fokusvyn använder standardvikter. Visa endast år med beräkningsbar poäng i diagrammet och dess årslista. Årsväljaren på /score/ ska bara innehålla år där minst en kommun har beräkningsbar poäng med valda vikter. Behåll valt år när det finns kvar, välj annars senaste giltiga året. Ge en åtkomlig lista med exakta årsvärden. Använd samma metod och vikter genom hela serien. En ändrad relativ poäng är inte säkert en förbättring eller försämring.

## /boring/ – Enkelt sagt

En egen mobilanpassad väg in i statistiken, med mycket lätt svenska, enkla jämförelsebilder, en snabb överblick och en gissningsfråga. Alla befintliga skalära kommunmått ska vara sökbara och grupperade i ämnen. Exakta värden och källor öppnas per kort. Huvudtexten använder vanliga ord. Jämför bara samma mått och mätår, och bara jämförbara andelar eller värden per enhet med Sverige. Jämför inte kommunala råantal med rikets total. Visa saknade lokala värden som saknade; använd aldrig riksdata som lokal ersättning. Saknad statistik är inte noll. Mer eller mindre betyder inte automatiskt bättre eller sämre. Ingen humor på invånares eller utsatta gruppers bekostnad. Bygg underlaget med data/build-boring.py vid varje publicering; skriptet körs från prepare-public.py. Behåll länkar till fullständiga kartor, fokus, poäng och källtabeller.

## Gemensam design från /boring/

Hela projektet använder stilen från Enkelt sagt: varm ljus bakgrund, mörk grön text, stora tydliga rubriker, mjuka gröna/lila/aprikosa ytor, luftiga kort och stora tryckytor. Gemensamt tema finns i dist/assets/site-theme.css. Alla huvudsidors navigation har samma struktur och aktiva markering. Även lokala kartkomponenter och statistikfördjupningar ska följa temat. Behåll sidornas roller, statistik, kartfunktioner, sökning, filter, tidsreglage och sticky-regler. Ändra inte kartornas dataskalor för att byta visuell stil.

## Eget utvecklingsrepo

GitHub-repot https://github.com/einand/statistik- används för utveckling och är redan kopplat till Codex Cloud. Källkod, publicerad visningsdata, regler och idébank förs över dit som en första snapshot. Äldre arbetsfiler och Sites-historiken behålls i det ursprungliga repot. Befintlig webbplats och Sites-projektidentitet behålls. GitHub och Sites måste synkroniseras före fortsatt arbete/publicering; GitHub-anslutningen till Codex Cloud innebär inte automatisk Sites-publicering.
