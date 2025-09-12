"use client"
import React, { useState } from 'react';

interface TestResult {
  status: number | string;
  success: boolean;
  data?: unknown;
  error?: string;
  url: string;
  timestamp: string;
}

interface TestResults {
  [key: string]: TestResult;
}

export default function DebugPage() {
  const [testResults, setTestResults] = useState<TestResults>({});
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const apiUrl = '/api/proxy'; // Proxy to backend

  const testEndpoint = async (endpoint: string, name: string): Promise<void> => {
    setIsLoading(true);
    try {
      const fullUrl = `${apiUrl}${endpoint}`;
      const response = await fetch(fullUrl, {
        cache: 'no-store', // Ensure fresh responses
      });
      const data = await response.json();
      
      setTestResults(prev => ({
        ...prev,
        [name]: {
          status: response.status,
          success: response.ok,
          data: data,
          url: fullUrl,
          timestamp: new Date().toLocaleTimeString()
        }
      }));
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        [name]: {
          status: 'ERROR',
          success: false,
          error: (error as Error).message,
          url: `${apiUrl}${endpoint}`,
          timestamp: new Date().toLocaleTimeString()
        }
      }));
    }
    setIsLoading(false);
  };

  const testAllEndpoints = async (): Promise<void> => {
    setTestResults({});
    await testEndpoint('/', 'Root'); // Adjusted to match backend
    await testEndpoint('/api/health', 'Health');
    await testEndpoint('/docs', 'Docs');
    await testEndpoint('/openapi.json', 'OpenAPI');
    // Add more endpoints if needed, e.g., '/api/messages/quick-transform'
  };

  return (
    <div className="min-h-screen bg-gray-900 text-green-300 p-8">
      <h1 className="text-2xl font-bold mb-4">🔍 Debug Dashboard</h1>
      
      <div className="space-y-4">
        <div className="bg-gray-800 p-4 rounded-lg">
          <p><strong>API URL:</strong> <span className="text-blue-400">{apiUrl}</span></p>
          <p><strong>Client-side check via proxy</strong></p>
        </div>

        <div className="flex space-x-4">
          <button 
            onClick={testAllEndpoints}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? 'Testing...' : 'Test All Endpoints'}
          </button>
          
          <button 
            onClick={() => testEndpoint('/', 'Root')}
            disabled={isLoading}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
          >
            Test Root
          </button>
        </div>

        {Object.keys(testResults).length > 0 && (
          <div className="mt-8 space-y-4">
            <h2 className="text-xl font-bold">Test Results</h2>
            {Object.entries(testResults).map(([name, result]: [string, TestResult]) => (
              <div key={name} className={`p-4 rounded-lg border-2 ${
                result.success ? 'border-green-500 bg-green-900/20' : 'border-red-500 bg-red-900/20'
              }`}>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-bold">{name} Endpoint</h3>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded text-sm ${
                      result.success ? 'bg-green-600' : 'bg-red-600'
                    }`}>
                      {result.status}
                    </span>
                    <span className="text-sm text-gray-400">{result.timestamp}</span>
                  </div>
                </div>
                
                <p className="text-sm text-gray-300 mb-2">
                  <strong>URL:</strong> {result.url}
                </p>
                
                {result.success ? (
                  <div>
                    <p className="text-green-400 mb-2">✅ Connection successful!</p>
                    {result.data != null && (
                      <details className="text-sm">
                        <summary className="cursor-pointer text-blue-400">View Response Data</summary>
                        <pre className="mt-2 p-2 bg-gray-800 rounded overflow-auto text-xs">
                          {JSON.stringify(result.data, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                ) : (
                  <div>
                    <p className="text-red-400 mb-2">❌ Connection failed!</p>
                    <p className="text-sm text-red-300">Error: {result.error}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        <div className="mt-8 p-4 bg-blue-800 rounded-xl shadow">
          <p className="text-lg font-bold">🔧 Proxy Configuration</p>
          <div className="text-sm mt-2 space-y-1">
            <p>Requests are proxied through /api/proxy to https://api.thethirdvoice.ai</p>
            <p>Ensure backend is running on Raspberry Pi and Cloudflare Tunnel is active.</p>
          </div>
        </div>

        <div className="mt-8 text-sm text-gray-400">
          <h3 className="font-bold mb-2">Manual Test Links:</h3>
          <div className="space-x-4">
            <a href={`${apiUrl}/`} target="_blank" rel="noopener noreferrer" className="underline text-blue-400 hover:text-blue-300">Root API</a>
            <a href={`${apiUrl}/docs`} target="_blank" rel="noopener noreferrer" className="underline text-blue-400 hover:text-blue-300">API Docs</a>
            <a href={`${apiUrl}/api/health`} target="_blank" rel="noopener noreferrer" className="underline text-blue-400 hover:text-blue-300">Health Check</a>
          </div>
        </div>
      </div>
    </div>
  );
}