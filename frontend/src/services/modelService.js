import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
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
