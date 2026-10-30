# Duovo – webbplats

Statisk webbplats för duovo.app på svenska och engelska. Den här mappen är ett lokalt utkast: den är inte publicerad, inte ett Git-repo och inte kopplad till någon domän.

**Första versionen innehåller bara startsidan** (`/` och `/en/`). Integritet (`/integritet/`, `/en/privacy/`) och support (`/support/`, `/en/support/`) finns bara som lokala utkast tills deras underlag är klart.

## Bygga

```bash
python3 build.py              # utkast av alla sidor i preview/ (lokalt, publiceras aldrig)
python3 build.py --release    # bara sidorna i RELEASE_PAGES, i docs/, och listan release-files.txt
python3 tools/check-public.py # kontrollerar de faktiska filerna som skulle publiceras
```

Bara Python 3 behövs. Bygget fungerar utan appmappen.

## Titta lokalt

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

- Det som skulle publiceras: http://localhost:8765/docs/ och http://localhost:8765/docs/en/
- Utkast av alla sidor: http://localhost:8765/preview/

## Innehåll

| Mapp/fil | Vad |
|---|---|
| `build.py` | Startsidans texter på båda språken och mallen för sidorna. `RELEASE_PAGES` bestämmer vad som publiceras |
| `drafts/pages.py` | Utkasten till integritet och support. **Lokalt, utesluten i `.gitignore`.** Utan filen bygger `build.py` bara startsidan, och `--release` behöver den aldrig |
| `assets/` | Källfiler som kopieras in i bygget: `site.css` (appens färger, ljust och mörkt efter enhetens inställning), typsnitten Onest och Instrument Serif med sina OFL-licenser, och mejllogotyperna i `email/` |
| `source/` | Kopior av Figma-exporterna (logotyp, symbol, appikon, ikoner), se `source/README.md` |
| `docs/` | **Byggd.** Det GitHub Pages ska publicera, inklusive `CNAME` med domänen (`DOMAIN` i `build.py`). Redigeras inte för hand |
| `release-files.txt` | **Byggd.** Exakt lista över filerna i `docs/`, med storlek och SHA-256 |
| `preview/` | **Byggd.** Utkast av alla sidor med gula markeringar. Utesluten i `.gitignore` |
| `tools/` | `check-public.py` (publiceringskontroll), `email-logo.swift` (gör mejllogotyperna), `email-logo-preview.html` (logotyperna mot olika bakgrunder) |
| `planning/`, `REVIEW.md` | Interna underlag. **Ska inte ligga i det publika repot**, se `planning/Publiceringsplan.md`. Uteslutna i `.gitignore` |

Sidorna har inga formulär, ingen analys, inga cookies och inga externa anrop.

## Regler för texten

Startsidan beskriver bara funktioner som är byggda: inköpslistor, packlistor med uppsättningar och ångra. Den nämner inte delning, synk, live-läge eller hushåll förrän de är verifierade. Det finns ingen nedladdningslänk och ingen väntelista.

Integritet och support är utkast och ligger bara lokalt (`drafts/pages.py`). I utkasten står delar utan beslut som `[[...]]`, och passager som måste anpassas eller verifieras som `{{launch|...}}` och `{{verify|...}}`. Båda visas gult i `preview/`. `--release` bygger bara sidorna i `RELEASE_PAGES` och vägrar om någon av dem har sådana kvar.
