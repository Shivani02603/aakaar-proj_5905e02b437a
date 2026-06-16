'use client';

import { useState, useRef } from 'react';
import { Session } from '@/lib/types';
import { createSession, uploadFile, ingestDocuments } from '@/lib/api';

interface SidebarProps {
  sessions: Session[];
  selectedSession: Session | null;
  onSelectSession: (session: Session) => void;
  onSessionCreated: (session: Session) => void;
  onSessionDeleted: (sessionId: string) => void;
}

export default function Sidebar({
  sessions,
  selectedSession,
  onSelectSession,
  onSessionCreated,
  onSessionDeleted,
}: SidebarProps) {
  const [newSessionName, setNewSessionName] = useState('');
  const [uploading, setUploading] = useState(false);
  const [ingesting, setIngesting] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleCreateSession = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSessionName.trim()) return;

    try {
      const session = await createSession(newSessionName.trim());
      onSessionCreated(session);
      setNewSessionName('');
    } catch (error) {
      console.error('Failed to create session:', error);
      alert('Failed to create session');
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    const newFileIds: string[] = [];

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const response = await uploadFile(file);
        newFileIds.push(response.file_id);
      }

      setUploadedFiles(prev => [...prev, ...newFileIds]);
      alert(`Successfully uploaded ${files.length} file(s)`);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed');
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleIngest = async () => {
    if (uploadedFiles.length === 0) {
      alert('No files to ingest');
      return;
    }

    setIngesting(true);
    try {
      const response = await ingestDocuments(uploadedFiles);
      alert(`Ingested ${response.document_count} documents: ${response.message}`);
      setUploadedFiles([]);
    } catch (error) {
      console.error('Ingestion failed:', error);
      alert('Ingestion failed');
    } finally {
      setIngesting(false);
    }
  };

  const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this session?')) return;

    // Note: There's no DELETE endpoint in the contract, so we'll just remove it locally
    // In a real app, you would call a DELETE endpoint here
    onSessionDeleted(sessionId);
  };

  return (
    <div className="w-80 bg-white border-r border-gray-200 flex flex-col h-full">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Create Session</h2>
        <form onSubmit={handleCreateSession} className="space-y-3">
          <input
            type="text"
            value={newSessionName}
            onChange={(e) => setNewSessionName(e.target.value)}
            placeholder="Enter session name"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            type="submit"
            disabled={!newSessionName.trim()}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Create New Session
          </button>
        </form>
      </div>

      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">File Upload</h2>
        <div className="space-y-3">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            multiple
            className="hidden"
            id="file-upload"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-md border border-gray-300 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? 'Uploading...' : 'Select Files to Upload'}
          </button>
          
          {uploadedFiles.length > 0 && (
            <div className="mt-2">
              <p className="text-sm text-gray-600 mb-2">
                {uploadedFiles.length} file(s) ready for ingestion
              </p>
              <button
                onClick={handleIngest}
                disabled={ingesting}
                className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {ingesting ? 'Ingesting...' : 'Ingest Documents'}
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="p-4">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Sessions</h2>
          {sessions.length === 0 ? (
            <p className="text-gray-500 text-center py-4">No sessions yet</p>
          ) : (
            <div className="space-y-2">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  onClick={() => onSelectSession(session)}
                  className={`p-3 rounded-md cursor-pointer transition-colors ${
                    selectedSession?.id === session.id
                      ? 'bg-blue-50 border border-blue-200'
                      : 'bg-gray-50 hover:bg-gray-100 border border-gray-200'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-800 truncate">{session.name}</h3>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(session.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <button
                      onClick={(e) => handleDeleteSession(session.id, e)}
                      className="text-red-500 hover:text-red-700 ml-2"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}