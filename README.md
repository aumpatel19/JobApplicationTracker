# JobApplicationTracker

Lightweight job application tracker with FastAPI (Python 3.11), SQLite, vanilla JS + Tailwind, daily reminder emails, and basic analytics.

## Features

- CRUD for Applications, Contacts, and Notes
- Stages: Draft → Applied → Interview → Offer → Rejected
- Search/filter (q, stage, date range), sorting, pagination
- Dashboard metrics: pipeline counts, weekly submissions, conversion rates
- CSV export for filtered applications
- Daily email reminders for due/overdue next actions (APScheduler + SMTP)
- Responsive UI (Tailwind CDN), board and list views

## Quickstart

1) Python 3.11+

2) Install dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3) Configure environment

```bash
cp .env.example .env
# Edit .env to match your SMTP settings (for reminders)
```

4) Run the server

```bash
uvicorn backend.main:app --reload
```

Open http://localhost:8000 to view the frontend.

5) Seed demo data (optional)

```bash
curl -X POST http://localhost:8000/api/dev/seed
```

## API Overview

- Base path: `/api`
- Applications
  - `GET /applications` — list with filters; returns `{ items, total_count }`
  - `POST /applications` — create
  - `GET /applications/{id}` — fetch single
  - `PUT /applications/{id}` — update (records stage changes)
  - `DELETE /applications/{id}` — delete (cascade contacts/notes)
  - `GET /applications/export.csv` — CSV export of filtered dataset
- Contacts
  - `GET /applications/{app_id}/contacts`, `POST /applications/{app_id}/contacts`
  - `PUT /contacts/{id}`, `DELETE /contacts/{id}`
- Notes
  - `GET /applications/{app_id}/notes`, `POST /applications/{app_id}/notes`
  - `PUT /notes/{id}`, `DELETE /notes/{id}`
- Metrics
  - `GET /metrics/summary` — pipeline counts, weekly submissions, conversion rates
- Dev utilities
  - `POST /dev/seed` — add sample data for demo

## Configuration

See `.env.example` for SMTP and app settings.

Key vars:
- `DATABASE_URL` (default: `sqlite:///./jobtracker.db`)
- `REMINDER_ENABLED=true|false` (enable/disable daily reminder job)
- SMTP_* vars for email sending

## Testing

```bash
pytest -q
```

Tests use an in-memory SQLite database and override dependencies for isolation.

## Notes

- CORS is enabled for `http://localhost:8000` and `http://127.0.0.1`.
- On startup, database indexes are created for faster listing: `stage`, `created_at`, `company`.
- Frontend is served statically from `frontend/` at `/`.

