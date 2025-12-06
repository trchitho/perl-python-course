import { apiGet, apiPost, apiPut, apiPatch, apiDelete, API_BASE } from './apiConfig.js';

export async function listUsers(page = 1, perPage = 10){
  return apiGet(`/admin/users?page=${page}&per_page=${perPage}`);
}

export async function lockUser(id){
  return apiPost(`/admin/users/${id}/lock`);
}

export async function unlockUser(id){
  return apiPost(`/admin/users/${id}/unlock`);
}

// New: create / update / delete and role assignment
export async function createUser(body){
  return apiPost('/admin/users', body);
}

export async function updateUser(id, body){
  return apiPut(`/admin/users/${id}`, body);
}

export async function deleteUser(id){
  return apiDelete(`/admin/users/${id}`);
}

export async function setUserRole(id, role){
  return apiPatch(`/admin/users/${id}/role`, { role });
}

// Enrollments
export async function listEnrollments(page = 1, perPage = 10){
  return apiGet(`/admin/enrollments?page=${page}&per_page=${perPage}`);
}

export async function approveEnrollment(id){
  return apiPost(`/admin/enrollments/${id}/approve`);
}

export async function lockEnrollment(id){
  return apiPost(`/admin/enrollments/${id}/lock`);
}

// Stats & Logs
export async function getAdminStats(){
  try {
    return await apiGet('/admin/stats');
  } catch (error) {
    return { users: 0, courses: 0, errors: 0 };
  }
}

export async function listLogs(){
  return apiGet('/admin/logs');
}

export function exportLogsCSV(){
  window.open(`${API_BASE}/admin/logs/export?format=csv`, '_blank');
}

export function exportLogsPDF(){
  window.open(`${API_BASE}/admin/logs/export?format=pdf`, '_blank');
}

// Settings
export async function getSettings(){
  return apiGet('/admin/settings');
}

export async function updateSettings(body){
  return apiPut('/admin/settings', body);
}

export async function runBackup(){
  return apiPost('/admin/backup');
}
