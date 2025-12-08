import { apiGet, apiPost } from './apiConfig.js';

export async function listAllCourses(searchQuery = ''){
  const params = searchQuery ? `?search=${encodeURIComponent(searchQuery)}` : '';
  return apiGet(`/student/all-courses${params}`);
}

export async function enrollCourse(courseId){
  return apiPost('/student/enroll', { course_id: courseId });
}
