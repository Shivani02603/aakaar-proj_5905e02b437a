import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

// Base URL configuration
const baseURL = process.env.NEXT_PUBLIC_API_URL || '';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT token
api.interceptors.request.use(
  (config) => {
    // Only run in browser environment
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error: AxiosError) => {
    // Only run in browser environment
    if (typeof window !== 'undefined' && error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// TypeScript interfaces
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface RegisterResponse {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
}

export interface CreateSessionRequest {
  title?: string;
}

export interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  user_id: string;
}

export interface Message {
  id: string;
  session_id: string;
  content: string;
  role: 'user' | 'assistant';
  created_at: string;
  metadata?: Record<string, any>;
}

export interface UploadFileRequest {
  file: File;
}

export interface UploadFileResponse {
  id: string;
  filename: string;
  filepath: string;
  file_size: number;
  mime_type: string;
  created_at: string;
}

export interface IngestDocumentsRequest {
  file_ids: string[];
}

export interface IngestDocumentsResponse {
  success: boolean;
  message: string;
  document_count: number;
}

export interface AIQueryRequest {
  session_id: string;
  query: string;
  file_ids?: string[];
}

export interface AIQueryResponse {
  response: string;
  session_id: string;
  sources?: Array<{
    document_id: string;
    filename: string;
    content: string;
    similarity_score: number;
  }>;
}

// API functions
export const login = (data: LoginRequest): Promise<AxiosResponse<LoginResponse>> => {
  return api.post('/api/auth/login', data);
};

export const register = (data: RegisterRequest): Promise<AxiosResponse<RegisterResponse>> => {
  return api.post('/api/auth/register', data);
};

export const createSession = (data: CreateSessionRequest = {}): Promise<AxiosResponse<Session>> => {
  return api.post('/api/sessions', data);
};

export const listSessions = (): Promise<AxiosResponse<Session[]>> => {
  return api.get('/api/sessions');
};

export const getMessages = (sessionId: string): Promise<AxiosResponse<Message[]>> => {
  return api.get(`/api/sessions/${sessionId}/messages`);
};

export const uploadFile = (data: FormData): Promise<AxiosResponse<UploadFileResponse>> => {
  return api.post('/api/files/upload', data, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const ingestDocuments = (data: IngestDocumentsRequest): Promise<AxiosResponse<IngestDocumentsResponse>> => {
  return api.post('/api/ai/ingest', data);
};

export const aiQuery = (data: AIQueryRequest): Promise<AxiosResponse<AIQueryResponse>> => {
  return api.post('/api/ai/query', data);
};

// Helper function to create FormData for file upload
export const createFileUploadFormData = (file: File): FormData => {
  const formData = new FormData();
  formData.append('file', file);
  return formData;
};

export default api;