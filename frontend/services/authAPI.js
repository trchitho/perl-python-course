const API_BASE = 'http://127.0.0.1:5000/api';

export async function login(email, password){
  const res = await fetch(`${API_BASE}/auth/login`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({email, password}) });
  if(!res.ok) throw new Error('Login failed');
  return res.json();
}

export async function register(data){
  const res = await fetch(`${API_BASE}/auth/register`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(data) });
  if(!res.ok) throw new Error('Register failed');
  return res.json();
}
