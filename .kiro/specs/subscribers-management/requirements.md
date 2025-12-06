# Requirements Document

## Introduction

The Subscribers Management feature enables teachers to manage student enrollments in their courses. Teachers need the ability to view all students enrolled in their courses, approve or reject enrollment requests, remove students from courses, and view detailed information about student progress. This feature is essential for maintaining course quality, managing class sizes, and ensuring only authorized students have access to course materials.

## Glossary

- **Teacher**: A user with the role of 'teacher' who creates and manages courses
- **Student**: A user with the role of 'student' who can enroll in courses
- **Enrollment**: A record representing a student's registration in a specific course
- **Enrollment Status**: The state of an enrollment (pending, approved, or rejected)
- **Payment Status**: The payment state of an enrollment (paid or unpaid)
- **Course Progress**: The percentage of lessons completed by a student in a course
- **Subscribers Management System**: The web interface and backend API for managing course enrollments
- **Quiz Result**: A record of a student's score on a quiz within a course

## Requirements

### Requirement 1

**User Story:** As a teacher, I want to view all students enrolled in my courses, so that I can see who has access to my course materials.

#### Acceptance Criteria

1. WHEN a teacher navigates to the subscribers page for a course THEN the Subscribers Management System SHALL display a list of all enrollments for that course
2. WHEN displaying enrollment information THEN the Subscribers Management System SHALL show student name, email, enrollment status, payment status, and enrollment date for each enrollment
3. WHEN a teacher views the subscribers list THEN the Subscribers Management System SHALL only display enrollments for courses owned by that teacher
4. WHEN the subscribers list is empty THEN the Subscribers Management System SHALL display a message indicating no students are enrolled
5. WHEN enrollment data is loaded THEN the Subscribers Management System SHALL order enrollments by enrollment date in descending order

### Requirement 2

**User Story:** As a teacher, I want to approve pending enrollment requests, so that students can access my course content after I verify their eligibility.

#### Acceptance Criteria

1. WHEN a teacher clicks the approve button for a pending enrollment THEN the Subscribers Management System SHALL change the enrollment status to 'approved'
2. WHEN an enrollment is approved THEN the Subscribers Management System SHALL persist the status change to the database
3. WHEN an enrollment status is updated to approved THEN the Subscribers Management System SHALL refresh the enrollment list to reflect the change
4. WHEN a teacher attempts to approve an enrollment for a course they do not own THEN the Subscribers Management System SHALL reject the request with a 403 error
5. WHEN a teacher attempts to approve a non-existent enrollment THEN the Subscribers Management System SHALL return a 404 error

### Requirement 3

**User Story:** As a teacher, I want to reject enrollment requests, so that I can prevent unauthorized students from accessing my course.

#### Acceptance Criteria

1. WHEN a teacher clicks the reject button for a pending enrollment THEN the Subscribers Management System SHALL change the enrollment status to 'rejected'
2. WHEN rejecting an enrollment THEN the Subscribers Management System SHALL prompt the teacher for confirmation before proceeding
3. WHEN an enrollment is rejected THEN the Subscribers Management System SHALL persist the status change to the database
4. WHEN a teacher attempts to reject an enrollment for a course they do not own THEN the Subscribers Management System SHALL reject the request with a 403 error

### Requirement 4

**User Story:** As a teacher, I want to remove students from my course, so that I can revoke access when necessary.

#### Acceptance Criteria

1. WHEN a teacher clicks the remove button for an enrollment THEN the Subscribers Management System SHALL prompt for confirmation before deletion
2. WHEN a teacher confirms removal THEN the Subscribers Management System SHALL delete the enrollment record from the database
3. WHEN an enrollment is deleted THEN the Subscribers Management System SHALL refresh the enrollment list to reflect the removal
4. WHEN a teacher attempts to remove an enrollment for a course they do not own THEN the Subscribers Management System SHALL reject the request with a 403 error
5. WHEN a teacher attempts to remove a non-existent enrollment THEN the Subscribers Management System SHALL handle the request gracefully

### Requirement 5

**User Story:** As a teacher, I want to view student progress details, so that I can understand how well students are performing in my course.

#### Acceptance Criteria

1. WHEN a teacher clicks on a student in the subscribers list THEN the Subscribers Management System SHALL display detailed progress information for that student
2. WHEN displaying student progress THEN the Subscribers Management System SHALL show the number of lessons completed, total lessons, and progress percentage
3. WHEN displaying student progress THEN the Subscribers Management System SHALL show all quiz results with scores and submission dates
4. WHEN a student has no progress data THEN the Subscribers Management System SHALL display zero progress and an empty quiz results list
5. WHEN calculating progress percentage THEN the Subscribers Management System SHALL compute it as (lessons completed / total lessons) * 100

### Requirement 6

**User Story:** As a teacher, I want to filter enrollments by status, so that I can quickly find pending requests or approved students.

#### Acceptance Criteria

1. WHEN a teacher selects a status filter THEN the Subscribers Management System SHALL display only enrollments matching that status
2. WHEN the status filter is set to 'all' THEN the Subscribers Management System SHALL display enrollments of all statuses
3. WHEN the status filter is set to 'pending' THEN the Subscribers Management System SHALL display only enrollments with status 'pending'
4. WHEN the status filter is set to 'approved' THEN the Subscribers Management System SHALL display only enrollments with status 'approved'
5. WHEN the status filter is set to 'rejected' THEN the Subscribers Management System SHALL display only enrollments with status 'rejected'

### Requirement 7

**User Story:** As a teacher, I want to search for students by name or email, so that I can quickly find specific students in large courses.

#### Acceptance Criteria

1. WHEN a teacher types in the search field THEN the Subscribers Management System SHALL filter the enrollment list to show only students whose name or email contains the search text
2. WHEN the search field is empty THEN the Subscribers Management System SHALL display all enrollments without filtering
3. WHEN searching THEN the Subscribers Management System SHALL perform case-insensitive matching
4. WHEN no enrollments match the search criteria THEN the Subscribers Management System SHALL display a message indicating no results found

### Requirement 8

**User Story:** As a teacher, I want to see enrollment statistics for my course, so that I can understand enrollment trends and course popularity.

#### Acceptance Criteria

1. WHEN a teacher views the subscribers page THEN the Subscribers Management System SHALL display the total number of enrollments
2. WHEN displaying enrollment statistics THEN the Subscribers Management System SHALL show counts for pending, approved, and rejected enrollments separately
3. WHEN displaying enrollment statistics THEN the Subscribers Management System SHALL show the average quiz score across all students in the course
4. WHEN no enrollments exist THEN the Subscribers Management System SHALL display zero for all statistics
