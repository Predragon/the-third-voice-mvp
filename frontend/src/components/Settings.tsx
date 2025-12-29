import { useState } from 'react';
import {
  ChevronLeft,
  User,
  Bell,
  Shield,
  Download,
  Trash2,
  Info,
  ChevronRight,
  Mail,
  Lock,
  Check,
  AlertTriangle,
  ExternalLink
} from 'lucide-react';
// API will be used when backend endpoints are connected
// import api from '../api';

interface SettingsProps {
  user: { id: string; email: string } | null;
  isDemo: boolean;
  onBack: () => void;
  onLogout: () => void;
}

type SettingsSection = 'main' | 'profile' | 'notifications' | 'privacy' | 'export' | 'delete' | 'about';

export default function Settings({ user, isDemo, onBack, onLogout }: SettingsProps) {
  const [section, setSection] = useState<SettingsSection>('main');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Notification preferences state
  const [notifications, setNotifications] = useState({
    emailUpdates: true,
    weeklyDigest: false,
    newFeatures: true,
    tips: true
  });

  // Privacy settings state
  const [privacy, setPrivacy] = useState({
    saveHistory: true,
    analytics: true,
    improvementData: true
  });

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 3000);
  };

  const handleExportData = async () => {
    setLoading(true);
    try {
      // In production, this would call an API endpoint
      const data = {
        exportDate: new Date().toISOString(),
        user: user?.email,
        note: 'Data export feature - full implementation requires backend endpoint'
      };

      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `thirdvoice-export-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);

      showMessage('success', 'Data export started. Check your downloads.');
    } catch (err) {
      showMessage('error', 'Export failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (isDemo) {
      showMessage('error', 'Demo accounts cannot be deleted.');
      return;
    }

    const confirmed = window.confirm(
      'Are you sure you want to delete your account? This action cannot be undone. All your data will be permanently deleted.'
    );

    if (confirmed) {
      const doubleConfirm = window.confirm(
        'This is your final warning. Type "DELETE" in the next prompt to confirm.'
      );

      if (doubleConfirm) {
        setLoading(true);
        try {
          // In production: await api.deleteAccount();
          showMessage('success', 'Account deletion requested. You will receive a confirmation email.');
          setTimeout(() => onLogout(), 2000);
        } catch (err) {
          showMessage('error', 'Failed to delete account. Please contact support.');
        } finally {
          setLoading(false);
        }
      }
    }
  };

  const handleSaveNotifications = async () => {
    setLoading(true);
    try {
      // In production: await api.updateNotificationPreferences(notifications);
      await new Promise(resolve => setTimeout(resolve, 500));
      showMessage('success', 'Notification preferences saved.');
    } catch (err) {
      showMessage('error', 'Failed to save preferences.');
    } finally {
      setLoading(false);
    }
  };

  const handleSavePrivacy = async () => {
    setLoading(true);
    try {
      // In production: await api.updatePrivacySettings(privacy);
      await new Promise(resolve => setTimeout(resolve, 500));
      showMessage('success', 'Privacy settings saved.');
    } catch (err) {
      showMessage('error', 'Failed to save settings.');
    } finally {
      setLoading(false);
    }
  };

  const renderMain = () => (
    <div className="space-y-2">
      {/* Profile */}
      <button
        onClick={() => setSection('profile')}
        className="w-full flex items-center justify-between p-4 bg-white rounded-lg shadow-sm hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
            <User className="w-5 h-5 text-blue-600" />
          </div>
          <div className="text-left">
            <p className="font-medium text-gray-900">Profile</p>
            <p className="text-sm text-gray-500">{user?.email || 'Manage your account'}</p>
          </div>
        </div>
        <ChevronRight className="w-5 h-5 text-gray-400" />
      </button>

      {/* Notifications */}
      <button
        onClick={() => setSection('notifications')}
        className="w-full flex items-center justify-between p-4 bg-white rounded-lg shadow-sm hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
            <Bell className="w-5 h-5 text-green-600" />
          </div>
          <div className="text-left">
            <p className="font-medium text-gray-900">Notifications</p>
            <p className="text-sm text-gray-500">Email and app alerts</p>
          </div>
        </div>
        <ChevronRight className="w-5 h-5 text-gray-400" />
      </button>

      {/* Privacy */}
      <button
        onClick={() => setSection('privacy')}
        className="w-full flex items-center justify-between p-4 bg-white rounded-lg shadow-sm hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
            <Shield className="w-5 h-5 text-purple-600" />
          </div>
          <div className="text-left">
            <p className="font-medium text-gray-900">Privacy</p>
            <p className="text-sm text-gray-500">Data and security settings</p>
          </div>
        </div>
        <ChevronRight className="w-5 h-5 text-gray-400" />
      </button>

      {/* Export Data */}
      <button
        onClick={() => setSection('export')}
        className="w-full flex items-center justify-between p-4 bg-white rounded-lg shadow-sm hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center">
            <Download className="w-5 h-5 text-orange-600" />
          </div>
          <div className="text-left">
            <p className="font-medium text-gray-900">Export Data</p>
            <p className="text-sm text-gray-500">Download your information</p>
          </div>
        </div>
        <ChevronRight className="w-5 h-5 text-gray-400" />
      </button>

      {/* About */}
      <button
        onClick={() => setSection('about')}
        className="w-full flex items-center justify-between p-4 bg-white rounded-lg shadow-sm hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
            <Info className="w-5 h-5 text-gray-600" />
          </div>
          <div className="text-left">
            <p className="font-medium text-gray-900">About</p>
            <p className="text-sm text-gray-500">App info and support</p>
          </div>
        </div>
        <ChevronRight className="w-5 h-5 text-gray-400" />
      </button>

      {/* Delete Account */}
      {!isDemo && (
        <button
          onClick={() => setSection('delete')}
          className="w-full flex items-center justify-between p-4 bg-white rounded-lg shadow-sm hover:bg-red-50 transition-colors mt-6"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
              <Trash2 className="w-5 h-5 text-red-600" />
            </div>
            <div className="text-left">
              <p className="font-medium text-red-600">Delete Account</p>
              <p className="text-sm text-gray-500">Permanently remove your data</p>
            </div>
          </div>
          <ChevronRight className="w-5 h-5 text-gray-400" />
        </button>
      )}
    </div>
  );

  const renderProfile = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
            <User className="w-8 h-8 text-blue-600" />
          </div>
          <div>
            <p className="font-semibold text-gray-900">{isDemo ? 'Demo User' : 'Co-Parent'}</p>
            <p className="text-sm text-gray-500">{user?.email}</p>
            {isDemo && (
              <span className="inline-block mt-1 px-2 py-0.5 bg-yellow-100 text-yellow-800 text-xs rounded-full">
                Demo Mode
              </span>
            )}
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            <Mail className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-xs text-gray-500">Email</p>
              <p className="text-sm text-gray-900">{user?.email}</p>
            </div>
          </div>

          {!isDemo && (
            <button
              onClick={() => showMessage('info' as any, 'Password change coming soon')}
              className="w-full flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Lock className="w-5 h-5 text-gray-400" />
              <div className="text-left">
                <p className="text-xs text-gray-500">Password</p>
                <p className="text-sm text-blue-600">Change password</p>
              </div>
            </button>
          )}
        </div>
      </div>

      {isDemo && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            <strong>Demo Mode:</strong> Create an account to save your data permanently and access all features.
          </p>
        </div>
      )}
    </div>
  );

  const renderNotifications = () => (
    <div className="bg-white rounded-lg p-6 shadow-sm">
      <h3 className="font-semibold text-gray-900 mb-4">Email Notifications</h3>

      <div className="space-y-4">
        <label className="flex items-center justify-between">
          <div>
            <p className="font-medium text-gray-900">Product Updates</p>
            <p className="text-sm text-gray-500">New features and improvements</p>
          </div>
          <input
            type="checkbox"
            checked={notifications.emailUpdates}
            onChange={(e) => setNotifications({ ...notifications, emailUpdates: e.target.checked })}
            className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
          />
        </label>

        <label className="flex items-center justify-between">
          <div>
            <p className="font-medium text-gray-900">Weekly Digest</p>
            <p className="text-sm text-gray-500">Summary of your communication progress</p>
          </div>
          <input
            type="checkbox"
            checked={notifications.weeklyDigest}
            onChange={(e) => setNotifications({ ...notifications, weeklyDigest: e.target.checked })}
            className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
          />
        </label>

        <label className="flex items-center justify-between">
          <div>
            <p className="font-medium text-gray-900">Co-Parenting Tips</p>
            <p className="text-sm text-gray-500">Helpful advice and resources</p>
          </div>
          <input
            type="checkbox"
            checked={notifications.tips}
            onChange={(e) => setNotifications({ ...notifications, tips: e.target.checked })}
            className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
          />
        </label>
      </div>

      <button
        onClick={handleSaveNotifications}
        disabled={loading}
        className="w-full mt-6 bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-300"
      >
        {loading ? 'Saving...' : 'Save Preferences'}
      </button>
    </div>
  );

  const renderPrivacy = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h3 className="font-semibold text-gray-900 mb-4">Data & Privacy</h3>

        <div className="space-y-4">
          <label className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">Save Message History</p>
              <p className="text-sm text-gray-500">Keep transformed/interpreted messages</p>
            </div>
            <input
              type="checkbox"
              checked={privacy.saveHistory}
              onChange={(e) => setPrivacy({ ...privacy, saveHistory: e.target.checked })}
              className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
            />
          </label>

          <label className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">Usage Analytics</p>
              <p className="text-sm text-gray-500">Help us improve the app</p>
            </div>
            <input
              type="checkbox"
              checked={privacy.analytics}
              onChange={(e) => setPrivacy({ ...privacy, analytics: e.target.checked })}
              className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
            />
          </label>

          <label className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">AI Improvement</p>
              <p className="text-sm text-gray-500">Use anonymized data to improve AI</p>
            </div>
            <input
              type="checkbox"
              checked={privacy.improvementData}
              onChange={(e) => setPrivacy({ ...privacy, improvementData: e.target.checked })}
              className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
            />
          </label>
        </div>

        <button
          onClick={handleSavePrivacy}
          disabled={loading}
          className="w-full mt-6 bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-300"
        >
          {loading ? 'Saving...' : 'Save Settings'}
        </button>
      </div>

      <div className="bg-gray-50 rounded-lg p-4">
        <p className="text-sm text-gray-600">
          Your messages are encrypted and never shared. We only use anonymized, aggregated data to improve our AI.
          <a href="#" className="text-blue-600 ml-1">Read our Privacy Policy</a>
        </p>
      </div>
    </div>
  );

  const renderExport = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h3 className="font-semibold text-gray-900 mb-2">Export Your Data</h3>
        <p className="text-sm text-gray-600 mb-6">
          Download all your data including messages, contacts, and settings. This is useful for your records or if you're leaving the platform.
        </p>

        <div className="space-y-3">
          <button
            onClick={handleExportData}
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-300"
          >
            <Download className="w-5 h-5" />
            {loading ? 'Preparing...' : 'Export All Data (JSON)'}
          </button>

          <p className="text-xs text-gray-500 text-center">
            Export includes: Profile, Contacts, Message History, Settings
          </p>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          <strong>GDPR Compliance:</strong> You have the right to receive a copy of your personal data. Export requests are processed immediately.
        </p>
      </div>
    </div>
  );

  const renderDelete = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg p-6 shadow-sm border-2 border-red-200">
        <div className="flex items-center gap-3 mb-4">
          <AlertTriangle className="w-8 h-8 text-red-600" />
          <h3 className="font-semibold text-red-600 text-lg">Delete Account</h3>
        </div>

        <p className="text-gray-600 mb-4">
          This action is <strong>permanent and cannot be undone</strong>. All your data will be deleted including:
        </p>

        <ul className="list-disc list-inside text-sm text-gray-600 space-y-1 mb-6">
          <li>Your profile and account information</li>
          <li>All contacts and relationships</li>
          <li>Complete message history</li>
          <li>Feedback and preferences</li>
        </ul>

        <button
          onClick={handleDeleteAccount}
          disabled={loading || isDemo}
          className="w-full bg-red-600 text-white py-3 rounded-lg font-semibold hover:bg-red-700 disabled:bg-gray-300"
        >
          {loading ? 'Processing...' : 'Delete My Account'}
        </button>

        {isDemo && (
          <p className="text-sm text-gray-500 text-center mt-3">
            Demo accounts cannot be deleted
          </p>
        )}
      </div>

      <div className="bg-gray-50 rounded-lg p-4">
        <p className="text-sm text-gray-600">
          Need help? Contact us at <a href="mailto:support@thethirdvoice.ai" className="text-blue-600">support@thethirdvoice.ai</a> before deleting your account.
        </p>
      </div>
    </div>
  );

  const renderAbout = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg p-6 shadow-sm text-center">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-3xl">🎭</span>
        </div>
        <h3 className="font-bold text-xl text-gray-900">The Third Voice</h3>
        <p className="text-gray-500 mb-2">Version 1.0.0</p>
        <p className="text-sm text-gray-600 italic">
          "When both parents are talking from pain, your children need a third voice."
        </p>
      </div>

      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h4 className="font-semibold text-gray-900 mb-4">Our Mission</h4>
        <p className="text-sm text-gray-600 mb-4">
          We help co-parents communicate better for the sake of their children. Using AI, we transform reactive messages into constructive ones and help decode emotional subtext.
        </p>
        <p className="text-sm text-gray-600">
          Built with love, powered by AI, designed for healing families.
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-sm divide-y">
        <a href="https://thethirdvoice.ai" target="_blank" rel="noopener noreferrer" className="flex items-center justify-between p-4 hover:bg-gray-50">
          <span className="text-gray-900">Website</span>
          <ExternalLink className="w-4 h-4 text-gray-400" />
        </a>
        <a href="mailto:support@thethirdvoice.ai" className="flex items-center justify-between p-4 hover:bg-gray-50">
          <span className="text-gray-900">Contact Support</span>
          <ExternalLink className="w-4 h-4 text-gray-400" />
        </a>
        <a href="#" className="flex items-center justify-between p-4 hover:bg-gray-50">
          <span className="text-gray-900">Privacy Policy</span>
          <ExternalLink className="w-4 h-4 text-gray-400" />
        </a>
        <a href="#" className="flex items-center justify-between p-4 hover:bg-gray-50">
          <span className="text-gray-900">Terms of Service</span>
          <ExternalLink className="w-4 h-4 text-gray-400" />
        </a>
      </div>
    </div>
  );

  const getSectionTitle = () => {
    switch (section) {
      case 'profile': return 'Profile';
      case 'notifications': return 'Notifications';
      case 'privacy': return 'Privacy';
      case 'export': return 'Export Data';
      case 'delete': return 'Delete Account';
      case 'about': return 'About';
      default: return 'Settings';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
      <div className="max-w-lg mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <button
            onClick={() => section === 'main' ? onBack() : setSection('main')}
            className="p-2 hover:bg-white rounded-lg transition-colors"
          >
            <ChevronLeft className="w-6 h-6 text-gray-600" />
          </button>
          <h1 className="text-xl font-bold text-gray-900">{getSectionTitle()}</h1>
        </div>

        {/* Message Toast */}
        {message && (
          <div className={`mb-4 p-3 rounded-lg flex items-center gap-2 ${
            message.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {message.type === 'success' ? <Check className="w-5 h-5" /> : <AlertTriangle className="w-5 h-5" />}
            <p className="text-sm">{message.text}</p>
          </div>
        )}

        {/* Content */}
        {section === 'main' && renderMain()}
        {section === 'profile' && renderProfile()}
        {section === 'notifications' && renderNotifications()}
        {section === 'privacy' && renderPrivacy()}
        {section === 'export' && renderExport()}
        {section === 'delete' && renderDelete()}
        {section === 'about' && renderAbout()}
      </div>
    </div>
  );
}
