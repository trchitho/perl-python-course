import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import Layout from "./components/Layout";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import ResetPasswordPage from "./pages/ResetPasswordPage";
import GoogleCallbackPage from "./pages/GoogleCallbackPage";
import DashboardPage from "./pages/DashboardPage";

// Admin pages
import AdminDashboardPage from "./pages/admin/DashboardPage";
import AdminCoursesPage from "./pages/admin/CoursesPage";
import EnrollmentsPage from "./pages/admin/EnrollmentsPage";
import LogsPage from "./pages/admin/LogsPage";
import SettingsPage from "./pages/admin/SettingsPage";
import UsersPage from "./pages/admin/UsersPage";

// Teacher pages
import TeacherDashboardPage from "./pages/teacher/DashboardPage";
import AnnouncementsPage from "./pages/teacher/AnnouncementsPage";
import TeacherCoursesPage from "./pages/teacher/CoursesPage";
import GradesPage from "./pages/teacher/GradesPage";
import TeacherLessonsPage from "./pages/teacher/LessonsPage";
import TeacherQuizzesPage from "./pages/teacher/QuizzesPage";
import SubscribersPage from "./pages/teacher/SubscribersPage";

// Student pages
import StudentDashboardPage from "./pages/student/DashboardPage";
import StudentAnnouncementsPage from "./pages/student/AnnouncementsPage";
import ChatbotPage from "./pages/student/ChatbotPage";
import StudentCoursesPage from "./pages/student/CoursesPage";
import CourseDetailsPage from "./pages/student/CourseDetailsPage";
import StudentLessonsPage from "./pages/student/LessonsPage";
import LessonDetailPage from "./pages/student/LessonDetailPage";
import ProfilePage from "./pages/student/ProfilePage";
import ProgressPage from "./pages/student/ProgressPage";
import QuizHistoryPage from "./pages/student/QuizHistoryPage";
import QuizPage from "./pages/student/QuizPage";
import PlacementTestPage from "./pages/student/PlacementTestPage";

import './App.css';

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      {
        index: true, // This makes HomePage the default child route for "/"
        element: <HomePage />,
      },
      {
        path: "login",
        element: <LoginPage />,
      },
      {
        path: "register",
        element: <RegisterPage />,
      },
      {
        path: "forgot-password",
        element: <ForgotPasswordPage />,
      },
      {
        path: "reset-password",
        element: <ResetPasswordPage />,
      },
      {
        path: "auth/google/callback",
        element: <GoogleCallbackPage />,
      },
      {
        path: "dashboard",
        element: <DashboardPage />,
      },
      {
        path: "admin",
        children: [
          {
            path: "dashboard",
            element: <AdminDashboardPage />,
          },
          {
            path: "courses",
            element: <AdminCoursesPage />,
          },
          {
            path: "enrollments",
            element: <EnrollmentsPage />,
          },
          {
            path: "logs",
            element: <LogsPage />,
          },
          {
            path: "settings",
            element: <SettingsPage />,
          },
          {
            path: "users",
            element: <UsersPage />,
          },
        ],
      },
      {
        path: "teacher",
        children: [
          {
            path: "dashboard",
            element: <TeacherDashboardPage />,
          },
          {
            path: "announcements",
            element: <AnnouncementsPage />,
          },
          {
            path: "courses",
            element: <TeacherCoursesPage />,
          },
          {
            path: "grades",
            element: <GradesPage />,
          },
          {
            path: "lessons",
            element: <TeacherLessonsPage />,
          },
          {
            path: "quizzes",
            element: <TeacherQuizzesPage />,
          },
          {
            path: "subscribers",
            element: <SubscribersPage />,
          },
        ],
      },
      {
        path: "student",
        children: [
          {
            path: "dashboard",
            element: <StudentDashboardPage />,
          },
          {
            path: "announcements",
            element: <StudentAnnouncementsPage />,
          },
          {
            path: "chatbot",
            element: <ChatbotPage />,
          },
          {
            path: "courses",
            element: <StudentCoursesPage />,
          },
          {
            path: "course-details",
            element: <CourseDetailsPage />,
          },
          {
            path: "lessons",
            element: <StudentLessonsPage />,
          },
          {
            path: "lesson/:lessonId",
            element: <LessonDetailPage />,
          },
          {
            path: "profile",
            element: <ProfilePage />,
          },
          {
            path: "progress",
            element: <ProgressPage />,
          },
          {
            path: "quiz-history",
            element: <QuizHistoryPage />,
          },
          {
            path: "quiz",
            element: <QuizPage />,
          },
          {
            path: "quiz/:quizId",
            element: <QuizPage />,
          },
          {
            path: "placement-test",
            element: <PlacementTestPage />,
          },
        ],
      },
    ],
  },
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;
