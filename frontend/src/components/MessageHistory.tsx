import { useState, useEffect } from 'react';
import { Clock, Sparkles, Lightbulb, ChevronLeft, TrendingUp, Copy, Check } from 'lucide-react';
import api from '../api';
import type { Message, Contact, ContactStats } from '../types';

interface MessageHistoryProps {
  contact: Contact;
  onBack: () => void;
}

export default function MessageHistory({ contact, onBack }: MessageHistoryProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [stats, setStats] = useState<ContactStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  useEffect(() => {
    loadHistory();
  }, [contact.id]);

  const loadHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const [historyRes, statsRes] = await Promise.all([
        api.getMessageHistory(contact.id, 100),
        api.getContactStats(contact.id)
      ]);
      setMessages(historyRes.messages);
      setStats(statsRes);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (err) {
      console.error('Copy failed', err);
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    });
  };

  const getSentimentColor = (sentiment?: string) => {
    switch (sentiment) {
      case 'positive': return 'text-green-600 bg-green-50';
      case 'negative': return 'text-red-600 bg-red-50';
      case 'neutral': return 'text-gray-600 bg-gray-50';
      default: return 'text-gray-400 bg-gray-50';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading history...</p>
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
            <h1 className="text-xl font-bold text-gray-900">{contact.name}</h1>
            <p className="text-sm text-gray-500 capitalize">{contact.context} • Message History</p>
          </div>
        </div>

        {/* Stats Card */}
        {stats && (
          <div className="bg-white rounded-lg p-4 shadow-sm mb-6">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold text-blue-600">{stats.total_messages}</p>
                <p className="text-xs text-gray-500">Messages</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-green-600">
                  {stats.avg_healing_score > 0 ? stats.avg_healing_score.toFixed(1) : '—'}
                </p>
                <p className="text-xs text-gray-500">Avg Score</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-purple-600">
                  {stats.sentiment_breakdown.positive}
                </p>
                <p className="text-xs text-gray-500">Positive</p>
              </div>
            </div>

            {/* Sentiment breakdown bar */}
            {stats.total_messages > 0 && (
              <div className="mt-4">
                <div className="flex h-2 rounded-full overflow-hidden bg-gray-100">
                  <div
                    className="bg-green-500"
                    style={{ width: `${(stats.sentiment_breakdown.positive / stats.total_messages) * 100}%` }}
                  />
                  <div
                    className="bg-gray-400"
                    style={{ width: `${(stats.sentiment_breakdown.neutral / stats.total_messages) * 100}%` }}
                  />
                  <div
                    className="bg-red-500"
                    style={{ width: `${(stats.sentiment_breakdown.negative / stats.total_messages) * 100}%` }}
                  />
                </div>
                <div className="flex justify-between mt-1 text-xs text-gray-500">
                  <span>Positive</span>
                  <span>Neutral</span>
                  <span>Negative</span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        {/* Messages */}
        {messages.length === 0 ? (
          <div className="bg-white rounded-lg p-8 shadow-sm text-center">
            <Clock className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="font-semibold text-gray-700 mb-2">No messages yet</h3>
            <p className="text-sm text-gray-500">
              Transform or interpret a message to start building your history
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((msg) => (
              <div key={msg.id} className="bg-white rounded-lg p-4 shadow-sm">
                {/* Message header */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    {msg.type === 'transform' ? (
                      <Sparkles className="w-4 h-4 text-blue-600" />
                    ) : (
                      <Lightbulb className="w-4 h-4 text-green-600" />
                    )}
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                      msg.type === 'transform' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'
                    }`}>
                      {msg.type === 'transform' ? 'Transformed' : 'Interpreted'}
                    </span>
                    {msg.sentiment && (
                      <span className={`text-xs px-2 py-0.5 rounded-full ${getSentimentColor(msg.sentiment)}`}>
                        {msg.sentiment}
                      </span>
                    )}
                  </div>
                  <span className="text-xs text-gray-400">{formatDate(msg.created_at)}</span>
                </div>

                {/* Original message */}
                <div className="mb-3">
                  <p className="text-xs text-gray-500 mb-1">Original:</p>
                  <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">{msg.original}</p>
                </div>

                {/* Result */}
                {msg.result && (
                  <div className="mb-3">
                    <p className="text-xs text-gray-500 mb-1">
                      {msg.type === 'transform' ? 'Transformed:' : 'Interpretation:'}
                    </p>
                    <div className={`p-3 rounded-lg ${
                      msg.type === 'transform' ? 'bg-blue-50' : 'bg-green-50'
                    }`}>
                      <p className="text-sm text-gray-800">{msg.result}</p>
                      <button
                        onClick={() => handleCopy(msg.result!, msg.id)}
                        className="mt-2 text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
                      >
                        {copiedId === msg.id ? (
                          <>
                            <Check className="w-3 h-3" /> Copied
                          </>
                        ) : (
                          <>
                            <Copy className="w-3 h-3" /> Copy
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                )}

                {/* Footer with healing score */}
                {msg.healing_score !== undefined && msg.healing_score !== null && (
                  <div className="flex items-center gap-2 pt-2 border-t">
                    <TrendingUp className="w-4 h-4 text-green-600" />
                    <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                      <div
                        className="bg-green-600 h-1.5 rounded-full"
                        style={{ width: `${msg.healing_score * 10}%` }}
                      />
                    </div>
                    <span className="text-xs font-medium text-gray-600">
                      {msg.healing_score}/10
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
