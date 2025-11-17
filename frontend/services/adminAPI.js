const API_BASE = 'http://127.0.0.1:5000/api';

export async function listUsers(token){
  const res = await fetch(`${API_BASE}/admin/users`, { headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Cannot fetch users');
  return res.json();
}

export async function lockUser(token, id){
  const res = await fetch(`${API_BASE}/admin/users/${id}/lock`, { method:'POST', headers:{'Authorization':'Bearer '+token} });
  return res.json();
}

export async function unlockUser(token, id){
  const res = await fetch(`${API_BASE}/admin/users/${id}/unlock`, { method:'POST', headers:{'Authorization':'Bearer '+token} });
  return res.json();
}

// New: create / update / delete and role assignment
export async function createUser(token, body){
  const res = await fetch(`${API_BASE}/admin/users`, { method:'POST', headers:{'Content-Type':'application/json','Authorization':'Bearer '+token}, body: JSON.stringify(body) });
  if(!res.ok) throw new Error('Create user failed');
  return res.json();
}

export async function updateUser(token, id, body){
  const res = await fetch(`${API_BASE}/admin/users/${id}`, { method:'PUT', headers:{'Content-Type':'application/json','Authorization':'Bearer '+token}, body: JSON.stringify(body) });
  if(!res.ok) throw new Error('Update user failed');
  return res.json();
}

export async function deleteUser(token, id){
  const res = await fetch(`${API_BASE}/admin/users/${id}`, { method:'DELETE', headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Delete user failed');
  return res.json();
}

export async function setUserRole(token, id, role){
  const res = await fetch(`${API_BASE}/admin/users/${id}/role`, { method:'PATCH', headers:{'Content-Type':'application/json','Authorization':'Bearer '+token}, body: JSON.stringify({role}) });
  if(!res.ok) throw new Error('Set role failed');
  return res.json();
}

// Enrollments
export async function listEnrollments(token){
  const res = await fetch(`${API_BASE}/admin/enrollments`, { headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Cannot fetch enrollments');
  return res.json();
}
export async function approveEnrollment(token, id){
  const res = await fetch(`${API_BASE}/admin/enrollments/${id}/approve`, { method:'POST', headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Approve enrollment failed');
  return res.json();
}
export async function lockEnrollment(token, id){
  const res = await fetch(`${API_BASE}/admin/enrollments/${id}/lock`, { method:'POST', headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Lock enrollment failed');
  return res.json();
}

// Stats & Logs
export async function getAdminStats(token){
  const res = await fetch(`${API_BASE}/admin/stats`, { headers:{'Authorization':'Bearer '+token} });
  return res.ok ? res.json() : { users:0, courses:0, errors:0 };
}
export async function listLogs(token){
  const res = await fetch(`${API_BASE}/admin/logs`, { headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Cannot fetch logs');
  return res.json();
}
export function exportLogsCSV(){
  window.open(`${API_BASE}/admin/logs/export?format=csv`, '_blank');
}
export function exportLogsPDF(){
  window.open(`${API_BASE}/admin/logs/export?format=pdf`, '_blank');
}

// Settings
export async function getSettings(token){
  const res = await fetch(`${API_BASE}/admin/settings`, { headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Cannot fetch settings');
  return res.json();
}
export async function updateSettings(token, body){
  const res = await fetch(`${API_BASE}/admin/settings`, { method:'PUT', headers:{'Content-Type':'application/json','Authorization':'Bearer '+token}, body: JSON.stringify(body) });
  if(!res.ok) throw new Error('Update settings failed');
  return res.json();
}
export async function runBackup(token){
  const res = await fetch(`${API_BASE}/admin/backup`, { method:'POST', headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Backup failed');
  return res.json();
}
