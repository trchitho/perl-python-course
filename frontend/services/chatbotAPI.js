const API_BASE = 'http://127.0.0.1:5000/api';

export async function ask(token, message){
  const res = await fetch(`${API_BASE}/ai/chat`, { method:'POST', headers:{'Content-Type':'application/json','Authorization':'Bearer '+token}, body: JSON.stringify({message}) });
  if(!res.ok) throw new Error('Chat failed');
  return res.json();
}
