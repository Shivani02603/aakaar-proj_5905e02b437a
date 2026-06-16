import { Deployment } from '@/types/deployment';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export async function createSession(data: { name?: string }): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/sessions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error('Failed to create session');
  }
  return response.json();
}

export async function listSessions(): Promise<any[]> {
  const response = await fetch(`${API_BASE_URL}/api/sessions`);
  if (!response.ok) {
    throw new Error('Failed to fetch sessions');
  }
  return response.json();
}

export async function getMessages(sessionId: string): Promise<any[]> {
  const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/messages`);
  if (!response.ok) {
    throw new Error('Failed to fetch messages');
  }
  return response.json();
}

export async function uploadFile(formData: FormData): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/files/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    throw new Error('Failed to upload file');
  }
  return response.json();
}

export async function ingestDocuments(data: { file_ids: string[] }): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/ai/ingest`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error('Failed to ingest documents');
  }
  return response.json();
}

export async function aiQuery(data: { session_id: string; query: string }): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/ai/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error('Failed to send query');
  }
  return response.json();
}

// Deployment-specific API functions
export async function fetchDeployments(): Promise<Deployment[]> {
  const response = await fetch(`${API_BASE_URL}/api/deployments`);
  if (!response.ok) {
    throw new Error('Failed to fetch deployments');
  }
  return response.json();
}

export async function createDeployment(data: Omit<Deployment, 'id' | 'created_at' | 'updated_at'>): Promise<Deployment> {
  const response = await fetch(`${API_BASE_URL}/api/deployments`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error('Failed to create deployment');
  }
  return response.json();
}

export async function deleteDeployment(id: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/deployments/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error('Failed to delete deployment');
  }
}