import axios from 'axios';
import type { Code, Category, TextSegment } from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Codes API
export const codesApi = {
  list: (level?: string) => api.get<Code[]>('/codes', { params: { level } }),
  get: (id: string) => api.get<Code>(`/codes/${id}`),
  create: (data: Partial<Code>) => api.post<Code>('/codes', data),
  update: (id: string, data: Partial<Code>) => api.put<Code>(`/codes/${id}`, data),
  delete: (id: string) => api.delete(`/codes/${id}`)
};

// Categories API
export const categoriesApi = {
  list: () => api.get<Category[]>('/categories'),
  get: (id: string) => api.get<Category>(`/categories/${id}`),
  create: (data: Partial<Category>) => api.post<Category>('/categories', data)
};

// Import API
export const importApi = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/import/text', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  listSegments: () => api.get<TextSegment[]>('/import/segments'),
  clearSegments: () => api.delete('/import/segments')
};

export default api;
