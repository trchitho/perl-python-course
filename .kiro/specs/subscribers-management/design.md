# Design Document: Subscribers Management

## Overview

The Subscribers Management feature provides teachers with a comprehensive interface to manage student enrollments in their courses. The system consists of a React-based frontend page and Flask backend API endpoints that enable teachers to view, approve, reject, and remove student enrollments, as well as view detailed student progress information including quiz results and lesson completion.

The feature integrates with the existing enrollment, progress, and quiz results systems, providing a unified view of student engagement and performance within each course.

## Architecture

### System Components

The Subscribers Management feature follows the existing three-tier architecture:

1. **Presentation Layer**: React component (`SubscribersPage.jsx`) using Material-UI
2. **API Layer**: Flask Blueprint routes in `teacher_view.py`
3. **Business Logic Layer**: Controller functions in `teacher_controller.py`
4. **Data Access Layer**: SQLAlchemy ORM models (Enrollment, Progress, QuizResult, User)

### Data Flow

```
User Action (Frontend)
    ↓
API Request (HTTP)
    ↓
Flask Route (teacher_view.py)
    ↓
JWT Authentication & Authorization
    ↓
Controller Function (teacher_controller.py)
    ↓
Database Query (SQLAlchemy ORM)
    ↓
Response (JSON)
    ↓
Frontend State Update
    ↓
UI Re-render
```

## Components and Interfaces

### Frontend Component

**SubscribersPage.jsx**

A React functional component that provides the user interface for managing course subscribers.

**State Management:**
- `enrollments`: Array of enrollment objects
- `loading`: Boolean for loading state
- `error`: String for error messages
- `success`: String for success messages
- `selectedStudent`: Object for student detail view
- `statusFilter`: String ('all', 'pending', 'approved', 'rejected')
- `searchQuery`: String for search functionality
- `statistics`: Object containing enrollment statistics
- `studentProgress`: Object containing detailed student progress data
- `openProgressDialog`: Boolean for progress dialog visibility

**Key Functions:**
- `loadEnrollments()`: Fetches enrollment list from API
- `loadStatistics()`: Fetches enrollment statistics
- `handleApprove(enrollmentId)`: Approves a pending enrollment
- `handleReject(enrollmentId)`: Rejects a pending enrollment
- `handleRemove(enrollmentId)`: Removes an enrollment
- `handleViewProgress(studentId, courseId)`: Opens student progress dialog
- `loadStudentProgress(studentId, courseId)`: Fetches detailed progress data
- `filterEnrollments()`: Filters enrollments by status and search query

### Backend API Endpoints

**Existing Endpoints (already implemented):**
- `GET /api/teacher/courses/<course_id>/subscribers` - List all enrollments for a course
- `POST /api/teacher/subscribers/<enroll_id>/approve` - Approve an enrollment
- `DELETE /api/teacher/subscribers/<enroll_id>` - Remove an enrollment

**New Endpoints (to be implemented):**
- `POST /api/teacher/subscribers/<enroll_id>/reject` - Reject an enrollment
- `GET /api/teacher/subscribers/<enroll_id>/progress` - Get detailed student progress
- `GET /api/teacher/courses/<course_id>/subscribers/stats` - Get enrollment statistics

### Backend Controller Functions

**Existing Functions:**
- `list_subscribers(course_id)`: Returns list of enrollments with student info
- `approve_subscriber(enroll_id)`: Updates enrollment status to 'approved'
- `remove_subscriber(enroll_id)`: Deletes enrollment record

**New Functions:**
- `reject_subscriber(enroll_id)`: Updates enrollment status to 'rejected'
- `get_subscriber_progress(enroll_id)`: Returns detailed progress and quiz results
- `get_subscribers_statistics(course_id)`: Returns enrollment statistics

## Data Models

### Enrollment Model (existing)

```python
class Enrollment(db.Model):
    __tablename__ = 'Enrollments'
    id = db.Column('EnrollmentID', db.Integer, primary_key=True)
    student_id = db.Column('UserID', db.Integer, db.ForeignKey('Users.UserID'))
    course_id = db.Column('CourseID', db.Integer, db.ForeignKey('Courses.CourseID'))
    status = db.Column('Status', db.String(20), default='pending')
    payment_status = db.Column('PaymentStatus', db.String(20), default='unpaid')
    enrolled_at = db.Column('EnrolledDate', db.DateTime, default=datetime.utcnow)
    
    student = db.relationship('User', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')
```

### Progress Model (existing)

```python
class Progress(db.Model):
    __tablename__ = 'Progress'
    id = db.Column('ProgressID', db.Integer, primary_key=True)
    student_id = db.Column('UserID', db.Integer, db.ForeignKey('Users.UserID'))
    course_id = db.Column('CourseID', db.Integer, db.ForeignKey('Courses.CourseID'))
    lessons_completed = db.Column('LessonsCompleted', db.Integer, default=0)
    total_lessons = db.Column('TotalLessons', db.Integer, default=0)
    progress_percent = db.Column('ProgressPercent', db.Integer)
    last_updated = db.Column('LastUpdated', db.DateTime, default=datetime.utcnow)
```

### QuizResult Model (existing)

```python
class QuizResult(db.Model):
    __tablename__ = 'QuizResults'
    id = db.Column('ResultID', db.Integer, primary_key=True)
    quiz_id = db.Column('QuizID', db.Integer, db.ForeignKey('Quizzes.QuizID'))
    user_id = db.Column('UserID', db.Integer, db.ForeignKey('Users.UserID'))
    score = db.Column('Score', db.Numeric(5, 2))
    submitted_at = db.Column('SubmittedAt', db.DateTime, default=datetime.utcnow)
    
    quiz = db.relationship('Quiz')
    user = db.relationship('User')
```

### API Response Formats

**Enrollment List Response:**
```json
[
  {
    "id": 1,
    "user_id": 5,
    "fullname": "Nguyen Van A",
    "email": "student@example.com",
    "status": "pending",
    "payment_status": "unpaid",
    "enrolled_date": "2025-12-01T10:30:00"
  }
]
```

**Statistics Response:**
```json
{
  "total": 50,
  "pending": 5,
  "approved": 40,
  "rejected": 5,
  "average_score": 85.5
}
```

**Student Progress Response:**
```json
{
  "student_id": 5,
  "student_name": "Nguyen Van A",
  "course_id": 10,
  "lessons_completed": 8,
  "total_lessons": 12,
  "progress_percent": 67,
  "quiz_results": [
    {
      "quiz_id": 1,
      "quiz_title": "Introduction Quiz",
      "score": 90.0,
      "submitted_at": "2025-12-01T14:30:00"
    }
  ],
  "average_score": 85.5
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Teacher authorization for enrollment operations

*For any* enrollment operation (view, approve, reject, remove), the system should only allow the operation if the enrollment's course is owned by the requesting teacher.
**Validates: Requirements 1.3, 2.4, 3.4, 4.4**

### Property 2: Enrollment status transitions

*For any* enrollment, when the status is changed from 'pending' to 'approved' or 'rejected', the database should persist the new status and subsequent queries should return the updated status.
**Validates: Requirements 2.2, 2.3, 3.3**

### Property 3: Enrollment deletion completeness

*For any* enrollment that is deleted, subsequent queries for that enrollment should return a 404 error or empty result.
**Validates: Requirements 4.3**

### Property 4: Progress calculation accuracy

*For any* student in a course, the progress percentage should equal (lessons_completed / total_lessons) * 100 when total_lessons > 0, and 0 when total_lessons = 0.
**Validates: Requirements 5.5**

### Property 5: Status filter correctness

*For any* status filter value ('pending', 'approved', 'rejected'), the filtered enrollment list should contain only enrollments with that exact status value.
**Validates: Requirements 6.3, 6.4, 6.5**

### Property 6: Search filter case-insensitivity

*For any* search query string, the filtered results should include all enrollments where the student name or email contains the query string, regardless of case differences between the query and the stored values.
**Validates: Requirements 7.3**

### Property 7: Statistics accuracy

*For any* course, the sum of pending, approved, and rejected counts in the statistics should equal the total enrollment count.
**Validates: Requirements 8.1, 8.2**

### Property 8: Empty state handling

*For any* course with zero enrollments, the system should display appropriate empty state messages and return zero for all statistics.
**Validates: Requirements 1.4, 5.4, 8.4**

## Error Handling

### Frontend Error Handling

1. **Network Errors**: Display user-friendly error messages in Alert components
2. **Authentication Errors**: Redirect to login page if token is invalid
3. **Authorization Errors**: Display "Permission denied" message
4. **Validation Errors**: Show inline validation messages for form inputs
5. **Loading States**: Display CircularProgress indicators during API calls

### Backend Error Handling

1. **404 Not Found**: Return when enrollment, course, or student doesn't exist
2. **403 Forbidden**: Return when teacher doesn't own the course
3. **400 Bad Request**: Return for invalid input data
4. **500 Internal Server Error**: Log error details and return generic error message

### Error Response Format

```json
{
  "error": "Error message description"
}
```

## Testing Strategy

### Unit Testing

Unit tests will verify specific examples and edge cases:

1. **Authorization Tests**:
   - Test that teachers can only access their own courses' enrollments
   - Test that non-teachers cannot access teacher endpoints
   - Test that accessing non-existent enrollments returns 404

2. **Status Transition Tests**:
   - Test approving a pending enrollment
   - Test rejecting a pending enrollment
   - Test that approved/rejected enrollments cannot be re-approved

3. **Progress Calculation Tests**:
   - Test progress calculation with various lesson counts
   - Test progress calculation when total_lessons is 0
   - Test progress calculation with partial completion

4. **Filter Tests**:
   - Test filtering by each status value
   - Test search with exact matches
   - Test search with partial matches
   - Test search with no matches

### Property-Based Testing

Property-based tests will verify universal properties across all inputs using the **Hypothesis** library for Python:

1. **Property 1 Test**: Generate random teacher IDs and course IDs, verify authorization checks work correctly
2. **Property 2 Test**: Generate random enrollments, change status, verify persistence
3. **Property 3 Test**: Generate random enrollments, delete them, verify they're gone
4. **Property 4 Test**: Generate random progress data, verify calculation formula
5. **Property 5 Test**: Generate random enrollment lists with various statuses, verify filtering
6. **Property 6 Test**: Generate random search queries with various cases, verify case-insensitive matching
7. **Property 7 Test**: Generate random enrollment data, verify statistics sum correctly
8. **Property 8 Test**: Test with empty enrollment lists, verify zero values and empty messages

### Integration Testing

Integration tests will verify the complete flow from frontend to database:

1. Test complete enrollment approval workflow
2. Test complete enrollment rejection workflow
3. Test complete enrollment removal workflow
4. Test student progress data retrieval
5. Test statistics calculation with real database data

### Frontend Testing

Frontend tests using React Testing Library:

1. Test component rendering with various data states
2. Test user interactions (button clicks, form submissions)
3. Test dialog open/close behavior
4. Test filter and search functionality
5. Test error and success message display

## Implementation Notes

### Vietnamese Text Support

All text fields (student names, course names) must use NVARCHAR columns in the database to support Vietnamese characters. The existing `database_types.py` custom SQLAlchemy types should be used to ensure proper encoding.

### Performance Considerations

1. **Eager Loading**: Use `db.joinedload()` to load related student data in a single query
2. **Pagination**: For courses with many enrollments, implement pagination (future enhancement)
3. **Caching**: Consider caching statistics data for frequently accessed courses
4. **Indexing**: Ensure database indexes exist on foreign keys (student_id, course_id)

### Security Considerations

1. **JWT Authentication**: All endpoints require valid JWT token
2. **Role-Based Access**: Only teachers and admins can access these endpoints
3. **Course Ownership**: Verify teacher owns the course before any operation
4. **SQL Injection Prevention**: Use SQLAlchemy ORM parameterized queries
5. **XSS Prevention**: React automatically escapes rendered content

### UI/UX Considerations

1. **Confirmation Dialogs**: Show confirmation before destructive actions (reject, remove)
2. **Loading States**: Show loading indicators during API calls
3. **Empty States**: Show helpful messages when no data exists
4. **Responsive Design**: Use Material-UI responsive components
5. **Accessibility**: Ensure proper ARIA labels and keyboard navigation
6. **Vietnamese Language**: Support Vietnamese text in all UI elements
