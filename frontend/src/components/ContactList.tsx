import { useState, useEffect } from 'react';
import { Users, Plus, ChevronRight, History, Trash2, X } from 'lucide-react';
import api from '../api';
import type { Contact } from '../types';

interface ContactListProps {
  onSelectContact: (contact: Contact) => void;
  onBack: () => void;
}

const CONTEXT_OPTIONS = [
  { value: 'coparenting', label: 'Co-Parent', emoji: '👨‍👩‍👧' },
  { value: 'family', label: 'Family', emoji: '👪' },
  { value: 'romantic', label: 'Partner', emoji: '💕' },
  { value: 'friend', label: 'Friend', emoji: '🤝' },
  { value: 'workplace', label: 'Work', emoji: '💼' }
];

export default function ContactList({ onSelectContact, onBack }: ContactListProps) {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newName, setNewName] = useState('');
  const [newContext, setNewContext] = useState('coparenting');
  const [adding, setAdding] = useState(false);

  useEffect(() => {
    loadContacts();
  }, []);

  const loadContacts = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getContacts();
      setContacts(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleAddContact = async () => {
    if (!newName.trim()) return;

    setAdding(true);
    try {
      const contact = await api.createContact(newName.trim(), newContext);
      setContacts([contact, ...contacts]);
      setNewName('');
      setNewContext('coparenting');
      setShowAddForm(false);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setAdding(false);
    }
  };

  const handleDeleteContact = async (contactId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Delete this contact and all message history?')) return;

    try {
      await api.deleteContact(contactId);
      setContacts(contacts.filter(c => c.id !== contactId));
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const getContextEmoji = (context: string) => {
    return CONTEXT_OPTIONS.find(c => c.value === context)?.emoji || '👤';
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'No messages';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading contacts...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
      <div className="max-w-3xl mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <History className="w-8 h-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Message History</h1>
              <p className="text-sm text-gray-500">View past conversations</p>
            </div>
          </div>
          <button
            onClick={() => setShowAddForm(true)}
            className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        {/* Add Contact Form */}
        {showAddForm && (
          <div className="bg-white rounded-lg p-4 shadow-sm mb-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">Add Contact</h3>
              <button onClick={() => setShowAddForm(false)} className="text-gray-400 hover:text-gray-600">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="e.g., Alex (co-parent)"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Relationship</label>
                <div className="grid grid-cols-3 gap-2">
                  {CONTEXT_OPTIONS.map((opt) => (
                    <button
                      key={opt.value}
                      onClick={() => setNewContext(opt.value)}
                      className={`p-2 rounded-lg text-sm font-medium transition-colors ${
                        newContext === opt.value
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {opt.emoji} {opt.label}
                    </button>
                  ))}
                </div>
              </div>
              <button
                onClick={handleAddContact}
                disabled={!newName.trim() || adding}
                className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:bg-gray-300"
              >
                {adding ? 'Adding...' : 'Add Contact'}
              </button>
            </div>
          </div>
        )}

        {/* Contact List */}
        {contacts.length === 0 ? (
          <div className="bg-white rounded-lg p-8 shadow-sm text-center">
            <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="font-semibold text-gray-700 mb-2">No contacts yet</h3>
            <p className="text-sm text-gray-500 mb-4">
              Add a contact to start tracking your communication history
            </p>
            <button
              onClick={() => setShowAddForm(true)}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              Add First Contact
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {contacts.map((contact) => (
              <div
                key={contact.id}
                onClick={() => onSelectContact(contact)}
                className="bg-white rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer flex items-center gap-4"
              >
                <div className="text-2xl">{getContextEmoji(contact.context)}</div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 truncate">{contact.name}</h3>
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <span className="capitalize">{contact.context}</span>
                    {contact.message_count !== undefined && (
                      <>
                        <span>•</span>
                        <span>{contact.message_count} messages</span>
                      </>
                    )}
                    {contact.last_message_date && (
                      <>
                        <span>•</span>
                        <span>{formatDate(contact.last_message_date)}</span>
                      </>
                    )}
                  </div>
                </div>
                <button
                  onClick={(e) => handleDeleteContact(contact.id, e)}
                  className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
                <ChevronRight className="w-5 h-5 text-gray-400" />
              </div>
            ))}
          </div>
        )}

        {/* Back button */}
        <button
          onClick={onBack}
          className="fixed bottom-4 left-4 bg-white text-gray-700 px-4 py-2 rounded-full shadow-lg hover:shadow-xl transition-shadow text-sm font-medium"
        >
          ← Back
        </button>
      </div>
    </div>
  );
}
