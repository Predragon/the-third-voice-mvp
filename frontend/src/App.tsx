import { useState, createContext, useContext, useEffect, ReactNode } from 'react';
import { MessageSquare, Lightbulb, Send, Sparkles, ArrowRight, Shield, Heart, Users, History, LogIn, LogOut, BarChart3, Settings as SettingsIcon } from 'lucide-react';
import api from './api';
import type { User, Contact, TransformResult, InterpretResult } from './types';
import ContactList from './components/ContactList';
import MessageHistory from './components/MessageHistory';
import Dashboard from './components/Dashboard';
import ForgotPassword from './components/ForgotPassword';
import FeedbackWidget, { FeedbackButton } from './components/FeedbackWidget';
import Settings from './components/Settings';

// Types
interface AuthContextType {
  user: User | null;
  token: string | null;
  isDemo: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  startDemo: () => Promise<void>;
  logout: () => void;
}

type ProcessResult = TransformResult | InterpretResult;
type ViewType = 'landing' | 'app' | 'contacts' | 'history' | 'auth' | 'dashboard' | 'forgot-password' | 'settings';

// Auth Context
const AuthContext = createContext<AuthContextType | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isDemo, setIsDemo] = useState(false);

  useEffect(() => {
    const savedToken = localStorage.getItem('thirdvoice_token');
    const savedUser = localStorage.getItem('thirdvoice_user');
    const savedIsDemo = localStorage.getItem('thirdvoice_is_demo') === 'true';

    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
      setIsDemo(savedIsDemo);
      api.setToken(savedToken);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const data = await api.login(email, password);
    setToken(data.access_token);
    setUser(data.user);
    setIsDemo(false);
    api.setToken(data.access_token);
    localStorage.setItem('thirdvoice_token', data.access_token);
    localStorage.setItem('thirdvoice_user', JSON.stringify(data.user));
    localStorage.setItem('thirdvoice_is_demo', 'false');
  };

  const register = async (email: string, password: string) => {
    const data = await api.register(email, password);
    setToken(data.access_token);
    setUser(data.user);
    setIsDemo(false);
    api.setToken(data.access_token);
    localStorage.setItem('thirdvoice_token', data.access_token);
    localStorage.setItem('thirdvoice_user', JSON.stringify(data.user));
    localStorage.setItem('thirdvoice_is_demo', 'false');
  };

  const startDemo = async () => {
    const data = await api.startDemo();
    setToken(data.access_token);
    setUser(data.user);
    setIsDemo(true);
    api.setToken(data.access_token);
    localStorage.setItem('thirdvoice_token', data.access_token);
    localStorage.setItem('thirdvoice_user', JSON.stringify(data.user));
    localStorage.setItem('thirdvoice_is_demo', 'true');
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    setIsDemo(false);
    api.setToken(null);
    localStorage.removeItem('thirdvoice_token');
    localStorage.removeItem('thirdvoice_user');
    localStorage.removeItem('thirdvoice_is_demo');
  };

  return (
    <AuthContext.Provider value={{ user, token, isDemo, login, register, startDemo, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Auth Page
function AuthPage({ onBack, onSuccess, onForgotPassword }: { onBack: () => void; onSuccess: () => void; onForgotPassword: () => void }) {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (mode === 'login') {
        await login(email, password);
      } else {
        await register(email, password);
      }
      onSuccess();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 flex items-center justify-center px-4">
      <div className="bg-white rounded-lg p-8 shadow-lg max-w-md w-full">
        <div className="flex items-center justify-center gap-2 mb-6">
          <MessageSquare className="w-8 h-8 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">The Third Voice</h1>
        </div>

        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setMode('login')}
            className={`flex-1 py-2 rounded-lg font-medium ${
              mode === 'login' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'
            }`}
          >
            Login
          </button>
          <button
            onClick={() => setMode('register')}
            className={`flex-1 py-2 rounded-lg font-medium ${
              mode === 'register' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'
            }`}
          >
            Register
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              required
              minLength={8}
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-300"
          >
            {loading ? 'Please wait...' : mode === 'login' ? 'Login' : 'Create Account'}
          </button>
        </form>

        {mode === 'login' && (
          <button
            onClick={onForgotPassword}
            className="w-full mt-3 text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            Forgot your password?
          </button>
        )}

        <button
          onClick={onBack}
          className="w-full mt-4 text-gray-500 hover:text-gray-700 text-sm"
        >
          ← Back to home
        </button>
      </div>
    </div>
  );
}

// Landing Page
function LandingPage({ onTryDemo, onLogin }: { onTryDemo: () => void; onLogin: () => void }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-2 mb-4">
            <MessageSquare className="w-10 h-10 text-blue-600" />
            <h1 className="text-4xl font-bold text-gray-900">The Third Voice</h1>
          </div>
          <p className="text-xl text-gray-700 mb-2">Communicate better for your children</p>
          <p className="text-lg text-gray-600">AI-powered message assistant for co-parents</p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <Shield className="w-8 h-8 text-blue-600 mb-3" />
            <h3 className="font-semibold mb-2">Stop the Conflict</h3>
            <p className="text-gray-600 text-sm">Transform reactive messages into constructive communication</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <Heart className="w-8 h-8 text-green-600 mb-3" />
            <h3 className="font-semibold mb-2">Understand Needs</h3>
            <p className="text-gray-600 text-sm">Decode what they're really saying beneath the words</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <Users className="w-8 h-8 text-blue-600 mb-3" />
            <h3 className="font-semibold mb-2">Put Kids First</h3>
            <p className="text-gray-600 text-sm">Better communication means better outcomes for your children</p>
          </div>
        </div>

        <div className="text-center space-y-4">
          <button
            onClick={onTryDemo}
            className="bg-blue-600 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-blue-700 transition-colors inline-flex items-center gap-2"
          >
            Try It Now <ArrowRight className="w-5 h-5" />
          </button>
          <p className="text-sm text-gray-600">No signup required</p>
          <button
            onClick={onLogin}
            className="text-blue-600 hover:text-blue-700 font-medium inline-flex items-center gap-1"
          >
            <LogIn className="w-4 h-4" /> Login or Register
          </button>
        </div>
      </div>
    </div>
  );
}

// Main App Interface
function MainApp({ onViewHistory, onViewDashboard, onViewSettings }: { onViewHistory: () => void; onViewDashboard: () => void; onViewSettings: () => void }) {
  const { user, isDemo, logout } = useAuth();
  const [message, setMessage] = useState('');
  const [mode, setMode] = useState<'transform' | 'interpret'>('transform');
  const [useDeep, setUseDeep] = useState(false);
  const [result, setResult] = useState<ProcessResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

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
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async (text: string, index: number | null = null) => {
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

  const isTransformResult = (r: ProcessResult): r is TransformResult => 'transformed_message' in r;
  const isInterpretResult = (r: ProcessResult): r is InterpretResult => 'suggested_responses' in r || 'interpretation' in r;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
      <div className="max-w-3xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-8 h-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">The Third Voice</h1>
              <p className="text-sm text-gray-500">
                {user ? (isDemo ? 'Demo Mode' : user.email) : 'Co-parenting assistant'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {user && (
              <>
                <button
                  onClick={onViewDashboard}
                  className="p-2 text-gray-600 hover:text-blue-600 hover:bg-white rounded-lg transition-colors"
                  title="Dashboard"
                >
                  <BarChart3 className="w-5 h-5" />
                </button>
                <button
                  onClick={onViewHistory}
                  className="p-2 text-gray-600 hover:text-blue-600 hover:bg-white rounded-lg transition-colors"
                  title="Message History"
                >
                  <History className="w-5 h-5" />
                </button>
                <button
                  onClick={onViewSettings}
                  className="p-2 text-gray-600 hover:text-blue-600 hover:bg-white rounded-lg transition-colors"
                  title="Settings"
                >
                  <SettingsIcon className="w-5 h-5" />
                </button>
                <button
                  onClick={logout}
                  className="p-2 text-gray-600 hover:text-red-600 hover:bg-white rounded-lg transition-colors"
                  title="Logout"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </>
            )}
          </div>
        </div>

        {/* Mode Toggle */}
        <div className="bg-white rounded-lg p-4 shadow-sm mb-6">
          <div className="flex gap-2 mb-4">
            <button
              onClick={() => setMode('transform')}
              className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-colors ${
                mode === 'transform' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <Sparkles className="w-5 h-5 inline mr-2" />
              Transform
            </button>
            <button
              onClick={() => setMode('interpret')}
              className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-colors ${
                mode === 'interpret' ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <Lightbulb className="w-5 h-5 inline mr-2" />
              Interpret
            </button>
          </div>
          <p className="text-sm text-gray-600 text-center">
            {mode === 'transform' ? 'Rewrite your message to be more constructive' : 'Understand what they really mean'}
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
                ? "I'm sick of you being late to every pickup..."
                : "You're always making excuses..."
            }
            className="w-full h-32 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          />
          <div className="mt-4 flex items-center justify-between">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={useDeep}
                onChange={(e) => setUseDeep(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Deep Analysis</span>
            </label>
            <button onClick={handleClear} className="text-sm text-gray-500 hover:text-gray-700">Clear</button>
          </div>
        </div>

        {/* Action Button */}
        <button
          onClick={handleProcess}
          disabled={!message.trim() || loading}
          className={`w-full py-4 rounded-lg font-semibold text-lg transition-colors ${
            mode === 'transform' ? 'bg-blue-600 hover:bg-blue-700' : 'bg-green-600 hover:bg-green-700'
          } text-white disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2`}
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
            {mode === 'transform' && isTransformResult(result) ? (
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-gray-900">Transformed Message:</h3>
                  <button onClick={() => handleCopy(result.transformed_message)} className="text-sm text-blue-600 hover:text-blue-700 font-medium">
                    {copied ? 'Copied!' : 'Copy'}
                  </button>
                </div>
                <p className="text-gray-800 leading-relaxed mb-4 p-4 bg-blue-50 rounded-lg">{result.transformed_message}</p>
                {result.explanation && (
                  <div className="border-t pt-4">
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Why this helps:</h4>
                    <p className="text-sm text-gray-600">{result.explanation}</p>
                  </div>
                )}
                {result.healing_score !== undefined && (
                  <div className="mt-4 flex items-center gap-2">
                    <span className="text-sm text-gray-600">Healing score:</span>
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div className="bg-green-600 h-2 rounded-full" style={{ width: `${result.healing_score * 10}%` }} />
                    </div>
                    <span className="text-sm font-semibold text-gray-700">{result.healing_score}/10</span>
                  </div>
                )}
                {result.saved && <p className="mt-2 text-xs text-green-600">✓ Saved to history</p>}
                <div className="mt-4 pt-4 border-t">
                  <FeedbackWidget context="transform" minimal />
                </div>
              </div>
            ) : isInterpretResult(result) ? (
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <h3 className="font-semibold text-gray-900 mb-3">What they really mean:</h3>
                <p className="text-gray-800 leading-relaxed mb-4 p-4 bg-green-50 rounded-lg">
                  {result.interpretation || result.explanation}
                </p>
                {result.suggested_responses && result.suggested_responses.length > 0 && (
                  <div className="border-t pt-4">
                    <h4 className="text-sm font-semibold text-gray-700 mb-3">Suggested responses:</h4>
                    <div className="space-y-2">
                      {result.suggested_responses.map((resp, idx) => (
                        <div key={idx} className="flex items-start gap-2">
                          <div className="flex-1 p-3 bg-gray-50 rounded-lg text-sm text-gray-700">{resp}</div>
                          <button
                            onClick={() => handleCopy(resp, idx)}
                            className="px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-lg font-medium"
                          >
                            {copiedIndex === idx ? '✓' : 'Copy'}
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
                        <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">{need}</span>
                      ))}
                    </div>
                  </div>
                )}
                {result.saved && <p className="mt-4 text-xs text-green-600">✓ Saved to history</p>}
                <div className="mt-4 pt-4 border-t">
                  <FeedbackWidget context="interpret" minimal />
                </div>
              </div>
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
}

// Main App Component
export default function App() {
  const [currentView, setCurrentView] = useState<ViewType>('landing');
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);

  return (
    <AuthProvider>
      <AppContent
        currentView={currentView}
        setCurrentView={setCurrentView}
        selectedContact={selectedContact}
        setSelectedContact={setSelectedContact}
      />
    </AuthProvider>
  );
}

function AppContent({
  currentView,
  setCurrentView,
  selectedContact,
  setSelectedContact
}: {
  currentView: ViewType;
  setCurrentView: (view: ViewType) => void;
  selectedContact: Contact | null;
  setSelectedContact: (contact: Contact | null) => void;
}) {
  const { user, isDemo, startDemo, logout } = useAuth();

  const handleTryDemo = async () => {
    try {
      await startDemo();
      setCurrentView('app');
    } catch (err) {
      console.error('Demo failed:', err);
      setCurrentView('app'); // Continue anyway
    }
  };

  switch (currentView) {
    case 'landing':
      return (
        <LandingPage
          onTryDemo={handleTryDemo}
          onLogin={() => setCurrentView('auth')}
        />
      );

    case 'auth':
      return (
        <AuthPage
          onBack={() => setCurrentView('landing')}
          onSuccess={() => setCurrentView('app')}
          onForgotPassword={() => setCurrentView('forgot-password')}
        />
      );

    case 'forgot-password':
      return (
        <ForgotPassword
          onBack={() => setCurrentView('auth')}
          onSuccess={() => setCurrentView('auth')}
        />
      );

    case 'app':
      return (
        <>
          <MainApp
            onViewHistory={() => setCurrentView('contacts')}
            onViewDashboard={() => setCurrentView('dashboard')}
            onViewSettings={() => setCurrentView('settings')}
          />
          <FeedbackButton />
          <button
            onClick={() => setCurrentView('landing')}
            className="fixed bottom-4 left-4 bg-white text-gray-700 px-4 py-2 rounded-full shadow-lg hover:shadow-xl transition-shadow text-sm font-medium"
          >
            ← Back
          </button>
        </>
      );

    case 'dashboard':
      return (
        <Dashboard
          onBack={() => setCurrentView('app')}
          onViewContact={(contact) => {
            setSelectedContact(contact);
            setCurrentView('history');
          }}
        />
      );

    case 'contacts':
      return (
        <ContactList
          onSelectContact={(contact) => {
            setSelectedContact(contact);
            setCurrentView('history');
          }}
          onBack={() => setCurrentView('app')}
        />
      );

    case 'history':
      return selectedContact ? (
        <MessageHistory
          contact={selectedContact}
          onBack={() => setCurrentView('contacts')}
        />
      ) : (
        <ContactList
          onSelectContact={(contact) => {
            setSelectedContact(contact);
            setCurrentView('history');
          }}
          onBack={() => setCurrentView('app')}
        />
      );

    case 'settings':
      return (
        <Settings
          user={user}
          isDemo={isDemo}
          onBack={() => setCurrentView('app')}
          onLogout={() => {
            logout();
            setCurrentView('landing');
          }}
        />
      );

    default:
      return <LandingPage onTryDemo={handleTryDemo} onLogin={() => setCurrentView('auth')} />;
  }
}

export { useAuth };
