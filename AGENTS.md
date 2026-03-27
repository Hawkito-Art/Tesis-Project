# AGENTS.md - Tesis Project Agent Instructions

## Project Snapshot

- Project type: Django backend API for municipal economic process management.
- Domain: CAM Alquízar (Consejo de Administración Municipal).
- Current stack:
  - Python 3.12 (venv)
  - Django 6.0.3
  - Django REST Framework 3.17.0
  - SQLite (default local DB)
- Repository layout:
  - `backend/tesis/` -> Django project root (`manage.py`)
  - `backend/venv/` -> local virtual environment
  - `context/` -> thesis/domain reference docs (functional requirements and background)

## Product/Domain Context for Agents

Use this context when proposing or implementing features:

- The system manages municipal economic data across multiple entities.
- Main processes include:
  - Authentication and session control (JWT requested at requirements level).
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

## Build and Run Commands

From repo root:

```bash
source backend/venv/bin/activate
cd backend/tesis
```

Core commands:

```bash
# Run development server
python manage.py runserver

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Open Django shell
python manage.py shell

# Create admin user
python manage.py createsuperuser

# Collect static assets (if needed)
python manage.py collectstatic
```

Useful checks:

```bash
# Django deployment checks
python manage.py check

# Show pending migrations
python manage.py showmigrations
```

## Test Commands (Important)

From `backend/tesis` with venv active:

```bash
# Run all tests
python manage.py test

# Run tests for one app
python manage.py test <app_name>

# Run one test class
python manage.py test <app_name>.tests.<TestClass>

# Run one specific test method (single test)
python manage.py test <app_name>.tests.<TestClass>.<test_method>

# Verbose mode
python manage.py test -v 2

# Keep test DB for faster reruns
python manage.py test --keepdb
```

Notes:
- Prefer writing deterministic unit tests for serializers, services, and view logic.
- For API endpoints, use DRF `APITestCase` or Django test client patterns consistently.

## Lint/Format Commands

No lint config file is currently committed. Recommended toolchain:

```bash
pip install black isort flake8
```

Run manually from repo root:

```bash
# Format
black backend/tesis
isort backend/tesis

# Lint
flake8 backend/tesis

# Combined check (CI-style)
isort --check-only backend/tesis && black --check backend/tesis && flake8 backend/tesis
```

## Code Style Guidelines

### Formatting

- Follow PEP 8.
- 4 spaces indentation, no tabs.
- Max line length: 88.
- Prefer short functions with clear responsibilities.
- Avoid dead code and commented-out blocks.

### Imports

Order imports in this sequence:
1. Standard library
2. Third-party packages
3. Local app imports

Example:

```python
from pathlib import Path

from django.conf import settings
from rest_framework import serializers

from .models import Entity
```

Use `isort` conventions; avoid wildcard imports.

### Types and Signatures

- Add type hints to new service functions and non-trivial methods.
- Use explicit return types when practical.
- Prefer `QuerySet[Model]` style hints when available.
- Avoid misleading `Any`; use concrete types where possible.

### Naming Conventions

- Classes: `PascalCase`
- Functions/methods/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Django apps: lowercase, underscores if needed
- URL names: lowercase with hyphens or underscores, consistent per app

### Django/DRF Conventions

- Keep business logic out of views when it grows; extract to service layer.
- Serializers validate input; views orchestrate request/response flow.
- Use `select_related`/`prefetch_related` to avoid N+1 queries.
- Use `ModelViewSet` only when CRUD semantics fit; otherwise explicit APIView/ViewSet actions.
- Paginate list endpoints when result size can grow.

### Error Handling

- Fail with clear, actionable messages.
- Prefer DRF exceptions and proper HTTP status codes over broad `try/except`.
- Catch specific exceptions only (e.g., `Model.DoesNotExist`, `ValidationError`).
- Never swallow exceptions silently.
- Validate external file data (Excel/import flows) defensively.

### Security

- Never commit secrets, tokens, or credentials.
- Do not hardcode production `SECRET_KEY`.
- Keep `DEBUG=False` in production-like settings.
- Validate and sanitize uploaded file content and schema.
- Enforce auth/permissions explicitly on sensitive endpoints.

### Documentation and Comments

- Add docstrings to public classes/functions and non-obvious service logic.
- Keep comments focused on intent and constraints, not obvious mechanics.
- Update docs/tests when behavior changes.

## Suggested Backend Structure for New Features

Under `backend/tesis`:

- `apps/<domain_app>/models.py`
- `apps/<domain_app>/serializers.py`
- `apps/<domain_app>/views.py`
- `apps/<domain_app>/services.py` (business rules)
- `apps/<domain_app>/selectors.py` (read/query logic, optional)
- `apps/<domain_app>/urls.py`
- `apps/<domain_app>/tests/`

Register app URLs in `tesis/urls.py` with namespaced prefixes (e.g., `api/indicators/`).

## Git and Delivery Practices

- Branch naming:
  - `feature/<short-description>`
  - `fix/<short-description>`
- Commit messages: imperative, specific, and scoped.
- Before opening PR:
  - run tests,
  - run formatting/lint checks,
  - verify migrations are intentional.
- Do not mix unrelated refactors with feature/fix commits.

## Agent Execution Preferences

When acting as an automated coding agent in this repository:

- Read existing code before proposing architecture changes.
- Prefer minimal, focused diffs aligned with Django conventions.
- Include tests for behavior changes.
- If requirement ambiguity exists, infer from thesis context and current code, then document assumptions.
- Highlight any mismatch between documented requirements (JWT, imports, indicators) and current implementation state.


