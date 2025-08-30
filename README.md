# DVDRental Visualisation

Exploratory data analysis and plots for the classic **dvdrental** PostgreSQL dataset.  
Primary goal: reveal rental/revenue patterns, catalog structure, and store/customer behavior.  
The project is **Python-first**; **Docker** is used only to provide a reproducible Postgres.

---

## What’s analyzed

- Time series: rentals and payments by month (overall & per store).
- Store performance: side-by-side comparisons (volume, revenue proxy).
- Catalog structure: film length groups, category mix, duration quartiles.
- Talent/credits: top actors by number of films.
- Trends: monthly stacked views; pivoted line charts.

Plots are written to `app/out/`.

---

## How it works (pipeline)

1) SQL lives in `app/queries/` and is loaded via a tiny helper (`load_sql` in `sql.py`).  
2) Connection uses SQLAlchemy; credentials come from environment variables (no `.env`).  
3) Pandas transforms; Matplotlib (Agg) saves charts to `app/out/`.

---

## Project structure
```
dvdrental_visualisation/
├─ docker-compose.yml                     # Compose file (postgres, optional app)
├─ dvdrental_presentation.pdf
├─ initdb/
│  ├─ dvdrental.tar                       # Dataset dump (pg_dump custom format)
│  └─ load.sh                             # Auto-restore dvdrental.tar on first DB init
└─ app/
   ├─ Dockerfile
   ├─ requirements.txt                    # pandas, matplotlib, SQLAlchemy>=2.0, psycopg2-binary, python-dotenv
   ├─ dvdrental_vis.py                    # Main script: orchestrates analyses & saves plots
   ├─ packages/
   │  ├─__init__.py
   │  ├─ db_engine_init.py                   # Engine factory using env vars (os.getenv)
   │  ├─ paths.py                            # Paths/constants (e.g., QUERIES_DIR, OUT)
   │  ├─ sql.py                              # load_sql() helper
   ├─ queries/
   │  ├─ q1.sql
   │  ├─ q2.sql
   │  ├─ q3.sql
   │  ├─ ... 
   └─ out/
      ├─ Q1.png
      ├─ Q2.png
      ├─ ...  
```

---


## Run locally (Python)

Prereqs: Python 3.11+

1) **(Optional)** create a virtualenv and install deps
  ```
  python3 -m venv .venv
  source .venv/bin/activate
  python -m pip install -U pip
  python -m pip install -r app/requirements.txt
  ```

2) Set DB env vars (script reads these via `os.getenv`)
- If using the Docker Postgres from this repo:
  ```
  export PGHOST=localhost
  export PGPORT=5433   # host → container port mapping
  export PGUSER=postgres
  export PGPASSWORD=postgres
  export PGDATABASE=dvdrental
  ```

3) Run the analysis
  ```
  python app/dvdrental_vis.py
  ```

Charts will appear in `app/out/`.

---

## Postgres via Docker (simple, recommended)

Start a clean Postgres 16 with persistent storage:
  ```
  docker compose up -d postgres
  ```

Seed data (first boot auto-restores if `initdb/dvdrental.tar` exists).  
To restore manually into a running DB:
  ```
  docker compose exec -T postgres bash -lc
  'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" /docker-entrypoint-initdb.d/dvdrental.tar'
  ```

Then run locally with `PGHOST=localhost` and `PGPORT=5433` (see above).

---

## (Optional) Run the Python app inside Docker

Build the image once:
  ```
  docker compose build app
  ```


Run on demand (one-shot):
  ```
  docker compose run --rm app python dvdrental_vis.py
  ```


Inside containers the app connects with `PGHOST=postgres`, `PGPORT=5432` (set in `docker-compose.yml`).

---

## Useful commands

- Stop services (keep data): `docker compose stop`
- Start again: `docker compose start`
- Tear down (keep data): `docker compose down`
- Fresh reset (delete DB volume): `docker compose down -v`

---

## Troubleshooting

- Script “worked without tar”: you likely hit a different DB. Use `PGPORT=5433` when talking to the Docker Postgres from your host.
- Missing tables (e.g., `film`): restore the dataset (see Docker section).
- Auth failures: double-check `PGUSER/PGPASSWORD` in your shell or `.env`.

---

## Presentation

A short PDF with highlights is included in the repo as dvdrental_presentation.pdf .



