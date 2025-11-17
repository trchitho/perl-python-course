-- SQL Server
ALTER TABLE [dbo].[Quizzes]
ADD [LessonID] INT NULL;

ALTER TABLE [dbo].[Quizzes]
ADD CONSTRAINT FK_Quizzes_Lessons
FOREIGN KEY ([LessonID]) REFERENCES [dbo].[Lessons]([LessonID]);

-- Optional: backfill LessonID manually per quiz before enforcing NOT NULL if desired.

GO

-- SQLite / generic
-- PRAGMA foreign_keys=off;
-- CREATE TABLE IF NOT EXISTS quizzes_new AS
--   SELECT id, course_id, NULL as lesson_id, title, description, total_questions, time_limit, created_at
--   FROM quizzes;
-- DROP TABLE quizzes;
-- ALTER TABLE quizzes_new RENAME TO quizzes;
-- PRAGMA foreign_keys=on;
