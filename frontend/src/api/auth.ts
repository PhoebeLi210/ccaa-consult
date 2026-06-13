import { request } from './request';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
  email?: string;
  full_name?: string;
  company?: string;
}

export interface UserInfo {
  user_id: string;
  username: string;
  email?: string;
  full_name?: string;
  company?: string;
  role: string;
  status: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserInfo;
}

export function register(data: RegisterRequest) {
  return request.post<unknown, UserInfo>('/v1/auth/register', data);
}

export function login(username: string, password: string) {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);
  return request.post<unknown, TokenResponse>('/v1/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
}

export function loginJson(data: LoginRequest) {
  return request.post<unknown, TokenResponse>('/v1/auth/login/json', data);
}

export function getCurrentUser() {
  return request.get<unknown, UserInfo>('/v1/auth/me');
}

export function logout() {
  return request.post<unknown, { message: string }>('/v1/auth/logout');
}
