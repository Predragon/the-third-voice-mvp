"use client";

import React, { useState } from 'react';
import { AlertCircle, CheckCircle, XCircle, Loader, Zap, RefreshCw } from 'lucide-react';

const APIDiagnosticTool = () => {
  const [diagnostics, setDiagnostics] = useState({});
  const [isRunning, setIsRunning] = useState(false);

  const runFullDiagnostic = async () => {
    setIsRunning(true);
    setDiagnostics({});

    const tests = [
      {
        name: 'Direct Backend Connection',
        test: () => fetch('https://api.thethirdvoice.ai/api/health/', { 
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        })
      },
      {
        name: 'Proxy Connection',
        test: () => fetch('/api/proxy/api/health/', {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        })
      },
      {
        name: 'AI Engine Status',
        test: () => fetch('/api/proxy/api/health/ai-engine', {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        })
      },
      {
        name: 'Database Connection',
        test: () => fetch('/api/proxy/api/health/database', {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        })
      },
      {
        name: 'Quick Transform (Real AI Test)',
        test: () => fetch('/api/proxy/api/messages/quick-transform', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({
            message: "I'm testing the AI connection",
            contact_context: "friend",
            contact_name: "Test",
            use_deep_analysis: false
          })
        })
      },
      {
        name: 'Detailed Health Check',
        test: () => fetch('/api/proxy/api/health/detailed', {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        })
      }
    ];

    for (const { name, test } of tests) {
      try {
        const startTime = Date.now();
        const response = await test();
        const responseTime = Date.now() - startTime;
        
        let data;
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
          data = await response.json();
        } else {
          data = await response.text();
        }

        setDiagnostics(prev => ({
          ...prev,
          [name]: {
            status: response.ok ? 'success' : 'error',
            statusCode: response.status,
            responseTime,
            data,
            timestamp: new Date().toISOString()
          }
        }));
      } catch (error) {
        setDiagnostics(prev => ({
          ...prev,
          [name]: {
            status: 'error',
            error: error.message,
            timestamp: new Date().toISOString()
          }
        }));
      }

      // Small delay between tests
      await new Promise(resolve => setTimeout(resolve, 200));
    }

    setIsRunning(false);
  };

  const analyzeResults = () => {
    const results = Object.entries(diagnostics);
    if (results.length === 0) return null;

    let analysis = [];
    
    // Check for specific patterns
    const healthCheck = diagnostics['Proxy Connection'];
    const aiEngine = diagnostics['AI Engine Status'];
    const aiTest = diagnostics['Quick Transform (Real AI Test)'];
    const directBackend = diagnostics['Direct Backend Connection'];

    if (directBackend && directBackend.status === 'error') {
      analysis.push({
        type: 'critical',
        message: 'Backend server appears to be down or unreachable directly'
      });
    }

    if (healthCheck && healthCheck.status === 'error') {
      analysis.push({
        type: 'critical',
        message: 'Main health endpoint failing - core API issue'
      });
    }

    if (aiEngine && aiEngine.status === 'error') {
      analysis.push({
        type: 'warning',
        message: 'AI Engine health check failing - may be using fallback responses'
      });
    }

    if (aiTest && aiTest.status === 'success' && aiTest.data) {
      const response = typeof aiTest.data === 'string' ? aiTest.data : JSON.stringify(aiTest.data);
      if (response.includes('Network Fallback') || response.includes('technical difficulties')) {
        analysis.push({
          type: 'warning',
          message: 'AI endpoint returns fallback response - AI engine not properly connected'
        });
      } else if (response.includes('suggested_responses') || response.includes('analysis')) {
        analysis.push({
          type: 'success',
          message: 'AI engine appears to be working properly'
        });
      }
    }

    return analysis;
  };

  const getStatusIcon = (status) => {
    if (status === 'success') return <CheckCircle className="w-5 h-5 text-green-500" />;
    if (status === 'error') return <XCircle className="w-5 h-5 text-red-500" />;
    return <AlertCircle className="w-5 h-5 text-yellow-500" />;
  };

  const analysis = analyzeResults();

  return (
    <div className="max-w-4xl mx-auto p-6 bg-gray-50 min-h-screen">
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
          <Zap className="w-6 h-6 mr-2 text-blue-500" />
          API Connection Diagnostic Tool
        </h1>
        
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-yellow-800 mb-2">🔍 Deep Diagnostic</h3>
          <p className="text-yellow-700 text-sm">
            This tool will test both direct backend connection and proxy routing to identify exactly where the communication is failing.
          </p>
        </div>

        <button
          onClick={runFullDiagnostic}
          disabled={isRunning}
          className="bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white px-6 py-3 rounded-lg font-medium flex items-center space-x-2"
        >
          {isRunning ? <Loader className="w-5 h-5 animate-spin" /> : <Zap className="w-5 h-5" />}
          <span>{isRunning ? 'Running Diagnostics...' : 'Run Full Diagnostic'}</span>
        </button>
      </div>

      {analysis && analysis.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">🎯 Analysis & Recommendations</h2>
          <div className="space-y-3">
            {analysis.map((item, index) => (
              <div 
                key={index}
                className={`p-3 rounded-lg border ${
                  item.type === 'critical' ? 'bg-red-50 border-red-200' :
                  item.type === 'warning' ? 'bg-yellow-50 border-yellow-200' :
                  'bg-green-50 border-green-200'
                }`}
              >
                <div className={`font-medium ${
                  item.type === 'critical' ? 'text-red-800' :
                  item.type === 'warning' ? 'text-yellow-800' :
                  'text-green-800'
                }`}>
                  {item.type === 'critical' ? '🚨' : item.type === 'warning' ? '⚠️' : '✅'} {item.message}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {Object.keys(diagnostics).length > 0 && (
        <div className="grid gap-4">
          {Object.entries(diagnostics).map(([name, result]) => (
            <div key={name} className="bg-white rounded-lg shadow-md p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-gray-800">{name}</h3>
                {getStatusIcon(result.status)}
              </div>
              
              <div className="text-sm text-gray-600 space-y-1">
                <div className="flex justify-between">
                  <span>Status:</span>
                  <span className={`font-medium ${
                    result.status === 'success' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {result.statusCode || result.status}
                  </span>
                </div>
                
                {result.responseTime && (
                  <div className="flex justify-between">
                    <span>Response Time:</span>
                    <span>{result.responseTime}ms</span>
                  </div>
                )}
                
                {result.error && (
                  <div className="text-red-600 mt-2">
                    <strong>Error:</strong> {result.error}
                  </div>
                )}
                
                {result.data && (
                  <details className="mt-2">
                    <summary className="cursor-pointer text-blue-600 hover:text-blue-800">
                      View Response Data
                    </summary>
                    <pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto max-h-32">
                      {typeof result.data === 'string' 
                        ? result.data 
                        : JSON.stringify(result.data, null, 2)
                      }
                    </pre>
                  </details>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="bg-white rounded-lg shadow-lg p-6 mt-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">🔧 Troubleshooting Steps</h2>
        <div className="space-y-4 text-sm">
          <div>
            <h4 className="font-medium text-gray-700 mb-2">1. If Direct Backend Connection Fails:</h4>
            <ul className="list-disc list-inside text-gray-600 ml-4 space-y-1">
              <li>Check if Raspberry Pi is running</li>
              <li>Verify Cloudflare Tunnel is active</li>
              <li>Test: <code className="bg-gray-100 px-1 rounded">curl https://api.thethirdvoice.ai/api/health/</code></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-700 mb-2">2. If Proxy Connection Fails:</h4>
            <ul className="list-disc list-inside text-gray-600 ml-4 space-y-1">
              <li>Check Next.js API route configuration</li>
              <li>Verify proxy route at <code className="bg-gray-100 px-1 rounded">/api/proxy/[...path]/route.ts</code></li>
              <li>Check CORS settings</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-700 mb-2">3. If AI Engine Fails:</h4>
            <ul className="list-disc list-inside text-gray-600 ml-4 space-y-1">
              <li>Check OpenAI API key configuration</li>
              <li>Verify AI service initialization in backend</li>
              <li>Check backend logs for AI engine errors</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default APIDiagnosticTool;