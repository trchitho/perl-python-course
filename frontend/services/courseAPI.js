const API_BASE = 'http://127.0.0.1:5000/api';

export async function listAllCourses(token){
  const res = await fetch(`${API_BASE}/student/all-courses`, { headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Cannot fetch courses');
  return res.json();
}

export async function enrollCourse(token, courseId){
  const res = await fetch(`${API_BASE}/student/enroll`, { method:'POST', headers:{'Content-Type':'application/json','Authorization':'Bearer '+token}, body: JSON.stringify({course_id: courseId}) });
  return res.json();
}
