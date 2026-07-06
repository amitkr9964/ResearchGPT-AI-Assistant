import axios from 'axios';

const API_BASE = (import.meta as any).env.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  signup: (data: { email: string; username: string; password: string; full_name?: string }) =>
    api.post('/auth/signup', data),
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
  updateMe: (data: { full_name?: string; dark_mode?: boolean }) =>
    api.patch('/auth/me', data),
};

export const documentsApi = {
  list: (search?: string) => api.get('/documents', { params: { search } }),
  get: (id: number) => api.get(`/documents/${id}`),
  upload: (file: File, author?: string, tags?: string) => {
    const form = new FormData();
    form.append('file', file);
    if (author) form.append('author', author);
    if (tags) form.append('tags', tags);
    return api.post('/documents/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  delete: (id: number) => api.delete(`/documents/${id}`),
  rename: (id: number, filename: string) =>
    api.patch(`/documents/${id}/rename`, { filename }),
  update: (id: number, data: { author?: string; tags?: string }) =>
    api.patch(`/documents/${id}`, data),
};

export const chatApi = {
  send: (data: {
    message: string;
    conversation_id?: number;
    document_ids?: number[];
    search_mode?: string;
    stream?: boolean;
  }) => api.post('/chat', { ...data, stream: false }),

  getHistory: () => api.get('/history'),
  getConversation: (id: number) => api.get(`/history/${id}`),
  deleteConversation: (id: number) => api.delete(`/history/${id}`),
  deleteAllHistory: () => api.delete('/history'),
  updateConversation: (id: number, data: { title?: string; is_favorite?: boolean }) =>
    api.patch(`/history/${id}`, data),
};

export const searchApi = {
  search: (data: {
    query: string;
    document_ids?: number[];
    tags?: string[];
    author?: string;
    filename?: string;
    search_mode?: string;
    top_k?: number;
  }) => api.post('/search', data),
};

export const advancedApi = {
  summarize: (docId: number) => api.get(`/summary/${docId}`),
  compare: (docId1: number, docId2: number) =>
    api.post('/compare', { document_id_1: docId1, document_id_2: docId2 }),
  quiz: (docId: number, numQuestions = 5) =>
    api.post('/quiz', { document_id: docId, num_questions: numQuestions }),
  flashcards: (docId: number, numCards = 10) =>
    api.post('/flashcards', { document_id: docId, num_cards: numCards }),
  literatureReview: (documentIds: number[]) =>
    api.post('/literature-review', { document_ids: documentIds }),
  entities: (docId: number) => api.get(`/entities/${docId}`),
  keywords: (docId: number) => api.get(`/keywords/${docId}`),
};

export const exportApi = {
  exportChat: (conversationId: number, format: 'markdown' | 'pdf' | 'docx') =>
    api.post('/export', { conversation_id: conversationId, format }, { responseType: 'blob' }),
};

export async function streamChat(
  data: {
    message: string;
    conversation_id?: number;
    document_ids?: number[];
    search_mode?: string;
  },
  onToken: (token: string) => void,
  onMeta: (meta: { conversation_id: number; citations: unknown[] }) => void,
  onDone: () => void,
  onError: (error: string) => void
) {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ ...data, stream: true }),
  });

  if (!response.ok) {
    onError('Failed to send message');
    return;
  }

  const reader = response.body?.getReader();
  if (!reader) return;

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const parsed = JSON.parse(line.slice(6));
          if (parsed.type === 'token') onToken(parsed.content);
          else if (parsed.type === 'meta') onMeta(parsed);
          else if (parsed.type === 'done') onDone();
        } catch {
          // skip malformed SSE
        }
      }
    }
  }
}

export default api;
