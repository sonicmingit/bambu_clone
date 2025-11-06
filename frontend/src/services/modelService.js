import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000
});

export async function fetchModels(params = {}) {
  const response = await api.get('/models', { params });
  return response.data;
}

export async function fetchModelDetail(id) {
  const response = await api.get(`/models/${id}`);
  return response.data;
}
