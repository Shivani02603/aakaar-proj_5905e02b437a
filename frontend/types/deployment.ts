export interface Deployment {
  id: string;
  name: string;
  status: 'pending' | 'active' | 'failed';
  environment: string;
  version: string;
  created_at: string;
  updated_at: string;
}