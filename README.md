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

The matcher runs **fully offline** on a committed deterministic enrichment cache, so the demo needs **no API key**. An LLM pass (OpenAI) upgrades the tags when a key is available.

### Key design decisions & assumptions
- **Gender is parent-specified, not same-gender.** ~57% of students state a desired mentor gender; ~22% of those request the *opposite* gender. So gender is enforced only when stated.
- **Capacity is defined by us** — the CSV `capacity` column is actually an availability schedule. We model capacity as the number of non-overlapping session blocks, capped by `max_students_per_mentor`.
- **Session length is not in the data** → a single `session_length_minutes` config value (default 30).
- **`learning_slot` entries are alternatives** (any-of); each student needs one weekly session.
- **LLM as a cached enrichment layer, not in the live matching loop** → deterministic, auditable, reproducible matching; the LLM only normalizes bilingual text to a closed tag vocabulary.

## Quickstart

```bash
pip install -e .                       # or: pip install -r requirements.txt
python -m matcher.cli run              # match on the committed cache → outputs/
streamlit run app/streamlit_app.py     # interactive UI
```

`python -m matcher.cli run` prints a metrics summary and writes `outputs/run_assignments.csv`, `run_unassigned.csv`, `run_review_queue.csv`. Other commands:

```bash
python -m matcher.cli run --engine greedy   # baseline engine
python -m matcher.cli rematch               # Q4 rejection + re-match
python -m matcher.cli enrich --sync --sample 25   # live LLM enrichment (needs OPENAI_API_KEY)
```

Representative results (committed keyword cache, default config):

| Engine | Coverage | Mean score | vs random |
|--------|----------|-----------|-----------|
| optimal | ~99.8% | ~0.38 | **+0.20** |
| greedy  | ~98%   | ~0.36 | +0.19 |
| random  | ~99%   | ~0.18 | — |

## Tuning & overrides (no code edits)

- **`config.yaml`** — `session_length_minutes`, `max_students_per_mentor`, `enforce_gender`, scoring `weights`, `thresholds`, `rejection_probability`, `random_seed`, `engine`. (The Streamlit sidebar exposes all of these live.)
- **`overrides.yaml`** — `force` a pair, `block` a pair, `skip_students` / `skip_mentors`. The UI has equivalent text boxes. Re-run to recompute.

## LLM enrichment (OpenAI)

Two paths, one cache schema (`data/cache/*.json`), using **Structured Outputs** for schema-valid tags:

- **Offline / bulk** — `python -m matcher.cli enrich` uses the **Batch API** (50% cheaper) for the full 2,200 rows.
- **Live / in-app** — the **"LLM enrichment"** panel in the Streamlit app: pick a model + sample size, click **Run** → concurrent calls with a progress bar; tags update and matching recomputes. Each row is retried up to **`max_retries`** times (default 2) before falling back to the keyword tagger (flagged `llm_failed`). Results are **auto-saved to the cache** for reuse, and the Data tab has **Save** + **Download JSON** controls (commit the JSON, or attach a Render persistent disk at the cache path, for persistence across redeploys).

Model is config/env-driven (`OPENAI_MODEL`, default `gpt-4o-mini`). **The API key is auto-loaded** from `st.secrets["OPENAI_API_KEY"]` or the `OPENAI_API_KEY` env var — there's **no key box to fill on open**. Set it once on Render (env var) and locally in `.streamlit/secrets.toml` (git-ignored — see `.streamlit/secrets.toml.example`). The key is never committed. With no key, a deterministic VI/EN keyword tagger fills every field (and always backs gender via regex), so the tool never hard-depends on the API.

### Data management (Data tab)

The app's **Data** tab shows the current students/mentors tables, lets you **upload replacement CSVs** (validated against the required columns — upload one or both), **reset** back to the bundled dataset, and download the current data. Uploaded data lives for the session (the deployed container's filesystem is ephemeral).

## Deployment

**Render + GitHub Actions:**

1. Push this repo to GitHub.
2. On Render: **New ▸ Blueprint**, select the repo (`render.yaml` defines a Docker web service that auto-deploys the `main` branch, with a `/_stcore/health` check). Set **`OPENAI_API_KEY`** as a service env var to enable live enrichment.
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
src/matcher/   config, data_io, enrich, schedule, capacity, constraints,
               scoring, matcher, rematch, metrics, cli
app/           streamlit_app.py        (UI + live LLM enrichment)
data/          input CSVs + committed enrichment cache
tests/         pytest unit tests
Dockerfile · render.yaml · .github/workflows/ci.yml   (deploy/CI)
config.yaml · overrides.yaml                          (tunables)
```
