# TeenCare Mentor–Student Matcher

A **rule-driven, tunable** tool that assigns 2,000 students to 200 mentors — not a one-off CSV export. The interviewer can change rules and weights, apply manual overrides, run the LLM enrichment live, and judge match quality, all from a web UI or the CLI.

> **Live URL:** _set after deploying to Render (see [Deployment](#deployment))._

---

## How it answers the brief

| Q | Question | Approach |
|---|----------|----------|
| **Q1** | Feasible matching (time + gender hard constraints, capacity) | Gender = the **parent's requested mentor gender** parsed from text, enforced only when stated (often *opposite* the student's gender). Time = a student `learning_slot` must fit a mentor availability window with room for `session_length`. Capacity = **slot-derived** (non-overlapping session blocks) + a configurable cap. Unassignable students are reported with the binding reason. |
| **Q2** | Improve with parent/student expectations | A cached **LLM enrichment** pass turns messy VI/EN text into structured tags (`desired_focus`, traits, …). Score = weighted tag overlap on feasible pairs. Measured as Δ vs a **random feasible baseline**. |
| **Q3** | Two-way fit (mentor preferences + student symptoms) | Adds the mentor's `preferred_student` needs and the student's `symptom_category` → a blended two-sided score. Feasible-but-weak pairs are flagged to a **review queue**. |
| **Q4** | Rejection & re-matching | Each matched student rejects with ~20% probability (seeded); kept students are pinned, rejected students are barred from their old mentor and re-matched against remaining capacity. Reports quality before/after. |

## How it works

```
CSVs ─► data_io (parse JSON schedules)
     ─► enrich  (messy VI/EN text → structured tags, cached)
     ─► constraints (gender + time → feasible edges, applies overrides)
     ─► scoring (Q2/Q3 weighted tag scores per edge)
     ─► matcher (greedy baseline | optimal min-cost-flow + booking + repair)
     ─► metrics / CSV outputs / Streamlit UI
```

Enrichment is **LLM-only** (OpenAI). The semantic tags come solely from the LLM and are persisted (Supabase, or local JSON) for reuse. Rows not yet enriched get a **base record** — empty semantic tags plus a deterministically parsed gender — so Q1 (hard constraints) always works; Q2/Q3 scores rise once enrichment runs.

### Key design decisions & assumptions
- **Gender is parent-specified, not same-gender.** ~57% of students state a desired mentor gender; ~22% of those request the *opposite* gender. So gender is enforced only when stated.
- **Capacity is defined by us** — the CSV `capacity` column is actually an availability schedule. We model capacity as the number of non-overlapping session blocks, capped by `max_students_per_mentor`.
- **Session length is not in the data** → a single `session_length_minutes` config value (default 30).
- **`learning_slot` entries are alternatives** (any-of); each student needs one weekly session.
- **LLM as a cached enrichment layer, not in the live matching loop** → deterministic, auditable, reproducible matching; the LLM only normalizes bilingual text to a closed tag vocabulary.

## Quickstart

```bash
pip install -e .                       # or: pip install -r requirements.txt
python -m matcher.cli run              # match via CLI → outputs/
streamlit run app/streamlit_app.py     # interactive UI
```

### Using the app

The sidebar has a **🌐 language toggle (English / Tiếng Việt)** that translates the whole UI, and a **page selector**: **Matcher · 📖 Instruction · 📋 Description** (the Instruction page is a how-to; the Description page explains the layers — data upload, enrichment, and the per-question algorithms).

The **Matcher** page has tabs: **📁 Data & Enrichment · Q1 · Q2 · Q3 · Q4**. The first tab combines data + enrichment: view raw data and enriched tags (Raw / Enriched sub-tabs per kind), upload/reset the dataset, and run enrichment. **Uploading new data auto-enriches all rows** and replaces the dataset + tags in the store. Each question is self-contained — its own controls plus a **▶ Run** button that executes *that question's* method (nothing auto-recomputes):

- **Q1** — hard constraints (session length, capacity, gender, engine) → feasible matching + unassigned reasons.
- **Q2** — focus + trait weights → parent-expectation scoring, shown vs the random baseline.
- **Q3** — symptom + mentor-preference weights (building on Q2) → two-way fit + poor-fit review queue.
- **Q4** — rejection probability + seed → simulate rejection on the Q3 match and re-match.

Run **🤖 Enrichment** first so Q2/Q3 have LLM tags (Q1 doesn't need it). Manual overrides (force/block/skip) are in the sidebar and apply on the next Run.

`python -m matcher.cli run` prints a metrics summary and writes `outputs/run_assignments.csv`, `run_unassigned.csv`, `run_review_queue.csv`. Other commands:

```bash
python -m matcher.cli run --engine greedy   # baseline engine
python -m matcher.cli rematch               # Q4 rejection + re-match
python -m matcher.cli enrich --sync --sample 25   # live LLM enrichment (needs OPENAI_API_KEY)
```

Representative results **after enrichment** (default config). Before enrichment, hard constraints give ~100% coverage at score 0; the engine gap appears once the LLM tags exist:

| Engine | Coverage | Mean score | vs random |
|--------|----------|-----------|-----------|
| optimal | ~100% | higher | **best** |
| greedy  | ~98%  | high   | + |
| random  | ~99%  | low    | — |

(optimal > greedy > random on mean score; the exact numbers depend on how many rows you enrich.)

## Tuning & overrides (no code edits)

- **`config.yaml`** — `session_length_minutes`, `max_students_per_mentor`, `enforce_gender`, scoring `weights`, `thresholds`, `rejection_probability`, `random_seed`, `engine`. (The app exposes the relevant ones in each question tab.)
- **`overrides.yaml`** (CLI) / **sidebar** (app) — `force` a pair, `block` a pair, `skip_students` / `skip_mentors`. In the app, the sidebar has an **"Add pair"** picker that searches students/mentors **by name** (no UUIDs to type). Overrides apply on the next Run.

## LLM enrichment (OpenAI) — LLM-only

The semantic tags come **only** from OpenAI **Structured Outputs**; there is no keyword tagger. Rows not yet enriched are base (unenriched) records — empty tags + parsed gender — so they score 0 until enriched. Two paths:

- **Offline / bulk** — `python -m matcher.cli enrich` uses the **Batch API** (50% cheaper) for the full dataset (requires `OPENAI_API_KEY`).
- **Live / in-app** — the **"LLM enrichment"** panel: pick a model + sample size (or **Enrich ALL**), click **Run** → concurrent calls with a progress bar; tags update and matching recomputes. Each row is retried up to **`max_retries`** times (default 2) before staying unenriched (flagged `llm_failed`). Results are **auto-saved** to the active store.

The API key is auto-loaded from `OPENAI_API_KEY` (env on Render, or `.streamlit/secrets.toml` locally) — **no key box on open**, never committed. Model is `OPENAI_MODEL` (default `gpt-4o-mini`).

### Persistence — Supabase (free) or local disk

Tags are stored via a pluggable backend (`src/matcher/store.py`):
- **Supabase** (Postgres) when `SUPABASE_URL` + `SUPABASE_KEY` are set → enrichment tags **and the raw dataset** persist across redeploys. One-time setup: run [`supabase_schema.sql`](supabase_schema.sql) in the Supabase SQL editor (creates `enrichment_tags` + `dataset_rows`), then set the two env vars. The app uses the **service-role key** server-side.
- **Local JSON** (`data/cache/*.json`) otherwise — fine for local dev, ephemeral on Render.

Uploading new CSVs in the Data tab **replaces the dataset in Supabase**; the app loads from Supabase on start (falling back to the bundled CSVs). Reset clears it.

The Data tab shows the active **backend**, a per-source breakdown (`llm` vs `unenriched`), and **Save** + **Download JSON** controls.

### Data management (Data tab)

The app's **Data** tab shows the current students/mentors tables, lets you **upload replacement CSVs** (validated against the required columns — upload one or both), **reset** back to the bundled dataset, and download the current data. Uploaded data lives for the session (the deployed container's filesystem is ephemeral).

## Deployment

**Render + GitHub Actions:**

1. Push this repo to GitHub.
2. On Render: **New ▸ Blueprint**, select the repo (`render.yaml` defines a Docker web service that auto-deploys the `main` branch, with a `/_stcore/health` check). Set env vars: **`OPENAI_API_KEY`** (enables LLM enrichment) and, for persistence, **`SUPABASE_URL`** + **`SUPABASE_KEY`** (after running `supabase_schema.sql`).
3. Render auto-deploys every push to `main` → public URL `https://<service>.onrender.com`.
4. [`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs `pytest` + a smoke match on every branch and PR, so you get a red/green signal before merging.

**Branch workflow** (develop/test on a branch, deploy by merging to `main`):

```bash
git checkout -b feature/x       # work on a branch — does NOT deploy
pytest -q                       # test locally
streamlit run app/streamlit_app.py
git push -u origin feature/x    # CI runs tests; still no deploy
# open a PR, merge to main  ->  Render auto-deploys
```

Run the same image locally:

```bash
docker build -t mentor-matcher .
docker run -p 8501:8501 mentor-matcher   # http://localhost:8501
```

## Testing

```bash
pytest -q
```

Covers slot/time boundaries, capacity non-overlap, gender-constraint logic (incl. opposite-gender requests), scoring math, and engine/override behavior (greedy vs optimal, force/block/skip).

## Project structure

```
src/matcher/   config, data_io, enrich, store, schedule, capacity, constraints,
               scoring, matcher, rematch, metrics, cli
app/           streamlit_app.py        (UI + live LLM enrichment + data tab)
data/          input CSVs
tests/         pytest unit tests
Dockerfile · render.yaml · .github/workflows/ci.yml   (deploy/CI)
supabase_schema.sql                                   (persistence table)
config.yaml · overrides.yaml                          (tunables)
```
