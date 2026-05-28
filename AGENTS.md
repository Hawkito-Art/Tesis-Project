# AGENTS.md - Tesis Project Agent Instructions

## Project Snapshot

- Project type: Full-stack application for municipal economic process management.
- Domain: CAM Alquízar (Consejo de Administración Municipal).
- Current stack:
  - **Backend**: Python 3.12 (venv), Django 6.0.3, Django REST Framework 3.17.0, SQLite (default local DB)
  - **Frontend**: Next.js 16.2.6 (App Router), React 19, TypeScript 5.7, Tailwind CSS 4, shadcn/ui, TanStack Query, Axios, pnpm.
- Repository layout:
  - `backend/tesis/` -> Django project root (`manage.py`)
  - `backend/venv/` -> local virtual environment
  - `fronted/municipal-council-system/` -> Next.js frontend (Note: folder is named `fronted` instead of `frontend`)
  - `context/` -> thesis/domain reference docs (functional requirements and background)

## Product/Domain Context for Agents

Use this context when proposing or implementing features:

- The system manages municipal economic data across multiple entities.
- Main processes include:
  - Authentication and session control. Currently fully integrated end-to-end via JWT (djangorestframework-simplejwt). Frontend uses a custom AuthProvider, Axios interceptors, and stores the refresh token in `localStorage` with body-based refresh requests (no cookies required).
  - Spreadsheet import and standardization.
  - Data migration into DB.
  - Indicator processing (accumulated values, correlation, estimates).
  - Linking indicators to municipal entities.
  - Reporting/export workflows.
- Prioritize reliability, traceability, and data integrity over UI concerns.

## Cursor/Copilot Rules Check

- `.cursorrules`: not found.
- `.cursor/rules/`: not found.
- `.github/copilot-instructions.md`: not found.
- If these files are added later, they must be treated as higher-priority repo guidance.

## Environment Setup

### Backend
Run from repository root (`/home/arturoa-dev/Desktop/Tesis Project`):

```bash
# Activate virtual environment
source backend/venv/bin/activate

# Verify interpreter and packages
python --version
pip list
```

If dependencies are missing:

```bash
pip install Django==6.0.3 djangorestframework==3.17.0
```

### Frontend
Run from the frontend directory:

```bash
cd fronted/municipal-council-system
pnpm install
```

Make sure there is a `.env` file in `fronted/municipal-council-system/` with:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Build and Run Commands

### Backend
From repo root:

```bash
source backend/venv/bin/activate
cd backend/tesis

# Run development server
python manage.py runserver

# Apply database migrations
python manage.py makemigrations
python manage.py migrate
```

### Frontend
From repo root:

```bash
cd fronted/municipal-council-system

# Run development server (Turbopack)
pnpm dev
```

## Test Commands (Important)

### Backend
From `backend/tesis` with venv active:

```bash
# Run all tests
python manage.py test

# Run tests for one app
python manage.py test <app_name>

# Verbose mode and keep DB
python manage.py test -v 2 --keepdb
```

Notes:
- Prefer writing deterministic unit tests for serializers, services, and view logic.
- For API endpoints, use DRF `APITestCase` or Django test client patterns consistently.

### Frontend
```bash
cd fronted/municipal-council-system
pnpm typecheck   # Check TypeScript errors
pnpm build       # Full production build test
```

## Code Style Guidelines

### Backend (Python/Django)
- Follow PEP 8 (black, isort, flake8). Max line length: 88.
- Extract business logic out of views into the `services.py` layer.
- Serializers validate input; views orchestrate request/response flow.
- Use `select_related`/`prefetch_related` to avoid N+1 queries.
- Catch specific exceptions only (e.g., `Model.DoesNotExist`, `ValidationError`).
- Add type hints to new service functions and non-trivial methods.

### Frontend (Next.js/React)
- Use App Router conventions (`app/page.tsx`, `app/layout.tsx`).
- Use `'use client'` only at the component level where hooks or event listeners are required. Keep layouts and top-level pages as server components where possible (unless they require context like AuthProvider).
- Fetch data using TanStack Query via Axios (`apiClient` defined in `lib/axios.ts`).
- Handle forms using `react-hook-form` and `zod` for schema validation.
- Use `shadcn/ui` and Tailwind utility classes for styling.
- Authentication: Do not bypass auth in development. `useAuth()` provides `user`, `isLoading`, and `isAuthenticated`.

### Authentication Flow (Frontend <-> Backend)
- **Login**: `POST /api/auth/login/` (payload: email/password). Returns `access` and `refresh` tokens.
- **Storage**: The `access` token is stored in memory via `setAccessToken()`. The `refresh` token is stored in `localStorage` under `refresh_token`.
- **Axios Interceptor**: Automatically attaches the `access` token. On `401 Unauthorized`, it pauses requests, reads `localStorage`, sends `{ refresh }` to `POST /api/auth/refresh/`, updates the access token, and retries.
- **CORS**: Requires `withCredentials: false` in Axios as we do not use HttpOnly cookies for JWTs. Ensure `CORS_ALLOW_ALL_ORIGINS = True` (or proper allowed hosts) in Django settings.

## Suggested Backend Structure for New Features

Under `backend/tesis`:

- `apps/<domain_app>/models.py`
- `apps/<domain_app>/serializers.py`
- `apps/<domain_app>/views.py`
- `apps/<domain_app>/services.py` (business rules)
- `apps/<domain_app>/urls.py`
- `apps/<domain_app>/tests/`

Register app URLs in `tesis/urls.py` with namespaced prefixes (e.g., `api/indicators/`).

## Git and Delivery Practices

- Branch naming: `feature/<short-description>`, `fix/<short-description>`
- Commit messages: imperative, specific, and scoped.
- Do not mix unrelated refactors with feature/fix commits.

## Agent Execution Preferences

When acting as an automated coding agent in this repository:

- Read existing code before proposing architecture changes.
- Prefer minimal, focused diffs aligned with Django and Next.js conventions.
- Include tests for behavior changes in the backend.
- If requirement ambiguity exists, infer from thesis context and current code, then document assumptions.
