import { useState, useEffect } from 'react';
import {
  BarChart3, TrendingUp, MessageSquare, Users, Calendar,
  ChevronLeft, Sparkles, Lightbulb, Heart, Award
} from 'lucide-react';
import api from '../api';
import type { Contact } from '../types';

interface DashboardProps {
  onBack: () => void;
  onViewContact: (contact: Contact) => void;
}

interface DashboardStats {
  totalMessages: number;
  totalContacts: number;
  avgHealingScore: number;
  transformCount: number;
  interpretCount: number;
  recentContacts: Contact[];
  weeklyActivity: number[];
  sentimentBreakdown: {
    positive: number;
    neutral: number;
    negative: number;
  };
}

export default function Dashboard({ onBack, onViewContact }: DashboardProps) {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      // Get contacts and aggregate stats
      const contacts = await api.getContacts();

      let totalMessages = 0;
      let totalHealingScore = 0;
      let messagesWithScore = 0;
      let transformCount = 0;
      let interpretCount = 0;
      const sentimentBreakdown = { positive: 0, neutral: 0, negative: 0 };

      // Fetch stats for each contact
      for (const contact of contacts.slice(0, 5)) { // Limit to 5 for performance
        try {
          const contactStats = await api.getContactStats(contact.id);
          totalMessages += contactStats.total_messages;
          transformCount += contactStats.transform_count;
          interpretCount += contactStats.interpret_count;

          if (contactStats.avg_healing_score > 0) {
            totalHealingScore += contactStats.avg_healing_score;
            messagesWithScore++;
          }

          sentimentBreakdown.positive += contactStats.sentiment_breakdown.positive;
          sentimentBreakdown.neutral += contactStats.sentiment_breakdown.neutral;
          sentimentBreakdown.negative += contactStats.sentiment_breakdown.negative;
        } catch {
          // Skip if stats fetch fails for a contact
        }
      }

      setStats({
        totalMessages,
        totalContacts: contacts.length,
        avgHealingScore: messagesWithScore > 0 ? totalHealingScore / messagesWithScore : 0,
        transformCount,
        interpretCount,
        recentContacts: contacts.slice(0, 3),
        weeklyActivity: [3, 5, 2, 8, 4, 6, 3], // Placeholder - would need date tracking
        sentimentBreakdown
      });
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 7) return 'text-green-600';
    if (score >= 4) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 8) return 'Excellent';
    if (score >= 6) return 'Good';
    if (score >= 4) return 'Improving';
    return 'Needs Work';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
      <div className="max-w-3xl mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <button
            onClick={onBack}
            className="p-2 hover:bg-white rounded-lg transition-colors"
          >
            <ChevronLeft className="w-6 h-6 text-gray-600" />
          </button>
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-sm text-gray-500">Your communication insights</p>
          </div>
          <BarChart3 className="w-8 h-8 text-blue-600" />
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        {stats && (
          <>
            {/* Main Stats Grid */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              {/* Healing Score */}
              <div className="bg-white rounded-lg p-4 shadow-sm col-span-2">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Heart className="w-5 h-5 text-pink-500" />
                    <span className="text-sm font-medium text-gray-700">Healing Score</span>
                  </div>
                  <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                    stats.avgHealingScore >= 7 ? 'bg-green-100 text-green-700' :
                    stats.avgHealingScore >= 4 ? 'bg-yellow-100 text-yellow-700' :
                    'bg-gray-100 text-gray-600'
                  }`}>
                    {getScoreLabel(stats.avgHealingScore)}
                  </span>
                </div>
                <div className="flex items-end gap-4">
                  <span className={`text-4xl font-bold ${getScoreColor(stats.avgHealingScore)}`}>
                    {stats.avgHealingScore > 0 ? stats.avgHealingScore.toFixed(1) : '—'}
                  </span>
                  <span className="text-gray-500 text-sm mb-1">/ 10</span>
                </div>
                <div className="mt-3 bg-gray-100 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-green-400 to-green-600 h-2 rounded-full transition-all"
                    style={{ width: `${stats.avgHealingScore * 10}%` }}
                  />
                </div>
              </div>

              {/* Total Messages */}
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="flex items-center gap-2 mb-2">
                  <MessageSquare className="w-4 h-4 text-blue-500" />
                  <span className="text-xs text-gray-500">Messages</span>
                </div>
                <span className="text-2xl font-bold text-gray-900">{stats.totalMessages}</span>
              </div>

              {/* Contacts */}
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="flex items-center gap-2 mb-2">
                  <Users className="w-4 h-4 text-purple-500" />
                  <span className="text-xs text-gray-500">Contacts</span>
                </div>
                <span className="text-2xl font-bold text-gray-900">{stats.totalContacts}</span>
              </div>

              {/* Transforms */}
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles className="w-4 h-4 text-blue-500" />
                  <span className="text-xs text-gray-500">Transforms</span>
                </div>
                <span className="text-2xl font-bold text-blue-600">{stats.transformCount}</span>
              </div>

              {/* Interprets */}
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="flex items-center gap-2 mb-2">
                  <Lightbulb className="w-4 h-4 text-green-500" />
                  <span className="text-xs text-gray-500">Interprets</span>
                </div>
                <span className="text-2xl font-bold text-green-600">{stats.interpretCount}</span>
              </div>
            </div>

            {/* Sentiment Breakdown */}
            {stats.totalMessages > 0 && (
              <div className="bg-white rounded-lg p-4 shadow-sm mb-6">
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                  Sentiment Trends
                </h3>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Positive</span>
                      <span className="text-green-600 font-medium">{stats.sentimentBreakdown.positive}</span>
                    </div>
                    <div className="bg-gray-100 rounded-full h-2">
                      <div
                        className="bg-green-500 h-2 rounded-full"
                        style={{ width: `${(stats.sentimentBreakdown.positive / stats.totalMessages) * 100}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Neutral</span>
                      <span className="text-gray-600 font-medium">{stats.sentimentBreakdown.neutral}</span>
                    </div>
                    <div className="bg-gray-100 rounded-full h-2">
                      <div
                        className="bg-gray-400 h-2 rounded-full"
                        style={{ width: `${(stats.sentimentBreakdown.neutral / stats.totalMessages) * 100}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Negative</span>
                      <span className="text-red-600 font-medium">{stats.sentimentBreakdown.negative}</span>
                    </div>
                    <div className="bg-gray-100 rounded-full h-2">
                      <div
                        className="bg-red-500 h-2 rounded-full"
                        style={{ width: `${(stats.sentimentBreakdown.negative / stats.totalMessages) * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Recent Contacts */}
            {stats.recentContacts.length > 0 && (
              <div className="bg-white rounded-lg p-4 shadow-sm mb-6">
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-purple-600" />
                  Recent Contacts
                </h3>
                <div className="space-y-2">
                  {stats.recentContacts.map((contact) => (
                    <button
                      key={contact.id}
                      onClick={() => onViewContact(contact)}
                      className="w-full flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors text-left"
                    >
                      <div>
                        <p className="font-medium text-gray-900">{contact.name}</p>
                        <p className="text-xs text-gray-500 capitalize">{contact.context}</p>
                      </div>
                      <ChevronLeft className="w-4 h-4 text-gray-400 rotate-180" />
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Tips */}
            <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-4 text-white">
              <div className="flex items-start gap-3">
                <Award className="w-6 h-6 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold mb-1">Keep improving!</h3>
                  <p className="text-sm text-blue-100">
                    {stats.avgHealingScore >= 7
                      ? "Your communication is excellent. You're creating a healthier environment for your children."
                      : stats.avgHealingScore >= 4
                      ? "You're making progress! Keep using transforms to improve your messages."
                      : "Every message is a chance to improve. Focus on 'I' statements and your children's needs."}
                  </p>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Empty State */}
        {stats && stats.totalMessages === 0 && (
          <div className="bg-white rounded-lg p-8 shadow-sm text-center">
            <BarChart3 className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="font-semibold text-gray-700 mb-2">No data yet</h3>
            <p className="text-sm text-gray-500">
              Start transforming or interpreting messages to see your communication insights
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
