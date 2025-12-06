import { apiGet, apiPost } from './apiConfig.js';

export async function listAllCourses(){
  return apiGet('/student/all-courses');
}

export async function enrollCourse(courseId){
  return apiPost('/student/enroll', { course_id: courseId });
}
