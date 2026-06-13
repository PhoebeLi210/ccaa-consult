import axios, { AxiosInstance, AxiosResponse } from 'axios';

const BASE_URL = '/api';

const request: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

request.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data;
  },
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      '网络异常，请稍后重试';
    return Promise.reject(new Error(message));
  },
);

export { request };
export default request;
