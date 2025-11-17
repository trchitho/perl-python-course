const API_BASE = 'http://127.0.0.1:5000/api';

export async function getMe(token){
  const res = await fetch(`${API_BASE}/profile/me`, { headers:{'Authorization':'Bearer '+token} });
  if(!res.ok) throw new Error('Cannot load profile');
  return res.json();
}

export async function updateMe(token, body){
  const res = await fetch(`${API_BASE}/profile/me`, { method:'PUT', headers:{'Content-Type':'application/json','Authorization':'Bearer '+token}, body: JSON.stringify(body) });
  if(!res.ok) throw new Error('Save failed');
  return res.json();
}

export async function changePassword(token, current_password, new_password){
  const res = await fetch(`${API_BASE}/profile/change-password`, { method:'POST', headers:{'Content-Type':'application/json','Authorization':'Bearer '+token}, body: JSON.stringify({current_password, new_password}) });
  return res.json();
}

export async function set2FA(token, enabled){
  const res = await fetch(`${API_BASE}/profile/2fa`, { method:'POST', headers:{'Content-Type':'application/json','Authorization':'Bearer '+token}, body: JSON.stringify({enabled}) });
  return res.json();
}

