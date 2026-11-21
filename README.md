# BookShelf

[![CI/CD](https://github.com/jurekucanITK/bookshelf/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/jurekucanITK/bookshelf/actions/workflows/ci-cd.yml)

**Nameščena aplikacija:** https://bookshelf-jure.netlify.app (API: https://bookshelf-api-jure.onrender.com/docs)

BookShelf je spletna aplikacija za ljubitelje in zbiratelje knjig. Uporabnik v njej spremlja branje (zelim prebrati, trenutno berem, prebrano), ocenjuje knjige in si nastavi letni bralni cilj. Hkrati vodi evidenco domace knjiznice: katere knjige ima, v kaksnem formatu, kje stojijo in komu jih je posodil. Podatke lahko uvozi iz Goodreadsa.

## Tehnologije

- **Frontend:** React (Vite), React Router, Tailwind CSS
- **Backend:** Python (FastAPI)
- **Podatkovna baza:** PostgreSQL (Supabase)
- **Avtentikacija:** Firebase Authentication
- **Podatki o knjigah:** Open Library API

## Dokumentacija

Dokumentacija je v mapi [`docs`](docs/):

- [Zasnova resitve](docs/01-zasnova-resitve.md)
- [Funkcionalnosti in obseg](docs/02-funkcionalnosti-in-obseg.md)
- [Podatkovni model](docs/03-podatkovni-model.md)
- [Arhitektura in tehnoloski sklad](docs/04-arhitektura-in-tehnoloski-sklad.md)
- [Uporabniske zgodbe](docs/05-uporabniske-zgodbe.md)
- [Wireframes](docs/06-wireframes.md)
- [Pregled projekta](docs/07-pregled-projekta.md)

## Lokalni zagon

### Predpogoji

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (mora biti zagnan)
- [Supabase](https://supabase.com/) projekt
- dostop do Firebase projekta `rirs-bookshelf`

### Podatkovna baza

V Supabase klikni **Connect** in kopiraj niz za **Session pooler** (Direct connection deluje samo prek IPv6). Tabel ni treba ustvarjati rocno, ustvari jih Alembic ob zagonu backenda.

### Firebase (prijava)

Backend za preverjanje prijave potrebuje kljuc Firebase service account:

1. V [Firebase konzoli](https://console.firebase.google.com/) odpri projekt, nato **Project settings → Service accounts**.
2. Klikni **Generate new private key** in preneseno datoteko shrani kot `backend/firebase-service-account.json`.

Datoteka je skrivnost in je v `.gitignore`. Brez nje se backend zazene, endpointi s prijavo pa vrnejo napako 503. Spletna konfiguracija za frontend je ze v `frontend/src/firebase.js`.

Če uporabljaš svoj Firebase projekt, kopiraj `frontend/.env.example` v `frontend/.env.local` in nastavi spremenljivke `VITE_FIREBASE_*` (vrednosti so v Firebase konzoli pod **Project settings → General → Your apps**).

### Zagon aplikacije

1. Ustvari datoteko z nastavitvami backenda in v `DATABASE_URL` prilepi niz iz Supabase (z vpisanim geslom):
   ```bash
   cp backend/.env.example backend/.env
   ```
2. Zazeni backend in frontend:
   ```bash
   docker compose up --build
   ```
3. Aplikacija je dosegljiva na:
   - `http://localhost:5173` – frontend (na zacetni strani je izpisano, ali backend in baza delujeta)
   - `http://localhost:8000/docs` – samodejna dokumentacija API-ja
   - `http://localhost:8000/health/db` – preverjanje povezave z bazo

Ob spremembi kode v `backend/` ali `frontend/` se aplikacija sama osvezi. Ustavis jo s `Ctrl+C` ali `docker compose down`.

Frontend privzeto klice backend na `http://localhost:8000`. Ce je backend drugje, kopiraj `frontend/.env.example` v `frontend/.env.local` in spremeni `VITE_API_URL`.

Nov npm paket dodas z `docker compose exec frontend npm install <paket>`; ob naslednjem zagonu ga container namesti sam.

### Migracije baze (Alembic)

Ob vsakem zagonu backenda se samodejno izvede `alembic upgrade head`, ki v bazi izvede manjkajoce migracije.

Ko spremenis modele v `backend/app/models.py`, ustvari novo migracijo:

```bash
docker compose run --rm backend alembic revision --autogenerate -m "opis spremembe"
```

Ustvarjeno datoteko v `backend/alembic/versions/` preglej (spremembe `CHECK` omejitev je treba dopisati rocno) in jo dodaj v git. Ostali ukazi:

```bash
docker compose run --rm backend alembic current     # trenutna verzija baze
docker compose run --rm backend alembic downgrade -1  # razveljavi zadnjo migracijo
```

## Lint in testi

Testi backenda potrebujejo ločeno PostgreSQL bazo, katere ime se mora končati na `_test`. Ustvariš jo enkrat:

```bash
docker run -d --name bookshelf-test-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=bookshelf_test -p 5433:5432 postgres:16
```

Backend (Ruff in pytest s pokritostjo):

```bash
docker compose run --rm -e DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5433/bookshelf_test backend sh -c "pip install -q -r requirements-dev.txt && ruff check . && pytest"
```

Frontend (oxlint in Vitest s pokritostjo):

```bash
docker compose run --rm frontend sh -c "npm run lint && npm run test:coverage"
```

## CI/CD

Cevovod [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml) se zažene ob vsakem pull requestu v `main` in ob vsakem pushu na `main`. Joba `lint`, `build` in `test` tečejo vzporedno, `deploy` pa se zažene šele, ko so vsi trije uspešni.

| Faza | Kaj naredi |
| --- | --- |
| `lint` | Preveri frontend z oxlint in backend z Ruff. Ob napaki ali opozorilu job pade. |
| `build` | Zgradi frontend (`vite build`) in backend kot Docker sliko. Rezultata shrani kot artefakta `frontend-dist` in `backend-image`. Odvisnosti npm in pip ter plasti Docker slike so predpomnjene. |
| `test` | Zažene teste backenda (pytest na PostgreSQL servisu) in frontenda (Vitest). Poročilo o pokritosti shrani kot artefakt `coverage-report`. |
| `deploy` | Samo ob pushu na `main`, v okolju `production`. Uporabi artefakte iz joba `build`: Docker sliko objavi v GitHub Container Registry in jo namesti na Render, `dist/` pa namesti na Netlify. Na koncu preveri, da sta frontend in backend dostopna. |

Veja `main` je zaščitena: pull request je mogoče združiti samo, če so `lint`, `build` in `test` uspešni.

### Namestitev

- Frontend: Netlify
- Backend: Render (Docker slika iz `ghcr.io`, ob zagonu izvede migracije)
- Baza: Supabase (PostgreSQL), prijava: Firebase Authentication
- Omejitev: Open Library zavrača povezave z Renderja, zato nameščena aplikacija išče samo po lastnem katalogu. Lokalno iskanje po Open Library deluje.

V GitHubu so nastavljene spremenljivke repozitorija `VITE_API_URL` in `VITE_FIREBASE_*` ter secrets okolja `production`: `NETLIFY_AUTH_TOKEN`, `NETLIFY_SITE_ID` in `RENDER_DEPLOY_HOOK_URL`. Na Renderju so nastavljeni `DATABASE_URL`, `CORS_ORIGINS` in `FIREBASE_CREDENTIALS_JSON`.