# Morgenrapport — din personlige nyhetsside

En gratis, selv-oppdaterende nyhetsside:
- **GitHub Actions** henter RSS-feeder én gang om dagen og lagrer dem i `docs/news.json`.
- **GitHub Pages** viser `docs/index.html`, som leser `news.json` og `sources.json`.
- Du kan **skjule saker**, **slå kilder av/på** og **legge til egne RSS-kilder** direkte på nettsiden — alt lagres i nettleseren din (localStorage).

## Slik setter du det opp (ca. 5 minutter)

1. **Opprett et nytt repo på GitHub** (f.eks. `mine-nyheter`), og last opp alle filene i denne mappen (behold mappestrukturen).
   - Enklest: last ned/kopiér denne mappen, kjør i terminalen inne i mappen:
     ```
     git init
     git add .
     git commit -m "Første versjon av nyhetssiden"
     git branch -M main
     git remote add origin https://github.com/DITT-BRUKERNAVN/mine-nyheter.git
     git push -u origin main
     ```

2. **Skru på GitHub Pages**
   - Gå til repoet → **Settings → Pages**
   - Under «Build and deployment» → Source: **Deploy from a branch**
   - Branch: **main**, mappe: **/docs**
   - Lagre. Etter et minutt eller to er siden din live på `https://DITT-BRUKERNAVN.github.io/mine-nyheter/`

3. **Kjør nyhetshentingen første gang**
   - Gå til **Actions**-fanen i repoet
   - Velg workflowen **«Oppdater nyheter»**
   - Klikk **Run workflow** (manuell trigger) — den henter alle kildene og committer `docs/news.json`
   - Etter dette kjører den automatisk hver dag kl. 05:30 UTC (se `.github/workflows/update-news.yml` hvis du vil endre tidspunkt)

4. **Åpne nettsiden og tilpass**
   - Bruk **Innstillinger**-knappen øverst til høyre for å slå av kilder du ikke vil ha, eller legge til dine egne RSS-lenker
   - Egendefinerte kilder hentes direkte i nettleseren din (via en gratis RSS-til-JSON-tjeneste), så de dukker opp med én gang — de trenger ikke vente på neste daglige kjøring
   - **↻ Oppdater nå**-knappen henter ferske saker fra *alle* kildene (faste og egendefinerte) direkte i nettleseren, med én gang du trykker — du trenger ikke vente på den daglige automatiske kjøringen. Svarer en kilde ikke akkurat da (midlertidig nede, treg, e.l.), beholdes de sakene du allerede hadde fra den, i stedet for at de forsvinner
   - Klikk ✕ på en sak for å skjule den. «Vis skjulte saker igjen» i innstillingspanelet nullstiller dette. Skjulte saker forblir skjult selv etter «Oppdater nå», siden hver sak får en stabil id basert på lenken

## Filstruktur

```
docs/
  index.html      ← selve nettsiden (HTML/CSS/JS, ingen byggeverktøy nødvendig)
  sources.json     ← liste over faste RSS-kilder, gruppert på kategori
  news.json        ← genereres automatisk av scriptet, IKKE rediger manuelt
scripts/
  fetch_news.py    ← henter alle kildene og skriver news.json
.github/workflows/
  update-news.yml  ← kjører fetch_news.py automatisk hver dag
requirements.txt    ← Python-avhengighet (feedparser)
```

## Legge til eller endre faste kilder

Rediger `docs/sources.json` — hver kilde trenger `name`, `url` (RSS-lenke) og `category`
(en av: `innenriks`, `utenriks`, `okonomi`, `teknologi`, `naringsliv`, `hobby`, eller en ny
kategori du finner på selv). Push endringen, så plukkes den opp neste gang Action-en kjører
(eller kjør den manuelt fra Actions-fanen for å se endringen med én gang).

**Viktig om RSS-lenkene:** Jeg har fylt inn kjente, offentlige RSS-feeder for kildene du
nevnte (NRK, Aftenposten, Nettavisen, DN, Finansavisen, E24, TechCrunch, Mashable, Digi.no)
pluss noen utenriks-kilder (BBC, Al Jazeera). Nettsteder endrer av og til RSS-adressene sine
uten varsel — hvis en kilde slutter å gi treff i loggen fra Action-kjøringen («Actions» →
velg siste kjøring → se output fra `fetch_news.py`), søk opp riktig RSS-lenke for nettstedet
og oppdater `sources.json`. Jeg fant ikke noen offentlig RSS-feed for **Finansavisen** som jeg
kunne bekrefte var korrekt — sjekk gjerne selv, evt. fjern den raden hvis den ikke fungerer.

Det finnes ingen standardkilder for **hobby**-kategorien siden dette er ganske personlig —
legg gjerne til dine egne via innstillingspanelet på selve nettsiden, eller direkte i
`sources.json`.

## Begrensninger å være obs på

- Egendefinerte kilder, og alt som hentes via **↻ Oppdater nå**, går via `rss2json.com`
  sin gratis, offentlige API for å unngå CORS-problemer i nettleseren. Den har en viss
  kapasitetsgrense — for personlig bruk (noen klikk her og der) går dette fint, men
  enkelte feeder kan feile å hente av og til. Den daglige, automatiske oppdateringen via
  GitHub Actions er upåvirket av dette, siden den henter RSS-feedene direkte fra serveren
  i stedet for gjennom denne tjenesten.
- Skjulte saker og kildevalg lagres i nettleserens localStorage — det vil si at det er
  knyttet til **denne nettleseren/enheten**. Åpner du siden på mobilen også, må du skjule/
  velge kilder der på nytt.
- Ønsker du i stedet at innstillingene skal følge deg på tvers av enheter, må det legges
  til en liten backend (f.eks. en gratis database som Supabase) — si ifra så hjelper jeg
  deg med det.
