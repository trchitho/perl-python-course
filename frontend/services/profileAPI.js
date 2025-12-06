import { apiGet, apiPut, apiPost } from './apiConfig.js';

export async function getMe(){
  return apiGet('/profile/me');
}

export async function updateMe(body){
  return apiPut('/profile/me', body);
}

export async function changePassword(current_password, new_password){
  return apiPost('/profile/change-password', { current_password, new_password });
}

export async function set2FA(enabled){
  return apiPost('/profile/2fa', { enabled });
}

