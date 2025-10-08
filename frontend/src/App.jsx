import React, { useState, createContext, useContext, useEffect } from 'react';
import { MessageSquare, Lightbulb, User, LogIn, Menu, X, Send, Sparkles, ArrowRight, Shield, Heart, Users } from 'lucide-react';

// API Client with automatic failover
const API_BACKENDS = import.meta.env.DEV 
  ? [''] // Development uses Vite proxy
  : [
      'https://api.thethirdvoice.ai',              // Pi primary
      'https://the-third-voice-mvp.onrender.com'   // Render failover
    ];

class ThirdVoiceAPI {
  constructor() {
    this.currentBackendIndex = 0;
    this.backends = API_BACKENDS;
  }

  async _fetchWithFallback(endpoint, options) {
    const maxRetries = this.backends.length;
    let lastError;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
      const backend = this.backends[this.currentBackendIndex];
      const url = import.meta.env.DEV 
        ? `/api${endpoint}`  // Proxy in dev
        : `${backend}/api${endpoint}`;

      try {
        console.log(`Attempting ${backend || 'local proxy'} (attempt ${attempt + 1}/${maxRetries})`);
        
        const res = await fetch(url, {
          ...options,
          signal: AbortSignal.timeout(40000) // 40 second timeout
        });
        
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        }
        
        // Success! Keep using this backend
        console.log(`✅ Success with ${backend || 'local proxy'}`);
        return res.json();
      } catch (err) {
        console.warn(`❌ ${backend || 'local proxy'} failed:`, err.message);
        lastError = err;
        
        // Try next backend
        this.currentBackendIndex = (this.currentBackendIndex + 1) % this.backends.length;
        
        // If this was the last attempt, throw
        if (attempt === maxRetries - 1) {
          throw new Error(`All backends failed. Last error: ${lastError.message}`);
        }
      }
    }
  }

  async quickTransform(message, contactContext = 'coparenting', useDeep = false) {
    return this._fetchWithFallback('/messages/quick-transform', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        contact_context: contactContext,
        use_deep_analysis: useDeep
      })
    });
  }

  async quickInterpret(message, contactContext = 'coparenting', useDeep = false) {
    return this._fetchWithFallback('/messages/quick-interpret', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        contact_context: contactContext,
        use_deep_analysis: useDeep
      })
    });
  }

  async login(email, password) {
    const res = await fetch(`${this.backends[0] || ''}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) throw new Error('Login failed');
    return res.json();
  }

  async startDemo() {
    const res = await fetch(`${this.backends[0] || ''}/api/auth/demo`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    if (!res.ok) throw new Error('Demo start failed');
    return res.json();
  }

  async register(email, password) {
    const res = await fetch(`${this.backends[0] || ''}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) throw new Error('Registration failed');
    return res.json();
  }
}

const api = new ThirdVoiceAPI();

// Auth Context
const AuthContext = createContext(null);

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [isDemo, setIsDemo] = useState(false);

  useEffect(() => {
    const savedToken = localStorage.getItem('thirdvoice_token');
    const savedUser = localStorage.getItem('thirdvoice_user');
    const savedIsDemo = localStorage.getItem('thirdvoice_is_demo') === 'true';
    
    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
      setIsDemo(savedIsDemo);
    }
  }, []);

  const login = async (email, password) => {
    const data = await api.login(email, password);
    setToken(data.access_token);
    setUser(data.user);
    setIsDemo(false);
    localStorage.setItem('thirdvoice_token', data.access_token);
    localStorage.setItem('thirdvoice_user', JSON.stringify(data.user));
    localStorage.setItem('thirdvoice_is_demo', 'false');
  };

  const startDemo = async () => {
    const data = await api.startDemo();
    setToken(data.access_token);
    setUser(data.user);
    setIsDemo(true);
    localStorage.setItem('thirdvoice_token', data.access_token);
    localStorage.setItem('thirdvoice_user', JSON.stringify(data.user));
    localStorage.setItem('thirdvoice_is_demo', 'true');
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    setIsDemo(false);
    localStorage.removeItem('thirdvoice_token');
    localStorage.removeItem('thirdvoice_user');
    localStorage.removeItem('thirdvoice_is_demo');
  };

  return (
    <AuthContext.Provider value={{ user, token, isDemo, login, startDemo, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

function useAuth() {
  return useContext(AuthContext);
}

// Landing Page
function LandingPage({ onGetStarted, onTryDemo }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
      {/* Hero */}
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-2 mb-4">
            <MessageSquare className="w-10 h-10 text-blue-600" />
            <h1 className="text-4xl font-bold text-gray-900">The Third Voice</h1>
          </div>
          <p className="text-xl text-gray-700 mb-2">
            Communicate better for your children
          </p>
          <p className="text-lg text-gray-600">
            AI-powered message assistant for co-parents
          </p>
        </div>

        {/* Value Props */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <Shield className="w-8 h-8 text-blue-600 mb-3" />
            <h3 className="font-semibold mb-2">Stop the Conflict</h3>
            <p className="text-gray-600 text-sm">
              Transform reactive messages into constructive communication
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <Heart className="w-8 h-8 text-green-600 mb-3" />
            <h3 className="font-semibold mb-2">Understand Needs</h3>
            <p className="text-gray-600 text-sm">
              Decode what they're really saying beneath the words
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <Users className="w-8 h-8 text-blue-600 mb-3" />
            <h3 className="font-semibold mb-2">Put Kids First</h3>
            <p className="text-gray-600 text-sm">
              Better communication means better outcomes for your children
            </p>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center space-y-4">
          <button
            onClick={onTryDemo}
            className="bg-blue-600 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-blue-700 transition-colors inline-flex items-center gap-2"
          >
            Try It Now <ArrowRight className="w-5 h-5" />
          </button>
          <p className="text-sm text-gray-600">No signup required</p>
        </div>

        {/* How It Works */}
        <div className="mt-16 bg-white rounded-lg p-8 shadow-sm">
          <h2 className="text-2xl font-bold mb-6 text-center">How It Works</h2>
          <div className="space-y-6">
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold">
                1
              </div>
              <div>
                <h3 className="font-semibold mb-1">Paste or Type Your Message</h3>
                <p className="text-gray-600 text-sm">
                  Enter the message you want to send to your co-parent
                </p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold">
                2
              </div>
              <div>
                <h3 className="font-semibold mb-1">Choose Transform or Interpret</h3>
                <p className="text-gray-600 text-sm">
                  Transform: Rewrite your message more constructively<br/>
                  Interpret: Understand what they really mean
                </p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold">
                3
              </div>
              <div>
                <h3 className="font-semibold mb-1">Copy and Send</h3>
                <p className="text-gray-600 text-sm">
                  Use the improved version in your messaging app
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Main App Interface
function MainApp() {
  const [message, setMessage] = useState('');
  const [mode, setMode] = useState('transform');
  const [useDeep, setUseDeep] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState(null);

  const handleProcess = async () => {
    if (!message.trim()) return;
    
    setLoading(true);
    setError(null);
    setResult(null);
    
    try {
      const data = mode === 'transform'
        ? await api.quickTransform(message, 'coparenting', useDeep)
        : await api.quickInterpret(message, 'coparenting', useDeep);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async (text, index = null) => {
    try {
      await navigator.clipboard.writeText(text);
      if (index !== null) {
        setCopiedIndex(index);
        setTimeout(() => setCopiedIndex(null), 2000);
      } else {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }
    } catch (err) {
      console.error('Copy failed', err);
    }
  };

  const handleClear = () => {
    setMessage('');
    setResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
      <div className="max-w-3xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-2">
            <MessageSquare className="w-8 h-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">The Third Voice</h1>
          </div>
          <p className="text-gray-600">Co-parenting communication assistant</p>
        </div>

        {/* Mode Toggle */}
        <div className="bg-white rounded-lg p-4 shadow-sm mb-6">
          <div className="flex gap-2 mb-4">
            <button
              onClick={() => setMode('transform')}
              className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-colors ${
                mode === 'transform'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <Sparkles className="w-5 h-5 inline mr-2" />
              Transform
            </button>
            <button
              onClick={() => setMode('interpret')}
              className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-colors ${
                mode === 'interpret'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <Lightbulb className="w-5 h-5 inline mr-2" />
              Interpret
            </button>
          </div>
          
          <p className="text-sm text-gray-600 text-center">
            {mode === 'transform' 
              ? 'Rewrite your message to be more constructive'
              : 'Understand what they really mean and get response ideas'
            }
          </p>
        </div>

        {/* Message Input */}
        <div className="bg-white rounded-lg p-6 shadow-sm mb-6">
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            {mode === 'transform' ? 'Message you want to send:' : 'Message you received:'}
          </label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder={
              mode === 'transform'
                ? "I'm sick of you being late to every pickup. You never respect my time..."
                : "You're always making excuses. I don't think you care about our kids..."
            }
            className="w-full h-32 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          />
          
          {/* Analysis Depth Toggle */}
          <div className="mt-4 flex items-center justify-between">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={useDeep}
                onChange={(e) => setUseDeep(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Deep Analysis (slower, more detailed)</span>
            </label>
            <button
              onClick={handleClear}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              Clear
            </button>
          </div>
        </div>

        {/* Action Button */}
        <button
          onClick={handleProcess}
          disabled={!message.trim() || loading}
          className={`w-full py-4 rounded-lg font-semibold text-lg transition-colors ${
            mode === 'transform'
              ? 'bg-blue-600 hover:bg-blue-700 text-white'
              : 'bg-green-600 hover:bg-green-700 text-white'
          } disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2`}
        >
          {loading ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Send className="w-5 h-5" />
              {mode === 'transform' ? 'Transform Message' : 'Interpret Message'}
            </>
          )}
        </button>

        {/* Error */}
        {error && (
          <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="mt-6 space-y-4">
            {mode === 'transform' ? (
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-gray-900">Transformed Message:</h3>
                  <button
                    onClick={() => handleCopy(result.transformed_message)}
                    className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                  >
                    {copied ? 'Copied!' : 'Copy'}
                  </button>
                </div>
                <p className="text-gray-800 leading-relaxed mb-4 p-4 bg-blue-50 rounded-lg">
                  {result.transformed_message}
                </p>
                
                {result.model_used && (
                  <div className="text-xs text-gray-500 mb-3 border-t pt-3">
                    <span>AI Model: {result.model_used}</span>
                    {result.backend_id && <span> • Backend: {result.backend_id}</span>}
                    {result.analysis_depth && <span> • {result.analysis_depth} analysis</span>}
                  </div>
                )}
                
                {result.explanation && (
                  <div className="border-t pt-4">
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Why this helps:</h4>
                    <p className="text-sm text-gray-600">{result.explanation}</p>
                  </div>
                )}
                
                {result.healing_score !== null && (
                  <div className="mt-4 flex items-center gap-2">
                    <span className="text-sm text-gray-600">Healing score:</span>
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-600 h-2 rounded-full transition-all"
                        style={{ width: `${result.healing_score * 10}%` }}
                      />
                    </div>
                    <span className="text-sm font-semibold text-gray-700">
                      {result.healing_score}/10
                    </span>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <h3 className="font-semibold text-gray-900 mb-3">What they really mean:</h3>
                <p className="text-gray-800 leading-relaxed mb-4 p-4 bg-green-50 rounded-lg">
                  {result.interpretation || result.explanation}
                </p>
                
                {result.model_used && (
                  <div className="text-xs text-gray-500 mb-3 border-t pt-3">
                    <span>AI Model: {result.model_used}</span>
                    {result.backend_id && <span> • Backend: {result.backend_id}</span>}
                    {result.analysis_depth && <span> • {result.analysis_depth} analysis</span>}
                  </div>
                )}
                
                {result.suggested_responses && result.suggested_responses.length > 0 && (
                  <div className="border-t pt-4">
                    <h4 className="text-sm font-semibold text-gray-700 mb-3">Suggested responses:</h4>
                    <div className="space-y-2">
                      {result.suggested_responses.map((resp, idx) => (
                        <div key={idx} className="flex items-start gap-2">
                          <div className="flex-1 p-3 bg-gray-50 rounded-lg text-sm text-gray-700">
                            {resp}
                          </div>
                          <button
                            onClick={() => handleCopy(resp, idx)}
                            className="flex-shrink-0 px-3 py-2 text-sm text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors font-medium"
                          >
                            {copiedIndex === idx ? '✓ Copied' : 'Copy'}
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {result.emotional_needs && result.emotional_needs.length > 0 && (
                  <div className="border-t pt-4 mt-4">
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">They need:</h4>
                    <div className="flex flex-wrap gap-2">
                      {result.emotional_needs.map((need, idx) => (
                        <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                          {need}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// Main App Component
export default function App() {
  const [currentView, setCurrentView] = useState('landing');

  return (
    <AuthProvider>
      <div className="min-h-screen">
        {currentView === 'landing' ? (
          <LandingPage
            onGetStarted={() => setCurrentView('app')}
            onTryDemo={() => setCurrentView('app')}
          />
        ) : (
          <MainApp />
        )}
        
        {/* Back to Landing */}
        {currentView === 'app' && (
          <button
            onClick={() => setCurrentView('landing')}
            className="fixed bottom-4 left-4 bg-white text-gray-700 px-4 py-2 rounded-full shadow-lg hover:shadow-xl transition-shadow text-sm font-medium"
          >
            ← Back
          </button>
        )}
      </div>
    </AuthProvider>
  );
}
