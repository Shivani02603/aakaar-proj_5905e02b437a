'use client';

import { useState, useEffect } from 'react';

interface BackendItem {
  id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export default function BackendPage() {
  const [backends, setBackends] = useState<BackendItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchBackends();
  }, []);

  const fetchBackends = async () => {
    try {
      setLoading(true);
      // Note: This is a placeholder - replace with actual API call
      // Since there's no /api/backends endpoint in the contract,
      // we'll simulate data for demonstration
      const mockData: BackendItem[] = [
        {
          id: '1',
          name: 'Production Backend',
          description: 'Main production backend service',
          created_at: '2024-01-15T10:30:00Z',
          updated_at: '2024-01-20T14:45:00Z',
        },
        {
          id: '2',
          name: 'Staging Backend',
          description: 'Staging environment for testing',
          created_at: '2024-01-10T09:15:00Z',
          updated_at: '2024-01-18T11:20:00Z',
        },
        {
          id: '3',
          name: 'Development Backend',
          description: 'Development and local testing',
          created_at: '2024-01-05T13:45:00Z',
          updated_at: '2024-01-12T16:30:00Z',
        },
      ];
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500));
      setBackends(mockData);
      setError(null);
    } catch (err) {
      setError('Failed to load backends');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this backend?')) return;
    
    try {
      // Note: This is a placeholder - replace with actual DELETE API call
      // Since there's no DELETE endpoint in the contract,
      // we'll simulate deletion
      setBackends(prev => prev.filter(item => item.id !== id));
    } catch (err) {
      alert('Failed to delete backend');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-center items-center h-64">
            <div className="text-gray-500">Loading backends...</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Backend Management</h1>
          <p className="text-gray-600 mt-2">View and manage all backend instances</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-800">Backend Instances</h2>
              <a
                href="/backend/new"
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                Add New Backend
              </a>
            </div>
          </div>

          {backends.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400 mb-4">
                <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No backends found</h3>
              <p className="text-gray-600">Get started by creating a new backend instance.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Description
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Updated
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {backends.map((backend) => (
                    <tr key={backend.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="font-medium text-gray-900">{backend.name}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-gray-700 max-w-md truncate">{backend.description}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-500">
                        {new Date(backend.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-500">
                        {new Date(backend.updated_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex space-x-3">
                          <a
                            href={`/backend/${backend.id}`}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            Edit
                          </a>
                          <button
                            onClick={() => handleDelete(backend.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}