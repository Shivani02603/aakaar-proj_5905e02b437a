export interface Session {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  created_at: string;
}

export interface FileUploadResponse {
  file_id: string;
  filename: string;
  size: number;
  uploaded_at: string;
}

export interface IngestResponse {
  success: boolean;
  message: string;
  document_count: number;
}

export interface QueryResponse {
  answer: string;
  sources: string[];
  session_id: string;
}