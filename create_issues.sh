#!/usr/bin/env bash
# Creates labels, milestones, and issues for ProtocolLens.
# Requires the GitHub CLI (https://cli.github.com), logged in with `gh auth login`.
# Run once from inside the repository folder: bash create_issues.sh
set -euo pipefail

# Labels
for l in backend api frontend llm infra test docs eval; do
  gh label create "$l" --force >/dev/null
done

# Milestones
for m in 'P1: Full-stack minimal loop' 'P2: Evaluation' 'P3: Agent upgrade' 'P4: MCP and audit trail'; do
  gh api "repos/{owner}/{repo}/milestones" -f title="$m" >/dev/null
done

# Issues, created in working order
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'infra' --title 'Clean up repo and tag the hackathon version' --body '**Goal**
Remove files that should not be in the project folder and mark the last Streamlit-only version.

**Done when**
- [ ] Root-level `Lib/`, `Scripts/`, `etc/`, `share/` are deleted
- [ ] `.gitignore` covers `.venv/`, `__pycache__/`, `*.pyc`, `.env`
- [ ] `git ls-files` shows only project files; `.env` is not tracked
- [ ] Tag `v1.0-hackathon` is pushed'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'infra' --title 'Restructure into backend/ and frontend/' --body '**Goal**
Move the existing code into the layout in docs/design.md so later PRs land in the right place.

**Done when**
- [ ] `app/`, `tests/`, `config.py`, `requirements.txt` live under `backend/`
- [ ] Streamlit UI moved to `backend/legacy_streamlit/main.py` and still runs
- [ ] `pre_test/samples/` moved to `backend/tests/fixtures/`
- [ ] Empty `frontend/` folder with a placeholder README
- [ ] `docs/design.md` committed'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'backend,bug' --title 'Fix fallback bug in orchestrator.run' --body '**Goal**
`run()` calls `_fallback_pipeline`, which is commented out, so a single-pass failure raises `AttributeError`.

**Done when**
- [ ] Fallback code and the `prefer_fallback` parameter are removed
- [ ] A failed extraction raises a clear `ValueError`
- [ ] A test covers the failure path'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'backend' --title 'ClinicalTrials.gov client: search and fetch by NCT ID' --body '**Goal**
A small client for the ClinicalTrials.gov API v2 that the agent can call.

**Done when**
- [ ] `search(condition, term, lat, lon, radius, status)` returns a list of studies
- [ ] `get(nct_id)` returns one study
- [ ] Uses the `fields` parameter to request only needed modules
- [ ] Handles paging, timeouts, and retry with backoff
- [ ] Tests use recorded responses, no live calls'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'backend' --title 'Local cache for API responses and parsed criteria' --body '**Goal**
Avoid re-fetching and re-parsing the same trial.

**Done when**
- [ ] Cache keyed by NCT ID and `lastUpdatePostDate`
- [ ] Storage choice (SQLite or JSON files) recorded in docs/design.md open questions
- [ ] Cache hit and miss are covered by tests'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'backend' --title 'Mapper: API JSON to TrialObject' --body '**Goal**
Convert a raw study into the shared `TrialObject` schema without an LLM.

**Done when**
- [ ] All `TrialObject` modules are Optional; `source` field added
- [ ] Every fixture in `backend/tests/fixtures/` maps without error
- [ ] Missing modules (no phases, no maximumAge) produce `None`, not exceptions'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'backend,llm' --title 'PatientProfile schema and description parsing' --body '**Goal**
Turn a free-text patient description into a structured profile.

**Done when**
- [ ] `PatientProfile` model in `app/schemas/patient.py`, all fields Optional
- [ ] Prompt returns the profile through Gemini `response_schema`
- [ ] Facts not stated in the text stay empty
- [ ] Three synthetic patients saved as test inputs'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'backend' --title 'Structured pre-filter' --body '**Goal**
Drop trials that cannot fit, using structured fields only.

**Done when**
- [ ] Filters on age, sex, healthy volunteers, study type, and phase
- [ ] Requires at least one RECRUITING site within the travel radius
- [ ] Returns the reason for each rejected trial
- [ ] Pure functions with unit tests'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'backend,llm' --title 'parse_criteria: eligibility text to Criterion list' --body '**Goal**
Split the free-text eligibility block into individual criteria.

**Done when**
- [ ] `Criterion` model added (text, type, category, group, needs_protocol_reference)
- [ ] Regex pre-split on the Exclusion header; whole text goes to the LLM if no header is found
- [ ] Markdown escapes are stripped before the LLM call
- [ ] Works on the varied fixtures: `Key Inclusion Criteria`, mixed bullets, flattened sub-items'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'backend,llm' --title 'match_criteria: judge each criterion against the patient' --body '**Goal**
For each criterion return met, not_met, or unknown with a reason.

**Done when**
- [ ] Output includes verdict, one-sentence reason, and the patient fact used
- [ ] Anything not explicit in the profile is `unknown`
- [ ] A test patient with missing information produces `unknown`, not a guess'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'backend,llm' --title 'Agent loop with function calling' --body '**Goal**
Tie the tools together in a single-agent loop on Gemini function calling.

**Done when**
- [ ] Tools registered: search_trials, get_trial, prefilter, parse_criteria, match_criteria
- [ ] Limits enforced: 15 tool calls per session, top 10 trials matched
- [ ] Progress reported through a callback; the agent has no HTTP knowledge
- [ ] Ranking: failed trials marked not eligible, rest ordered by met share and unknown count'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'backend' --title 'Command-line script to run a match end to end' --body '**Goal**
Stage 1 demo: run the agent on a synthetic patient from the terminal.

**Done when**
- [ ] `python -m scripts.match "<description>"` prints progress and ranked trials
- [ ] Output shows per-criterion verdicts for the top trial

**Note**
End of stage 1. Worth a short screen recording for the README.'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'backend,api' --title 'FastAPI skeleton: health route, CORS, error shape' --body '**Goal**
The thin API layer over the core.

**Done when**
- [ ] `uvicorn api.main:app` starts; `/api/health` responds
- [ ] CORS allows only `FRONTEND_ORIGIN`
- [ ] All errors return `{code, message}`'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'backend,api' --title 'Session store and background agent task' --body '**Goal**
Run the agent per session and keep its state in memory.

**Done when**
- [ ] Session holds profile, results, and audit log; 30-minute expiry
- [ ] Agent runs as a background task and writes events to the session queue
- [ ] Expired or unknown session IDs return a clear error'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'backend,api' --title 'POST /api/match and the events stream' --body '**Goal**
Start a session and stream progress and results over server-sent events.

**Done when**
- [ ] `POST /api/match` returns `{session_id}`
- [ ] `GET /api/match/{id}/events` streams status, profile, trial_result, done, error
- [ ] A client can reconnect to a running session'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'backend,api' --title 'Trial routes: detail and role-based Q&A' --body '**Goal**
Expose one trial and the existing `ask_question` through the API.

**Done when**
- [ ] `GET /api/trials/{nct_id}` returns a `TrialObject`
- [ ] `POST /api/trials/{nct_id}/ask` takes role and question, returns an answer'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'backend,api,test' --title 'API tests with mocked Gemini and ClinicalTrials.gov' --body '**Goal**
Cover each route and the event sequence of a full session.

**Done when**
- [ ] Every route has a success and a failure test
- [ ] A full session test asserts the order of events
- [ ] No test makes a live network call'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'infra' --title 'CI: backend lint and tests' --body '**Goal**
Run checks on every PR.

**Done when**
- [ ] GitHub Actions workflow runs ruff and pytest on push and PR
- [ ] Status badge added to the README

**Note**
End of stage 2. The backend is demoable from `/docs`.'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'frontend' --title 'Frontend scaffold and generated API types' --body '**Goal**
Set up the React app and the typed contract with the backend.

**Done when**
- [ ] Vite + React + TypeScript + Tailwind + shadcn/ui running at localhost:5173
- [ ] `npm run gen:api` generates types from the backend OpenAPI schema
- [ ] Router with three routes: `/`, `/match/:sessionId`, `/trials/:nctId`
- [ ] TanStack Query set up with a typed client'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'frontend' --title 'Home page: PatientForm with example patients' --body '**Goal**
Where the user enters a patient description.

**Done when**
- [ ] Free-text input and a submit button that calls `POST /api/match`
- [ ] Three synthetic example patients can be loaded with one click
- [ ] PHI and not-medical-advice notice is visible'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'frontend' --title 'useMatchStream hook, ProgressTimeline, ProfileSummary' --body '**Goal**
Show the agent working in real time.

**Done when**
- [ ] `useMatchStream` handles every event type
- [ ] `ProgressTimeline` renders status events as they arrive
- [ ] `ProfileSummary` shows the parsed patient profile'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'frontend' --title 'TrialCard and CriterionTable' --body '**Goal**
Present each trial result and its per-criterion judgments.

**Done when**
- [ ] `TrialCard` shows verdict, met / not met / unknown counts, nearest site
- [ ] `CriterionTable` shows verdict, reason, and verbatim source text per row
- [ ] Table can be filtered by verdict'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'frontend' --title 'Trial detail page with RoleQA' --body '**Goal**
A page for one trial with role-based questions.

**Done when**
- [ ] Shows trial summary and the full criterion table
- [ ] Role selector and question box call the ask endpoint'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'frontend' --title 'Empty, error, and expired-session states' --body '**Goal**
Handle everything that is not the happy path.

**Done when**
- [ ] No trials found: message with suggestions
- [ ] Dropped stream: reconnects with the same session ID
- [ ] Expired session and backend failure each have a clear screen'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'frontend,test,infra' --title 'Frontend tests and CI job' --body '**Goal**
Component tests and a frontend job in CI.

**Done when**
- [ ] Tests for `CriterionTable` filtering and `useMatchStream` event handling
- [ ] CI runs lint, type-check, and Vitest
- [ ] CI fails if generated API types are out of date

**Note**
End of stage 3.'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'backend,api' --title 'Rate limit and per-session caps' --body '**Goal**
Protect the Gemini budget before the demo is public.

**Done when**
- [ ] Per-IP rate limit on `POST /api/match`
- [ ] Spending cap set on the Gemini API key
- [ ] Limits return a clear error the UI can show'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'infra' --title 'Deploy backend and frontend' --body '**Goal**
A public demo URL.

**Done when**
- [ ] Backend deployed; SSE connections stay open for a full session
- [ ] Frontend deployed and pointed at the backend
- [ ] Secrets are set as environment variables, not committed'
gh issue create --milestone 'P1: Full-stack minimal loop' --label 'docs' --title 'README: live link, demo recording, PHI note' --body '**Goal**
Make the project easy to evaluate in one minute.

**Done when**
- [ ] Live demo link at the top
- [ ] Short recording or GIF of a matching session
- [ ] Feature status table and roadmap table are current

**Note**
End of P1.'

# One planning issue per later phase
gh issue create --milestone 'P2: Evaluation' --label 'eval' --title 'P2 plan: evaluation' --body 'Rough scope, to be split into issues when this phase starts:

- [ ] Hand-labeled set for criteria parsing (20 to 30 trials)
- [ ] TREC Clinical Trials Track evaluation scripts
- [ ] Keyword-search baseline
- [ ] Results table in the README'
gh issue create --milestone 'P3: Agent upgrade' --label 'backend' --title 'P3 plan: agent upgrade' --body 'Rough scope, to be split into issues when this phase starts:

- [ ] RxNorm drug-class lookup
- [ ] Deterministic calculators (eGFR, CrCl, BMI, unit conversion)
- [ ] Follow-up questions: answers endpoint and FollowUpForm
- [ ] LangGraph orchestration
- [ ] Per-tool ablation study'
gh issue create --milestone 'P4: MCP and audit trail' --label 'backend' --title 'P4 plan: MCP and audit trail' --body 'Rough scope, to be split into issues when this phase starts:

- [ ] ProtocolLens MCP server (FastMCP)
- [ ] Audit trail endpoint and view in the UI
- [ ] ICH/FDA guidance documents as MCP resources'
