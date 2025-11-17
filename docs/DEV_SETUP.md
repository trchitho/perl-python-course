Local Development Setup

Prerequisites
- Python 3.11+
- PowerShell (on Windows) or a POSIX shell

Install dependencies
- Windows (PowerShell):
  - `py -m venv .venv`
  - `.\.venv\Scripts\Activate.ps1`
  - `pip install -r requirements.txt`

Run the backend
- `py backend\app.py`
- Health: http://127.0.0.1:5000/
- API: http://127.0.0.1:5000/api/*

Open the frontend
- Open `frontend\index.html` directly or run a static server and point it to that folder.

Database configuration
- Default: SQLite file at `backend/app.db` (auto-created).
- To use SQL Server:
  - Set `DB_DIALECT=mssql`
  - Optionally set: `MSSQL_SERVER`, `MSSQL_DATABASE`, `MSSQL_USERNAME`, `MSSQL_PASSWORD`, `MSSQL_DRIVER`
  - Or set a full `DATABASE_URL` for SQLAlchemy.

Common admin tasks
- Create user (admin panel uses: `/api/admin/users` via `frontend/services/adminAPI.js`).
- Change roles, lock/unlock users, inspect logs.

Notes
- When using MSSQL, the app does not call `db.create_all()`. It assumes tables already exist and uses raw SQL where naming differs.

