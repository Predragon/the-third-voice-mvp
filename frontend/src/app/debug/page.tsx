"use client";

import React, { useState } from 'react';
import { AlertCircle, CheckCircle, XCircle, Loader, Zap, Server } from 'lucide-react';

interface DiagnosticResult {
  status: 'success' | 'error';
  statusCode?: number;
  responseTime?: number;
  data?: string | Record<string, unknown>;
  error?: string;
  timestamp: string;
  backend_id?: string;  // Add backend_id support
}

interface AnalysisItem {
  type: 'critical' | 'warning' | 'success';
  message: string;
}

const APIDiagnosticTool = () => {
  const [diagnostics, setDiagnostics] = useState<Record<string, DiagnosticResult>>({});
  const [isRunning, setIsRunning] = useState(false);

  const cleanUrl = (url: string) => url.replace(/\/$/, ''); // Remove trailing slash

  const runFullDiagnostic = async () => {
    setIsRunning(true);
    setDiagnostics({});

    const tests = [
      {
        name: 'Direct Backend Connection',
        test: () => fetch(cleanUrl('https://api.thethirdvoice.ai/api/health'), { 
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        })
      },
      {
        name: 'Proxy Connection',
        test: () => fetch(cleanUrl('/api/proxy/api/health'), {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        })
      },
      {
        name: 'Root Endpoint',
        test: () => fetch(cleanUrl('/api/proxy'), {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        })
      },
      {
        name: 'AI Engine Status',
        test: () => fetch(cleanUrl('/api/proxy/api/health/ai-engine'), {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        })
      },
      {
        name: 'Database Connection',
        test: () => fetch(cleanUrl('/api/proxy/api/health/database'), {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        })
      },
      {
        name: 'System Health',
        test: () => fetch(cleanUrl('/api/proxy/api/health/system'), {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        })
      },
      {
        name: 'Readiness Check',
        test: () => fetch(cleanUrl('/api/proxy/api/health/ready'), {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        })
      },
      {
        name: 'Backend Info Check',
        test: () => fetch(cleanUrl('/api/proxy/api/backend-info'), {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        })
      },
      {
        name: 'Quick Transform (AI Test)',
        test: () => fetch(cleanUrl('/api/proxy/api/messages/quick-transform'), {
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
        name: 'Quick Interpret (AI Test)',
        test: () => fetch(cleanUrl('/api/proxy/api/messages/quick-interpret'), {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({
            message: "Thanks but I'm busy right now",
            contact_context: "friend",
            contact_name: "Test",
            use_deep_analysis: false
          })
        })
      },
      {
        name: 'Messages Health',
        test: () => fetch(cleanUrl('/api/proxy/api/messages/health'), {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        })
      },
      {
        name: 'Get Contacts',
        test: () => fetch(cleanUrl('/api/proxy/api/contacts'), {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        })
      },
      {
        name: 'Available Contexts',
        test: () => fetch(cleanUrl('/api/proxy/api/contacts/contexts/available'), {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        })
      },
      {
        name: 'Feedback Categories',
        test: () => fetch(cleanUrl('/api/proxy/api/feedback/categories'), {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        })
      },
      {
        name: 'Detailed Health Check',
        test: () => fetch(cleanUrl('/api/proxy/api/health/detailed'), {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        })
      },
      {
        name: 'OpenAPI Docs',
        test: () => fetch(cleanUrl('/api/proxy/openapi.json'), {
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
        let backend_id;
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
          data = await response.json();
          
          // Extract backend_id from response if available
          if (data && typeof data === 'object' && 'backend_id' in data) {
            backend_id = data.backend_id;
          }
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
            backend_id,
            timestamp: new Date().toISOString()
          }
        }));
      } catch (error) {
        setDiagnostics(prev => ({
          ...prev,
          [name]: {
            status: 'error',
            error: error instanceof Error ? error.message : String(error),
            timestamp: new Date().toISOString()
          }
        }));
      }

      await new Promise(resolve => setTimeout(resolve, 200));
    }

    setIsRunning(false);
  };

  const analyzeResults = (): AnalysisItem[] | null => {
    const results = Object.entries(diagnostics);
    if (results.length === 0) return null;

    const analysis: AnalysisItem[] = [];
    
    const healthCheck = diagnostics['Proxy Connection'];
    const aiEngine = diagnostics['AI Engine Status'];
    const aiTransform = diagnostics['Quick Transform (AI Test)'];
    const aiInterpret = diagnostics['Quick Interpret (AI Test)'];
    const directBackend = diagnostics['Direct Backend Connection'];
    const contacts = diagnostics['Get Contacts'];
    const backendInfo = diagnostics['Backend Info Check'];

    // Backend identification analysis
    const backendIds = new Set();
    Object.values(diagnostics).forEach(result => {
      if (result.backend_id) {
        backendIds.add(result.backend_id);
      }
    });

    if (backendIds.size > 0) {
      const backendList = Array.from(backendIds).join(', ');
      const serverType = backendIds.has('b1') ? 'Pi Server' : 
                        backendIds.has('b2') ? 'Render/Cloud' : 
                        backendIds.has('dev') ? 'Development' : 'Unknown';
      
      analysis.push({
        type: 'success',
        message: `Backend identification working: ${serverType} (${backendList})`
      });
    } else {
      analysis.push({
        type: 'warning',
        message: 'Backend ID not detected in responses - check backend identification system'
      });
    }

    if (directBackend?.status === 'error') {
      analysis.push({
        type: 'warning',
        message: 'Direct backend connection blocked (expected - CORS protection working)'
      });
    }

    if (healthCheck?.status === 'error') {
      analysis.push({
        type: 'critical',
        message: 'Main health endpoint failing through proxy - check trailing slash handling'
      });
    }

    if (aiEngine?.status === 'error') {
      analysis.push({
        type: 'warning',
        message: 'AI Engine health check failing - may be using fallback responses'
      });
    }

    const aiWorking = [];
    if (aiTransform?.status === 'success' && aiTransform.data) {
      const response = typeof aiTransform.data === 'string' ? aiTransform.data : JSON.stringify(aiTransform.data);
      if (response.includes('transformed_message') && response.includes('healing_score')) {
        aiWorking.push('Transform');
        
        // Check for backend_id in AI responses
        if (response.includes('backend_id')) {
          analysis.push({
            type: 'success',
            message: 'AI Transform endpoint includes backend identification'
          });
        }
      }
    }
    
    if (aiInterpret?.status === 'success' && aiInterpret.data) {
      const response = typeof aiInterpret.data === 'string' ? aiInterpret.data : JSON.stringify(aiInterpret.data);
      if (response.includes('suggested_responses') || response.includes('deeper_feelings')) {
        aiWorking.push('Interpret');
        
        // Check for backend_id in AI responses
        if (response.includes('backend_id')) {
          analysis.push({
            type: 'success',
            message: 'AI Interpret endpoint includes backend identification'
          });
        }
      }
    }

    if (aiWorking.length > 0) {
      analysis.push({
        type: 'success',
        message: `AI engine working properly - ${aiWorking.join(' & ')} endpoints functional`
      });
    } else if (aiTransform?.status === 'success' || aiInterpret?.status === 'success') {
      analysis.push({
        type: 'warning',
        message: 'AI endpoints respond but may be returning fallback responses'
      });
    }

    if (contacts?.status === 'error') {
      analysis.push({
        type: 'warning',
        message: 'Contacts endpoint failing - authentication may be required'
      });
    }

    if (backendInfo?.status === 'success') {
      analysis.push({
        type: 'success',
        message: 'Backend info endpoint functional - detailed backend information available'
      });
    }

    return analysis.length > 0 ? analysis : null;
  };

  const getStatusIcon = (status: string) => {
    if (status === 'success') return <CheckCircle className="w-5 h-5 text-green-500" />;
    if (status === 'error') return <XCircle className="w-5 h-5 text-red-500" />;
    return <AlertCircle className="w-5 h-5 text-yellow-500" />;
  };

  const getBackendBadge = (backend_id?: string) => {
    if (!backend_id) return null;
    
    const badgeColor = backend_id === 'b1' ? 'bg-blue-100 text-blue-800' :
                      backend_id === 'b2' ? 'bg-green-100 text-green-800' :
                      backend_id === 'dev' ? 'bg-purple-100 text-purple-800' :
                      'bg-gray-100 text-gray-800';
    
    const serverName = backend_id === 'b1' ? 'Pi Server' :
                      backend_id === 'b2' ? 'Render/Cloud' :
                      backend_id === 'dev' ? 'Development' :
                      backend_id;
    
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${badgeColor}`}>
        <Server className="w-3 h-3 mr-1" />
        {serverName} ({backend_id})
      </span>
    );
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
          <h3 className="font-semibold text-yellow-800 mb-2">🔍 Deep Diagnostic with Backend Identification</h3>
          <p className="text-yellow-700 text-sm">
            This tool will test both direct backend connection and proxy routing to identify exactly where the communication is failing. 
            Now includes backend identification to show which server (Pi/b1 vs Render/b2) is handling requests.
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
                <div className="flex items-center space-x-3">
                  <h3 className="font-semibold text-gray-800">{name}</h3>
                  {getBackendBadge(result.backend_id)}
                </div>
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
                
                {result.backend_id && (
                  <div className="flex justify-between">
                    <span>Backend ID:</span>
                    <span className="font-medium text-blue-600">{result.backend_id}</span>
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
              <li>Test: <code className="bg-gray-100 px-1 rounded">curl https://api.thethirdvoice.ai/api/health</code></li>
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

          <div>
            <h4 className="font-medium text-gray-700 mb-2">4. Backend Identification Issues:</h4>
            <ul className="list-disc list-inside text-gray-600 ml-4 space-y-1">
              <li>Check BACKEND_ID environment variable is set (b1=Pi, b2=Render)</li>
              <li>Verify config.py has backend detection logic</li>
              <li>Ensure AI responses include backend_id field</li>
              <li>Test backend info endpoint: <code className="bg-gray-100 px-1 rounded">/api/proxy/api/backend-info</code></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default APIDiagnosticTool;