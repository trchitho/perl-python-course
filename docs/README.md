E-Learning Website for Basic IT Beginners — Documentation

This documentation captures the analysis and quality model for the perl-python-course project and aligns the system with an MVC-oriented Flask backend and static web frontend.

**SECTION A – FUNCTIONAL ANALYSIS & CONTEXT MODELING**
- A.1. Use Case Diagram
  - Source: `docs/diagrams/use-case.puml` (PlantUML)
  - Generate image: `plantuml docs/diagrams/use-case.puml`
  - Main actors: Learner, Teacher, Admin. Core use cases include registration/login, course discovery and enrollment, viewing lessons, taking quizzes, managing courses and users, and AI chatbot assistance.
- A.2. User Stories
  - Admin
    - Manage users (create/lock/delete) for system security.
    - Manage system-wide enrollments to resolve issues.
    - View audit logs and adjust configurations.
  - Teacher
    - Create/update courses and lessons.
    - Upload materials and create/grade quizzes.
    - View class reports and send announcements.
  - Learner
    - Register/login and manage profile.
    - Search, view, and enroll in courses and lessons.
    - Take quizzes, track progress, and use AI chatbot help.
- A.3. Context Diagram
  - Source: `docs/diagrams/context.puml` (PlantUML)
  - Generate image: `plantuml docs/diagrams/context.puml`
  - System boundary: Flask REST API + HTML/CSS/JS UI; external systems include Database (MySQL/SQLite), Email/OTP server, and AI API service.

**SECTION B – QUALITY ANALYSIS & EVALUATION**
- B.1. Table of Quality Attributes
  1) Usability — Simple interface for beginners; actions ≤ 3 s; ≥ 60% first-use comprehension.
  2) Performance — Response ≤ 5 s; video ≤ 4 s; stable with 1000 concurrents.
  3) Security — JWT + optional 2FA + Google OAuth; 100% unauthorized blocked.
  4) Reliability — Prevent data loss; restore ≤ 5 s after reconnect.
  5) Scalability — Add new course with <10% backend changes.
  6) Availability — Uptime ≥ 99% during 7:00–22:00.

- B.2. Quality Scenarios
  1) Lesson access loads in ≤ 5 s; video buffer ≤ 4 s.
  2) Restricted content denied with HTTP 403; ≤ 2 s; audited.
  3) Quiz autosave; data loss ≤ 1 question; auto-resubmit ≤ 5 s.
  4) ≥ 200 concurrent learners; CPU < 85%; ≤ 3 s; no crash.
  5) Restart downtime ≤ 10 s; session restored.
  6) Admin actions validated, logged, and recoverable (≤ 30 s).
  7) 100 MB upload ≤ 2 min; responsive UI; compression OK.
  8) Placement scoring ≤ 10 s; ≥ 95% accuracy.
  9) AI reply ≤ 6 s; ≥ 90% accuracy; 0 timeouts.

- B.3. Use ↔ Quality Attribute Matrix (legend: ✓✓ core; ✓ relevant; – not primary)
  Register/Login: Usability ✓, Performance ✓, Security ✓✓, Availability ✓
  Profile/Password: Usability ✓, Security ✓✓, Reliability ✓, Availability ✓
  Search/View Courses: Usability ✓✓, Performance ✓, Scalability ✓, Availability ✓
  View Course Details: Usability ✓✓, Performance ✓, Scalability ✓, Availability ✓
  Enroll: Usability ✓, Performance ✓, Security ✓, Scalability ✓, Availability ✓
  Validation: Security ✓✓, Reliability ✓, Availability ✓
  View Lesson: Usability ✓✓, Performance ✓, Security ✓, Reliability ✓, Scalability ✓, Availability ✓
  Preview/Notifications: Usability ✓, Performance ✓, Scalability ✓, Availability ✓
  Take Quiz: Usability ✓, Performance ✓, Security ✓, Reliability ✓✓, Availability ✓
  Track Progress: Usability ✓, Performance ✓, Reliability ✓, Scalability ✓, Availability ✓
  AI Chatbot (+ Assistance): Usability ✓, Performance ✓, Security ✓ (rate-limit/token), Scalability ✓, Availability ✓
  Announcements/Send: Performance ✓, Security ✓ (role-based), Scalability ✓, Availability ✓
  Manage Subscribers/Enrollments: Performance ✓, Security ✓✓, Reliability ✓, Scalability ✓, Availability ✓
  View Reports: Usability ✓, Performance ✓, Security ✓, Reliability ✓, Scalability ✓, Availability ✓
  Manage Course/Quiz: Performance ✓, Security ✓✓, Reliability ✓, Scalability ✓, Availability ✓
  Create/Edit/Grade Quiz: Performance ✓, Security ✓, Reliability ✓, Scalability ✓, Availability ✓
  Upload Materials: Usability ✓, Performance ✓, Reliability ✓, Scalability ✓, Availability ✓
  Manage Users: Performance ✓, Security ✓✓, Reliability ✓, Scalability ✓, Availability ✓
  Audit/Config: Security ✓✓, Reliability ✓, Scalability ✓, Availability ✓

**SECTION C – CONSTRAINTS**
- Business: 2-month timeline; scope limited to “Basic IT”; 3-member team; beginners-focused UI; non-commercial; small demo datasets; privacy protection.
- Technical: Frontend HTML/CSS/JS; Flask REST API; MySQL/SQLite; basic chatbot/FAQ; JWT + RBAC; localhost/Render/Railway; lesson ≤ 3 s, chatbot ≤ 5 s; backups; HTTPS in real deploys.

Implementation follows MVC: models in `be/models/`, controllers in `be/controllers/`, and thin blueprints in `be/routes/`. RBAC is enforced on teacher endpoints via JWT claims.
