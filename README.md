# Sverige i siffror

Källkod och självhostad visningsdata för Sveriges statistikwebbplats.

- Webbplats: https://sveriges-lansbefolkning-1749-2025.einand.chatgpt.site/
- Utvecklingsrepo: https://github.com/einand/statistik-
- GitHub Pages: https://einand.github.io/statistik-/
- Läs **AGENTS.md**, **BESLUT.md** och **IDEBANK.md** innan du ändrar projektet.

## Codex Cloud

Repot är redan kopplat till Codex Cloud. Arbeta här och committa ändringar till en arbetsgren/PR eller till överenskommen huvudgren. Publicering via Sites är ett separat steg och använder den befintliga projektidentiteten och adressen i `.openai/hosting.json`.

## Bygg och kontrollera

Kräver Python 3 och Node.js (22 eller senare). Inga externa Python- eller npm-paket behövs för ordinarie bygge.

```bash
node tests/score-engine.cjs
node tests/score-build.cjs
python data/prepare-public.py
python -m http.server 8000 --directory build
```

`dist/` innehåller sidornas källfiler och visningsdata. `build/` är genererat och ska inte committas. `data/` innehåller hämtnings- och byggskript. Stora datafiler laddas vid behov av webbplatsen.

## GitHub Pages

Arbetsflödet `.github/workflows/github-pages.yml` testar, bygger och publicerar
automatiskt vid push till `main`. Välj **Settings → Pages → Source → GitHub
Actions** i GitHub-repot vid första aktiveringen.

```bash
python data/prepare-github-pages.py --base-path /statistik-/
```

Resultatet ligger i `public-build/github-pages/`. Bygget anpassar lokala länkar,
skript och dataadresser till `/statistik-/` i en separat arbetskopia. Det ändrar
inte `dist/`, sparad poänghistorik eller det befintliga Sites-projektet.
För lokal kontroll ska paketet serveras under samma `/statistik-/`-sökväg.
GitHub Pages-publicering och Sites-publicering är separata arbetsflöden.

## Första överföringen

Engångsimporten återställer källkod samt en kontrollerad kopia av den publicerade webbplatsens visningsdata. Nedladdningar verifieras mot sparade SHA-256-kontrollsummor. Äldre arbetsfiler och historiken från Sites-repot finns kvar där; detta GitHub-repo börjar med en ny snapshot.

Efter lyckad import ligger kod och visningsdata direkt i repot och behöver inte hämtas från den publicerade webbplatsen igen. Engångsmanifestet ligger kvar för spårbarhet. Arbetsflödet körs endast vid ändring av importfilerna eller på uttrycklig begäran. Det ursprungliga Sites-repot och den publicerade adressen behålls.

## Arbetsflöde framöver

GitHub är utvecklingsrepot. Innan en ändring publiceras ska GitHub och Sites bygga från samma granskade källäge. Synkronisera med GitHub före arbete så att ändringar från Codex Cloud inte skrivs över. Använd inte force-push för att kringgå avvikande historik. Lagra aldrig tokens eller nycklar i repot.
