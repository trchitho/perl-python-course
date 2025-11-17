const API_BASE = 'http://127.0.0.1:5000/api';

export async function getProgress(token){
  const res = await fetch(`${API_BASE}/student/progress`, { headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Cannot fetch progress');
  return res.json();
}

export async function getNotifications(token){
  const res = await fetch(`${API_BASE}/student/announcements`, { headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Cannot fetch notifications');
  return res.json();
}

export async function getAnnouncements(token, courseId){
  const url = courseId ? `${API_BASE}/student/announcements?course_id=${courseId}` : `${API_BASE}/student/announcements`;
  const res = await fetch(url, { headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Cannot fetch announcements');
  return res.json();
}

export async function getCourseDetail(token, courseId){
  const res = await fetch(`${API_BASE}/student/course-detail/${courseId}`, { headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Cannot fetch course detail');
  return res.json();
}

export async function getLessonDetail(token, lessonId){
  const res = await fetch(`${API_BASE}/student/lesson/${lessonId}`, { headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Cannot fetch lesson');
  return res.json();
}

// Quizzes (student)
export async function listCourseQuizzes(token, courseId){
  const res = await fetch(`${API_BASE}/student/courses/${courseId}/quizzes`, { headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Cannot list quizzes');
  return res.json();
}

export async function getQuiz(token, quizId){
  const res = await fetch(`${API_BASE}/student/quizzes/${quizId}`, { headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Cannot load quiz');
  return res.json();
}

export async function submitQuiz(token, quizId, answers){
  const res = await fetch(`${API_BASE}/student/quizzes/${quizId}/submit`, { method:'POST', headers:{'Content-Type':'application/json','Authorization':'Bearer '+token}, body: JSON.stringify({answers}) });
  if(!res.ok) throw new Error('Cannot submit quiz');
  return res.json();
}

export async function getQuizHistory(token){
  const res = await fetch(`${API_BASE}/student/quizzes/results`, { headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Cannot load quiz history');
  return res.json();
}
