const API_BASE = 'http://127.0.0.1:5000/api';

// Stats
export async function getTeacherStats(token){
  const res = await fetch(`${API_BASE}/teacher/stats`, { headers:{'Authorization':'Bearer '+token} });
  return res.ok ? res.json() : { courses:0, students:0, quizzes:0, avg_score:0 };
}

// Courses
export async function listTeacherCourses(token){
  const res = await fetch(`${API_BASE}/teacher/courses`, { headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Cannot list courses');
  return res.json();
}
export async function createCourse(token, body){
  const res = await fetch(`${API_BASE}/teacher/courses`, { method:'POST', headers:{'Content-Type':'application/json','Authorization':'Bearer '+token}, body: JSON.stringify(body)});
  if(!res.ok) throw new Error('Create failed');
  return res.json();
}
export async function updateCourse(token, id, body){
  const res = await fetch(`${API_BASE}/teacher/courses/${id}`, { method:'PUT', headers:{'Content-Type':'application/json','Authorization':'Bearer '+token}, body: JSON.stringify(body)});
  if(!res.ok) throw new Error('Update failed');
  return res.json();
}
export async function toggleCourseStatus(token, id, status){
  const res = await fetch(`${API_BASE}/teacher/courses/${id}/status`, { method:'PATCH', headers:{'Content-Type':'application/json','Authorization':'Bearer '+token}, body: JSON.stringify({status})});
  if(!res.ok) throw new Error('Toggle failed');
  return res.json();
}
export async function deleteCourse(token, id){
  const res = await fetch(`${API_BASE}/teacher/courses/${id}`, { method:'DELETE', headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Delete failed');
  return res.json();
}

// Lessons
export async function listLessons(token, courseId){
  const res = await fetch(`${API_BASE}/teacher/courses/${courseId}/lessons`, { headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Cannot list lessons');
  return res.json();
}
export async function createLesson(token, courseId, body){
  const res = await fetch(`${API_BASE}/teacher/courses/${courseId}/lessons`, { method:'POST', headers:{'Content-Type':'application/json','Authorization':'Bearer '+token}, body: JSON.stringify(body)});
  if(!res.ok) throw new Error('Create lesson failed');
  return res.json();
}
export async function reorderLessons(token, courseId, order){
  const res = await fetch(`${API_BASE}/teacher/courses/${courseId}/lessons/reorder`, { method:'PATCH', headers:{'Content-Type':'application/json','Authorization':'Bearer '+token}, body: JSON.stringify({order})});
  if(!res.ok) throw new Error('Reorder failed');
  return res.json();
}

// Quizzes
export async function listQuizzes(token, courseId){
  const res = await fetch(`${API_BASE}/teacher/courses/${courseId}/quizzes`, { headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Cannot list quizzes');
  return res.json();
}
export async function listAllQuizzes(token){
  const res = await fetch(`${API_BASE}/teacher/quizzes`, { headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Cannot list all quizzes');
  return res.json();
}
export async function createQuiz(token, courseId, body){
  const res = await fetch(`${API_BASE}/teacher/courses/${courseId}/quizzes`, { method:'POST', headers:{'Content-Type':'application/json','Authorization':'Bearer '+token}, body: JSON.stringify(body)});
  if(!res.ok) throw new Error('Create quiz failed');
  return res.json();
}
export async function updateQuiz(token, quizId, body){
  const res = await fetch(`${API_BASE}/teacher/quizzes/${quizId}`, { method:'PUT', headers:{'Content-Type':'application/json','Authorization':'Bearer '+token}, body: JSON.stringify(body)});
  if(!res.ok) throw new Error('Update quiz failed');
  return res.json();
}
export async function deleteQuiz(token, quizId){
  const res = await fetch(`${API_BASE}/teacher/quizzes/${quizId}`, { method:'DELETE', headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Delete quiz failed');
  return res.json();
}
export async function createQuestion(token, quizId, body){
  const res = await fetch(`${API_BASE}/teacher/quizzes/${quizId}/questions`, { method:'POST', headers:{'Content-Type':'application/json','Authorization':'Bearer '+token}, body: JSON.stringify(body)});
  if(!res.ok) throw new Error('Create question failed');
  return res.json();
}
export async function listResults(token, quizId){
  const res = await fetch(`${API_BASE}/teacher/quizzes/${quizId}/results`, { headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Cannot list results');
  return res.json();
}

export async function listCourseScores(token, courseId){
  const res = await fetch(`${API_BASE}/teacher/courses/${courseId}/scores`, { headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Cannot load course scores');
  return res.json();
}

// Subscribers
export async function listSubscribers(token, courseId){
  const res = await fetch(`${API_BASE}/teacher/courses/${courseId}/subscribers`, { headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Cannot list subscribers');
  return res.json();
}
export async function approveSubscriber(token, id){
  const res = await fetch(`${API_BASE}/teacher/subscribers/${id}/approve`, { method:'POST', headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Approve failed');
  return res.json();
}
export async function removeSubscriber(token, id){
  const res = await fetch(`${API_BASE}/teacher/subscribers/${id}`, { method:'DELETE', headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Remove failed');
  return res.json();
}

export async function listTeacherAnnouncements(token, courseId){
  const url = courseId ? `${API_BASE}/teacher/announcements?course_id=${courseId}` : `${API_BASE}/teacher/announcements`;
  const res = await fetch(url, { headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Cannot load announcements');
  return res.json();
}


export async function updateLesson(token, lessonId, body){
  const res = await fetch(`${API_BASE}/teacher/lessons/${lessonId}`, { method:'PUT', headers:{'Content-Type':'application/json','Authorization':'Bearer '+token}, body: JSON.stringify(body)});
  if(!res.ok) throw new Error('Update lesson failed');
  return res.json();
}

export async function deleteLesson(token, lessonId){
  const res = await fetch(`${API_BASE}/teacher/lessons/${lessonId}`, { method:'DELETE', headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Delete lesson failed');
  return res.json();
}
