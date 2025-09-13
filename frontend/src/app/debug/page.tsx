"use client";

import React, { useState } from 'react';
import { Play, CheckCircle, XCircle, Eye, RefreshCw } from 'lucide-react';

type Endpoint = { name: string; path: string };

type EndpointResult = {
  status: string;
  statusCode?: number;
  data?: any;
  responseTime?: number;
  url?: string;
  method?: string;
  timestamp?: string;
  error?: string;
};

const DebugDashboard = () => {
  const [results, setResults] = useState<Record<string, EndpointResult>>({});
  const [isTestingAll, setIsTestingAll] = useState(false);

  const endpoints: Endpoint[] = [
    { name: 'Root Endpoint', path: '' },
    { name: 'Health Check', path: 'api/health/' },
    { name: 'Database Health', path: 'api/health/database' },
    { name: 'AI Engine Health', path: 'api/health/ai-engine' },
    { name: 'System Health', path: 'api/health/system' },
    { name: 'Readiness Check', path: 'api/health/ready' },
    { name: 'Liveness Check', path: 'api/health/liveness' },
    { name: 'Detailed Health', path: 'api/health/detailed' },
    { name: 'Docs Endpoint', path: 'docs' },
    { name: 'OpenAPI Endpoint', path: 'openapi.json' },
    { name: 'Quick Transform', path: 'api/messages/quick-transform' },
    { name: 'Quick Interpret', path: 'api/messages/quick-interpret' },
    { name: 'Messages Health', path: 'api/messages/health' },
    { name: 'Get Contacts', path: 'api/contacts/' },
    { name: 'Available Contexts', path: 'api/contacts/contexts/available' },
    { name: 'Feedback Categories', path: 'api/feedback/categories' }
  ];

  const testEndpoint = async (endpoint: Endpoint) => {
    const startTime = Date.now();
    try {
      const url = `/api/proxy/${endpoint.path}`;

      // Use appropriate method based on endpoint
      const method = endpoint.path.includes('quick-transform') ||
                     endpoint.path.includes('quick-interpret') ? 'POST' : 'GET';

      const options = {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        ...(method === 'POST' && {
          body: JSON.stringify({ 
            message: "Test message",
            analysis_depth: "QUICK" 
          })
        })
      };

      const response = await fetch(url, options);
      const responseTime = Date.now() - startTime;

      let data;
      const contentType = response.headers.get('content-type');

      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      return {
        status: response.ok ? 'success' : 'error',
        statusCode: response.status,
        data,
        responseTime,
        url,
        method,
        timestamp: new Date().toLocaleTimeString()
      };
    } catch (error: any) {
      return {
        status: 'error',
        error: error.message,
        responseTime: Date.now() - startTime,
        url: `/api/proxy/${endpoint.path}`,
        method: endpoint.path.includes('quick-') ? 'POST' : 'GET',
        timestamp: new Date().toLocaleTimeString()
      };
    }
  };

  const testAllEndpoints = async () => {
    setIsTestingAll(true);
    setResults({});
    
    for (const endpoint of endpoints) {
      const result = await testEndpoint(endpoint);
      setResults(prev => ({
        ...prev,
        [endpoint.name]: result
      }));
      
      // Small delay between requests
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    setIsTestingAll(false);
  };

  const testSingleEndpoint = async (endpoint: Endpoint) => {
    const result = await testEndpoint(endpoint);
    setResults(prev => ({
      ...prev,
      [endpoint.name]: result
    }));
  };

  const viewResponseData = (result: any) => {
    const dataStr = typeof result.data === 'string' 
      ? result.data 
      : JSON.stringify(result.data, null, 2);
    
    alert(`Response Data:\n\nURL: ${result.url}\nMethod: ${result.method}\nStatus: ${result.statusCode}\nResponse Time: ${result.responseTime}ms\n\nData:\n${dataStr}`);
  };

  return (
    <div className="max-w-6xl mx-auto p-6 bg-gray-50 min-h-screen">
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
          🔍 Debug Dashboard
        </h1>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-blue-800 mb-2">API URL: /api/proxy</h3>
          <p className="text-blue-700 text-sm mb-2">Client-side check via proxy</p>
        </div>

        <button
          onClick={testAllEndpoints}
          disabled={isTestingAll}
          className="bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white px-6 py-3 rounded-lg font-medium flex items-center space-x-2 mb-6"
        >
          {isTestingAll ? <RefreshCw className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5" />}
          <span>{isTestingAll ? 'Testing...' : 'Test All Endpoints'}</span>
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {endpoints.map((endpoint) => {
          const result = results[endpoint.name];
          return (
            <div key={endpoint.name} className="bg-white rounded-lg shadow-md p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-gray-800 text-sm">{endpoint.name}</h3>
                {result && (
                  result.status === 'success' ? 
                    <CheckCircle className="w-5 h-5 text-green-500" /> : 
                    <XCircle className="w-5 h-5 text-red-500" />
                )}
              </div>
              
              {result && (
                <div className="text-xs text-gray-600 mb-3">
                  <div className={`font-medium ${result.status === 'success' ? 'text-green-600' : 'text-red-600'}`}>
                    {result.status === 'success' ? '✅ Connection successful!' : '❌ Connection failed!'}
                  </div>
                  <div className="mt-1">
                    {result.statusCode && <span className="mr-2">{result.statusCode}</span>}
                    <span>{result.timestamp}</span>
                  </div>
                  <div className="mt-1">URL: /api/proxy/{endpoint.path}</div>
                  {result.responseTime && (
                    <div className="mt-1">Response Time: {result.responseTime}ms</div>
                  )}
                  {result.error && (
                    <div className="mt-1 text-red-600">Error: {result.error}</div>
                  )}
                </div>
              )}

              <div className="flex space-x-2">
                <button
                  onClick={() => testSingleEndpoint(endpoint)}
                  className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded text-sm font-medium"
                >
                  Test
                </button>
                {result && result.data && (
                  <button
                    onClick={() => viewResponseData(result)}
                    className="bg-blue-100 hover:bg-blue-200 text-blue-700 px-3 py-2 rounded text-sm font-medium flex items-center"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6 mt-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">🔧 Proxy Configuration</h2>
        <p className="text-gray-600 mb-4">
          Requests are proxied through /api/proxy to https://api.thethirdvoice.ai
        </p>
        <p className="text-sm text-gray-500 mb-4">
          Ensure backend is running on Raspberry Pi and Cloudflare Tunnel is active.
        </p>
        
        <div className="space-x-4">
          <span className="text-sm font-medium text-gray-700">Manual Test Links:</span>
          <a 
            href="https://api.thethirdvoice.ai/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 text-sm underline"
          >
            Root API
          </a>
          <a 
            href="https://api.thethirdvoice.ai/docs" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 text-sm underline"
          >
            API Docs
          </a>
          <a 
            href="https://api.thethirdvoice.ai/api/health/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 text-sm underline"
          >
            Health Check
          </a>
        </div>
      </div>
    </div>
  );
};

export default DebugDashboard;