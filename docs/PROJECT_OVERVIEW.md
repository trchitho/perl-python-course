E‑Learning Website for Basic IT Beginners — Project Overview

Scope
- Backend: Flask REST API organized in MVC style under `backend/app/`
- Frontend: Static HTML/CSS/JS under `frontend/`
- Database: SQLite by default for local dev; optional SQL Server via ODBC

Key Modules (Backend)
- `backend/app.py`: Entrypoint calling `create_app()`.
- `backend/app/__init__.py`: App factory. Configures CORS, SQLAlchemy, JWT, blueprints.
- `backend/config.py`: Configuration. Picks DB via env; defaults to SQLite.
- Models (`backend/app/models/*`):
  - `user_model.py`: `users` table (id, fullname, email, password_hash, role, ...)
  - `course_model.py`: `courses`
  - `lesson_model.py`: `lessons`
  - `quiz_model.py`: `quizzes`, `quiz_questions`, `quiz_results`
  - `enrollment_model.py`: `enrollments`
  - `progress_model.py`: `progress`
  - `announcement_model.py`: `announcements`
  - `chatbot_history_model.py`: `chatbot_history`
  - `placement_test_model.py`: `placement_tests`
- Services:
  - `services/jwt_service.py`: Token issuing helpers.
- Controllers (`backend/app/controllers/*`): request-agnostic business logic. Many functions are dialect-aware (MSSQL vs generic) and use raw SQL where needed.
- Views (`backend/app/views/*`): Flask blueprints that validate input, enforce auth, and call controllers.

Key Modules (Frontend)
- `frontend/services/*.js`: Small API wrappers grouped by role/domain.
- `frontend/pages/*/*.html`: Static pages (auth, student, teacher, admin).
- `frontend/assets/*`: Global CSS/JS helpers and theme files.
- `frontend/components/*.html`: Reusable HTML snippets.

API Surface (High level)
- `/api/auth/*`: Registration and login (JWT bearer tokens).
- `/api/student/*`: Enrollments, course/lesson view, student quiz actions.
- `/api/teacher/*`: Teacher stats, CRUD for courses/lessons/quizzes, subscribers.
- `/api/admin/*`: Admin users CRUD, enrollments, settings, logs, stats.
- `/api/ai/chat`: Simple chatbot stub for now.

Security Model
- JWT bearer tokens with role claim (`student`, `teacher`, `admin`).
- Blueprints enforce role-based access for teacher/admin routes.
- CORS configured to allow local dev origins (`*` for API-only calls without cookies).

Database Strategy
- Generic path (SQLite/MySQL): snake_case table names, SQLAlchemy models.
- MSSQL path: raw SQL targets existing PascalCase tables under `[dbo]`.
- The app auto-creates tables only when NOT using MSSQL.

Recent Improvements
- Default to SQLite for local dev; MSSQL is opt-in via env.
- Standardized `users` model/table for generic path, fixing joins and FKs.
- Admin user actions now support MSSQL via raw SQL.

