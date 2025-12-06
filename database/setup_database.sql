USE [master]
GO

/****** Object:  Database [ELearningDB]    Script Date: 11/30/2025 2:39:54 AM ******/
CREATE DATABASE [ELearningDB]
 CONTAINMENT = NONE
 ON  PRIMARY 
( NAME = N'ELearningDB', FILENAME = N'C:\Program Files\Microsoft SQL Server\MSSQL16.SQLEXPRESS\MSSQL\DATA\ELearningDB.mdf' , SIZE = 8192KB , MAXSIZE = UNLIMITED, FILEGROWTH = 65536KB )
 LOG ON 
( NAME = N'ELearningDB_log', FILENAME = N'C:\Program Files\Microsoft SQL Server\MSSQL16.SQLEXPRESS\MSSQL\DATA\ELearningDB_log.ldf' , SIZE = 8192KB , MAXSIZE = 2048GB , FILEGROWTH = 65536KB )
 WITH CATALOG_COLLATION = DATABASE_DEFAULT, LEDGER = OFF
GO

ALTER DATABASE [ELearningDB] SET COMPATIBILITY_LEVEL = 160
GO

IF (1 = FULLTEXTSERVICEPROPERTY('IsFullTextInstalled'))
begin
EXEC [ELearningDB].[dbo].[sp_fulltext_database] @action = 'enable'
end
GO

ALTER DATABASE [ELearningDB] SET ANSI_NULL_DEFAULT OFF 
GO

ALTER DATABASE [ELearningDB] SET ANSI_NULLS OFF 
GO

ALTER DATABASE [ELearningDB] SET ANSI_PADDING OFF 
GO

ALTER DATABASE [ELearningDB] SET ANSI_WARNINGS OFF 
GO

ALTER DATABASE [ELearningDB] SET ARITHABORT OFF 
GO

ALTER DATABASE [ELearningDB] SET AUTO_CLOSE ON 
GO

ALTER DATABASE [ELearningDB] SET AUTO_SHRINK OFF 
GO

ALTER DATABASE [ELearningDB] SET AUTO_UPDATE_STATISTICS ON 
GO

ALTER DATABASE [ELearningDB] SET CURSOR_CLOSE_ON_COMMIT OFF 
GO

ALTER DATABASE [ELearningDB] SET CURSOR_DEFAULT  GLOBAL 
GO

ALTER DATABASE [ELearningDB] SET CONCAT_NULL_YIELDS_NULL OFF 
GO

ALTER DATABASE [ELearningDB] SET NUMERIC_ROUNDABORT OFF 
GO

ALTER DATABASE [ELearningDB] SET QUOTED_IDENTIFIER OFF 
GO

ALTER DATABASE [ELearningDB] SET RECURSIVE_TRIGGERS OFF 
GO

ALTER DATABASE [ELearningDB] SET  ENABLE_BROKER 
GO

ALTER DATABASE [ELearningDB] SET AUTO_UPDATE_STATISTICS_ASYNC OFF 
GO

ALTER DATABASE [ELearningDB] SET DATE_CORRELATION_OPTIMIZATION OFF 
GO

ALTER DATABASE [ELearningDB] SET TRUSTWORTHY OFF 
GO

ALTER DATABASE [ELearningDB] SET ALLOW_SNAPSHOT_ISOLATION OFF 
GO

ALTER DATABASE [ELearningDB] SET PARAMETERIZATION SIMPLE 
GO

ALTER DATABASE [ELearningDB] SET READ_COMMITTED_SNAPSHOT OFF 
GO

ALTER DATABASE [ELearningDB] SET HONOR_BROKER_PRIORITY OFF 
GO

ALTER DATABASE [ELearningDB] SET RECOVERY SIMPLE 
GO

ALTER DATABASE [ELearningDB] SET  MULTI_USER 
GO

ALTER DATABASE [ELearningDB] SET PAGE_VERIFY CHECKSUM  
GO

ALTER DATABASE [ELearningDB] SET DB_CHAINING OFF 
GO

ALTER DATABASE [ELearningDB] SET FILESTREAM( NON_TRANSACTED_ACCESS = OFF ) 
GO

ALTER DATABASE [ELearningDB] SET TARGET_RECOVERY_TIME = 60 SECONDS 
GO

ALTER DATABASE [ELearningDB] SET DELAYED_DURABILITY = DISABLED 
GO

ALTER DATABASE [ELearningDB] SET ACCELERATED_DATABASE_RECOVERY = OFF  
GO

ALTER DATABASE [ELearningDB] SET QUERY_STORE = ON
GO

ALTER DATABASE [ELearningDB] SET QUERY_STORE (OPERATION_MODE = READ_WRITE, CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = 30), DATA_FLUSH_INTERVAL_SECONDS = 900, INTERVAL_LENGTH_MINUTES = 60, MAX_STORAGE_SIZE_MB = 1000, QUERY_CAPTURE_MODE = AUTO, SIZE_BASED_CLEANUP_MODE = AUTO, MAX_PLANS_PER_QUERY = 200, WAIT_STATS_CAPTURE_MODE = ON)
GO

USE [ELearningDB]
GO

/****** Object:  Table [dbo].[Users]    Script Date: 11/30/2025 2:39:54 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Users](
	[UserID] [int] IDENTITY(1,1) NOT NULL,
	[FullName] [nvarchar](100) NOT NULL,
	[Email] [nvarchar](100) NOT NULL,
	[PasswordHash] [nvarchar](255) NOT NULL,
	[Role] [nvarchar](20) NOT NULL,
	[TwoFAEnabled] [bit] NULL,
	[AvatarUrl] [nvarchar](255) NULL,
	[CreatedAt] [datetime] NULL,
	[UpdatedAt] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[UserID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[Email] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

/****** Object:  Table [dbo].[Courses]    Script Date: 11/30/2025 2:39:54 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Courses](
	[CourseID] [int] IDENTITY(1,1) NOT NULL,
	[Title] [nvarchar](150) NOT NULL,
	[Description] [nvarchar](max) NULL,
	[Category] [nvarchar](50) NULL,
	[Duration] [int] NULL,
	[TeacherID] [int] NOT NULL,
	[Status] [nvarchar](20) NULL,
	[CreatedAt] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[CourseID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO

/****** Object:  Table [dbo].[Lessons]    Script Date: 11/30/2025 2:39:54 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Lessons](
	[LessonID] [int] IDENTITY(1,1) NOT NULL,
	[CourseID] [int] NOT NULL,
	[Title] [nvarchar](150) NOT NULL,
	[VideoUrl] [nvarchar](255) NULL,
	[FileUrl] [nvarchar](255) NULL,
	[Description] [nvarchar](max) NULL,
	[OrderIndex] [int] NULL,
	[CreatedAt] [datetime] NULL,
	[Content] [nvarchar](max) NULL,
PRIMARY KEY CLUSTERED 
(
	[LessonID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO

/****** Object:  Table [dbo].[Quizzes]    Script Date: 11/30/2025 2:39:54 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Quizzes](
	[QuizID] [int] IDENTITY(1,1) NOT NULL,
	[CourseID] [int] NOT NULL,
	[Title] [nvarchar](150) NOT NULL,
	[Description] [nvarchar](max) NULL,
	[TotalQuestions] [int] NULL,
	[TimeLimit] [int] NULL,
	[CreatedAt] [datetime] NULL,
	[LessonID] [int] NULL,
PRIMARY KEY CLUSTERED 
(
	[QuizID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO

/****** Object:  Table [dbo].[QuizQuestions]    Script Date: 11/30/2025 2:39:54 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[QuizQuestions](
	[QuestionID] [int] IDENTITY(1,1) NOT NULL,
	[QuizID] [int] NOT NULL,
	[QuestionText] [nvarchar](max) NOT NULL,
	[OptionA] [nvarchar](255) NULL,
	[OptionB] [nvarchar](255) NULL,
	[OptionC] [nvarchar](255) NULL,
	[OptionD] [nvarchar](255) NULL,
	[CorrectOption] [char](1) NULL,
PRIMARY KEY CLUSTERED 
(
	[QuestionID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO

/****** Object:  Table [dbo].[QuizResults]    Script Date: 11/30/2025 2:39:54 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[QuizResults](
	[ResultID] [int] IDENTITY(1,1) NOT NULL,
	[QuizID] [int] NOT NULL,
	[UserID] [int] NOT NULL,
	[Score] [decimal](5, 2) NULL,
	[SubmittedAt] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[ResultID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

/****** Object:  Table [dbo].[Enrollments]    Script Date: 11/30/2025 2:39:54 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Enrollments](
	[EnrollmentID] [int] IDENTITY(1,1) NOT NULL,
	[UserID] [int] NOT NULL,
	[CourseID] [int] NOT NULL,
	[Status] [nvarchar](20) NULL,
	[PaymentStatus] [nvarchar](20) NULL,
	[EnrolledDate] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[EnrollmentID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

/****** Object:  Table [dbo].[Progress]    Script Date: 11/30/2025 2:39:54 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Progress](
	[ProgressID] [int] IDENTITY(1,1) NOT NULL,
	[UserID] [int] NOT NULL,
	[CourseID] [int] NOT NULL,
	[LessonsCompleted] [int] NULL,
	[TotalLessons] [int] NULL,
	[ProgressPercent]  AS (case when [TotalLessons]=(0) then (0) else ([LessonsCompleted]*(100))/[TotalLessons] end),
	[LastUpdated] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[ProgressID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

/****** Object:  Table [dbo].[Announcements]    Script Date: 11/30/2025 2:39:54 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Announcements](
	[AnnouncementID] [int] IDENTITY(1,1) NOT NULL,
	[CourseID] [int] NOT NULL,
	[TeacherID] [int] NOT NULL,
	[Title] [nvarchar](200) NULL,
	[Message] [nvarchar](max) NULL,
	[CreatedAt] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[AnnouncementID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO

/****** Object:  Table [dbo].[AuditLogs]    Script Date: 11/30/2025 2:39:54 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[AuditLogs](
	[LogID] [int] IDENTITY(1,1) NOT NULL,
	[AdminID] [int] NOT NULL,
	[Action] [nvarchar](100) NULL,
	[Target] [nvarchar](100) NULL,
	[Description] [nvarchar](max) NULL,
	[Timestamp] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[LogID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO

/****** Object:  Table [dbo].[ChatbotHistory]    Script Date: 11/30/2025 2:39:54 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[ChatbotHistory](
	[ChatID] [int] IDENTITY(1,1) NOT NULL,
	[UserID] [int] NOT NULL,
	[Question] [nvarchar](max) NULL,
	[Answer] [nvarchar](max) NULL,
	[CreatedAt] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[ChatID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO

/****** Object:  Table [dbo].[PlacementTests]    Script Date: 11/30/2025 2:39:54 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[PlacementTests](
	[TestID] [int] IDENTITY(1,1) NOT NULL,
	[UserID] [int] NOT NULL,
	[Score] [decimal](5, 2) NULL,
	[RecommendedLevel] [nvarchar](50) NULL,
	[TakenAt] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[TestID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- Add Default Constraints
ALTER TABLE [dbo].[Users] ADD  DEFAULT ('student') FOR [Role]
GO

ALTER TABLE [dbo].[Users] ADD  DEFAULT ((0)) FOR [TwoFAEnabled]
GO

ALTER TABLE [dbo].[Users] ADD  DEFAULT (getdate()) FOR [CreatedAt]
GO

ALTER TABLE [dbo].[Courses] ADD  DEFAULT ('active') FOR [Status]
GO

ALTER TABLE [dbo].[Courses] ADD  DEFAULT (getdate()) FOR [CreatedAt]
GO

ALTER TABLE [dbo].[Lessons] ADD  DEFAULT ((1)) FOR [OrderIndex]
GO

ALTER TABLE [dbo].[Lessons] ADD  DEFAULT (getdate()) FOR [CreatedAt]
GO

ALTER TABLE [dbo].[Quizzes] ADD  DEFAULT ((0)) FOR [TotalQuestions]
GO

ALTER TABLE [dbo].[Quizzes] ADD  DEFAULT (getdate()) FOR [CreatedAt]
GO

ALTER TABLE [dbo].[QuizResults] ADD  DEFAULT (getdate()) FOR [SubmittedAt]
GO

ALTER TABLE [dbo].[Enrollments] ADD  DEFAULT ('pending') FOR [Status]
GO

ALTER TABLE [dbo].[Enrollments] ADD  DEFAULT ('unpaid') FOR [PaymentStatus]
GO

ALTER TABLE [dbo].[Enrollments] ADD  DEFAULT (getdate()) FOR [EnrolledDate]
GO

ALTER TABLE [dbo].[Progress] ADD  DEFAULT ((0)) FOR [LessonsCompleted]
GO

ALTER TABLE [dbo].[Progress] ADD  DEFAULT ((0)) FOR [TotalLessons]
GO

ALTER TABLE [dbo].[Progress] ADD  DEFAULT (getdate()) FOR [LastUpdated]
GO

ALTER TABLE [dbo].[Announcements] ADD  DEFAULT (getdate()) FOR [CreatedAt]
GO

ALTER TABLE [dbo].[AuditLogs] ADD  DEFAULT (getdate()) FOR [Timestamp]
GO

ALTER TABLE [dbo].[ChatbotHistory] ADD  DEFAULT (getdate()) FOR [CreatedAt]
GO

ALTER TABLE [dbo].[PlacementTests] ADD  DEFAULT (getdate()) FOR [TakenAt]
GO

-- Add Foreign Key Constraints
ALTER TABLE [dbo].[Courses]  WITH CHECK ADD FOREIGN KEY([TeacherID])
REFERENCES [dbo].[Users] ([UserID])
ON UPDATE CASCADE
ON DELETE CASCADE
GO

ALTER TABLE [dbo].[Lessons]  WITH CHECK ADD FOREIGN KEY([CourseID])
REFERENCES [dbo].[Courses] ([CourseID])
ON UPDATE CASCADE
ON DELETE CASCADE
GO

ALTER TABLE [dbo].[Quizzes]  WITH CHECK ADD FOREIGN KEY([CourseID])
REFERENCES [dbo].[Courses] ([CourseID])
ON UPDATE CASCADE
ON DELETE CASCADE
GO

ALTER TABLE [dbo].[Quizzes]  WITH CHECK ADD  CONSTRAINT [FK_Quizzes_Lessons] FOREIGN KEY([LessonID])
REFERENCES [dbo].[Lessons] ([LessonID])
GO

ALTER TABLE [dbo].[Quizzes] CHECK CONSTRAINT [FK_Quizzes_Lessons]
GO

ALTER TABLE [dbo].[QuizQuestions]  WITH CHECK ADD FOREIGN KEY([QuizID])
REFERENCES [dbo].[Quizzes] ([QuizID])
ON UPDATE CASCADE
ON DELETE CASCADE
GO

ALTER TABLE [dbo].[QuizResults]  WITH CHECK ADD FOREIGN KEY([QuizID])
REFERENCES [dbo].[Quizzes] ([QuizID])
GO

ALTER TABLE [dbo].[QuizResults]  WITH CHECK ADD FOREIGN KEY([UserID])
REFERENCES [dbo].[Users] ([UserID])
GO

ALTER TABLE [dbo].[Enrollments]  WITH CHECK ADD FOREIGN KEY([CourseID])
REFERENCES [dbo].[Courses] ([CourseID])
GO

ALTER TABLE [dbo].[Enrollments]  WITH CHECK ADD FOREIGN KEY([UserID])
REFERENCES [dbo].[Users] ([UserID])
GO

ALTER TABLE [dbo].[Progress]  WITH CHECK ADD FOREIGN KEY([CourseID])
REFERENCES [dbo].[Courses] ([CourseID])
GO

ALTER TABLE [dbo].[Progress]  WITH CHECK ADD FOREIGN KEY([UserID])
REFERENCES [dbo].[Users] ([UserID])
GO

ALTER TABLE [dbo].[Announcements]  WITH CHECK ADD FOREIGN KEY([CourseID])
REFERENCES [dbo].[Courses] ([CourseID])
GO

ALTER TABLE [dbo].[Announcements]  WITH CHECK ADD FOREIGN KEY([TeacherID])
REFERENCES [dbo].[Users] ([UserID])
GO

ALTER TABLE [dbo].[AuditLogs]  WITH CHECK ADD FOREIGN KEY([AdminID])
REFERENCES [dbo].[Users] ([UserID])
ON UPDATE CASCADE
ON DELETE CASCADE
GO

ALTER TABLE [dbo].[ChatbotHistory]  WITH CHECK ADD FOREIGN KEY([UserID])
REFERENCES [dbo].[Users] ([UserID])
ON UPDATE CASCADE
ON DELETE CASCADE
GO

ALTER TABLE [dbo].[PlacementTests]  WITH CHECK ADD FOREIGN KEY([UserID])
REFERENCES [dbo].[Users] ([UserID])
ON UPDATE CASCADE
ON DELETE CASCADE
GO

-- Add Check Constraints
ALTER TABLE [dbo].[Users]  WITH CHECK ADD CHECK  (([Role]='admin' OR [Role]='teacher' OR [Role]='student'))
GO

ALTER TABLE [dbo].[Enrollments]  WITH CHECK ADD CHECK  (([Status]='rejected' OR [Status]='approved' OR [Status]='pending'))
GO

ALTER TABLE [dbo].[QuizQuestions]  WITH CHECK ADD CHECK  (([CorrectOption]='D' OR [CorrectOption]='C' OR [CorrectOption]='B' OR [CorrectOption]='A'))
GO

USE [master]
GO

ALTER DATABASE [ELearningDB] SET  READ_WRITE 
GO
