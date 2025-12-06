import { apiGet, apiPost, API_BASE } from './apiConfig.js';

// Progress
export async function getProgress() {
  return apiGet('/student/progress');
}

// Announcements
export async function getAnnouncements(courseId) {
  const url = courseId ? `/student/announcements?course_id=${courseId}` : '/student/announcements';
  return apiGet(url);
}

// Courses & Lessons
export async function getCourseDetail(courseId) {
  return apiGet(`/student/course-detail/${courseId}`);
}

export async function getLessonDetail(lessonId) {
  return apiGet(`/student/lesson/${lessonId}`);
}

// Quizzes
export async function listCourseQuizzes(courseId) {
  return apiGet(`/student/courses/${courseId}/quizzes`);
}

export async function listLessonQuizzes(lessonId) {
  return apiGet(`/student/lessons/${lessonId}/quizzes`);
}

export async function getQuiz(quizId) {
  return apiGet(`/student/quizzes/${quizId}`);
}

export async function submitQuiz(quizId, answers) {
  return apiPost(`/student/quizzes/${quizId}/submit`, { answers });
}

export async function getQuizHistory() {
  return apiGet('/student/quizzes/results');
}

// Get student dashboard stats
export async function getStudentStats() {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      return { courses: 0, lessons: 0, quizzes: 0, avgScore: '0%', progressData: [] };
    }
    
    // Get progress
    const progressRes = await fetch(`${API_BASE}/student/progress`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const progress = progressRes.ok ? await progressRes.json() : [];
    
    // Get quiz results
    const quizRes = await fetch(`${API_BASE}/student/quizzes/results`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const quizResults = quizRes.ok ? await quizRes.json() : [];
    
    // Calculate stats
    const totalCourses = progress.length || 0;
    const totalLessons = progress.reduce((sum, p) => sum + (p.lessons_completed || 0), 0);
    const totalQuizzes = quizResults.length || 0;
    const avgScore = quizResults.length > 0 
      ? Math.round(quizResults.reduce((sum, r) => sum + (parseFloat(r.score) || 0), 0) / quizResults.length)
      : 0;
    
    return {
      courses: totalCourses,
      lessons: totalLessons,
      quizzes: totalQuizzes,
      avgScore: avgScore + '%',
      progressData: progress
    };
  } catch (error) {
    console.error('Failed to load student stats:', error);
    return {
      courses: 0,
      lessons: 0,
      quizzes: 0,
      avgScore: '0%',
      progressData: []
    };
  }
}
