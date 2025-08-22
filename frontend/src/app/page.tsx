"use client";

import React, { useState, useEffect } from 'react';
import { Heart, MessageCircle, Users, Settings, BarChart3, Send, Copy, Sparkles, User, Plus, Search, Filter, ArrowRight, Star, Clock, CheckCircle, ChevronDown } from 'lucide-react';

const API_BASE = 'http://100.71.78.118:8000';

export default function TheThirdVoiceApp() {
  const [currentPage, setCurrentPage] = useState('landing');
  const [activeTab, setActiveTab] = useState('Analyze Message');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [contacts, setContacts] = useState([]);
  const [selectedRelationship, setSelectedRelationship] = useState('Co-parent');
  
  // Form states
  const [messageText, setMessageText] = useState('');
  const [transformedMessage, setTransformedMessage] = useState('');
  const [interpretedMessage, setInterpretedMessage] = useState('');
  const [healingScore, setHealingScore] = useState(0);

  const relationshipTypes = [
    'Co-parent',
    'Partner',
    'Spouse',
    'Ex-partner',
    'Family Member',
    'Friend',
    'Colleague',
    'Other'
  ];

  // Demo authentication
  const startDemo = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/auth/demo`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      
      if (response.ok) {
        const data = await response.json();
        setUser({ 
          name: 'Demo User', 
          email: 'demo@thirdvoice.ai', 
          isDemo: true,
          token: data.access_token 
        });
        setCurrentPage('main');
        loadContacts();
      }
    } catch (error) {
      console.error('Demo start failed:', error);
    }
    setLoading(false);
  };

  const loadContacts = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/contacts/`, {
        headers: { 'Content-Type': 'application/json' },
      });
      if (response.ok) {
        const data = await response.json();
        setContacts(data);
      }
    } catch (error) {
      console.error('Failed to load contacts:', error);
    }
  };

  const processMessage = async (type) => {
    if (!messageText.trim()) return;
    
    setLoading(true);
    try {
      const endpoint = type === 'transform' ? '/api/messages/quick-transform' : '/api/messages/quick-interpret';
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageText,
          context: selectedRelationship.toLowerCase(),
          contact_name: selectedRelationship
        }),
      });

      if (response.ok) {
        const data = await response.json();
        if (type === 'transform') {
          setTransformedMessage(data.transformed_message);
          setHealingScore(data.healing_score || 8);
        } else {
          setInterpretedMessage(data.interpretation);
        }
      } else {
        // Fallback responses for demo
        if (type === 'transform') {
          setTransformedMessage(`I understand you're feeling frustrated. Could we talk about this together and find a solution that works for both of us?`);
          setHealingScore(8);
        } else {
          setInterpretedMessage(`They may be feeling unheard or overwhelmed. Behind the frustration, they might need support or reassurance.`);
        }
      }
    } catch (error) {
      console.error(`${type} failed:`, error);
      if (type === 'transform') {
        setTransformedMessage(`I'd love to discuss this with you. Can we find a time to talk about what's important to both of us?`);
        setHealingScore(7);
      } else {
        setInterpretedMessage(`This message suggests they may be feeling stressed or need more connection. Consider responding with empathy.`);
      }
    }
    setLoading(false);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  // Landing Page Component
  const LandingPage = () => (
    <div className="min-h-screen bg-gradient-to-br from-violet-900 via-purple-900 to-indigo-900">
      <div className="container mx-auto px-6 py-12">
        {/* Hero Section */}
        <div className="text-center text-white mb-16">
          <div className="flex justify-center mb-8">
            <div className="bg-white/10 backdrop-blur-lg rounded-full p-6 shadow-2xl">
              <Heart className="w-16 h-16 text-pink-300" />
            </div>
          </div>
          
          <h1 className="text-6xl md:text-8xl font-bold mb-6 bg-gradient-to-r from-white via-pink-200 to-violet-200 bg-clip-text text-transparent">
            The Third Voice
          </h1>
          
          <p className="text-2xl md:text-3xl font-light mb-8 text-violet-200">
            Your AI companion for emotionally intelligent communication.
          </p>
          
          <p className="text-xl mb-12 text-violet-300 max-w-3xl mx-auto">
            When both people are speaking from pain, someone must be the third voice. 
            Let AI help you communicate with love, understanding, and healing.
          </p>

          {/* CTA Button */}
          <button
            onClick={startDemo}
            disabled={loading}
            className="group bg-gradient-to-r from-pink-500 to-violet-600 hover:from-pink-600 hover:to-violet-700 text-white font-bold py-6 px-12 rounded-2xl text-xl transition-all duration-300 transform hover:scale-105 shadow-2xl disabled:opacity-50"
          >
            {loading ? (
              <div className="flex items-center space-x-3">
                <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Starting your journey...</span>
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <Sparkles className="w-6 h-6" />
                <span>Try Demo - No Signup Required</span>
                <ArrowRight className="w-6 h-6 transition-transform group-hover:translate-x-1" />
              </div>
            )}
          </button>
          
          <p className="text-violet-400 mt-4">
            ⚡ Instant access • 🚫 No email required • ✨ See results immediately
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-8 text-center hover:bg-white/10 transition-all duration-300">
            <MessageCircle className="w-12 h-12 text-pink-400 mx-auto mb-4" />
            <h3 className="text-2xl font-semibold text-white mb-3">Transform</h3>
            <p className="text-violet-300">
              Turn harsh words into loving communication. "You never help!" becomes 
              "I'd love your support with this."
            </p>
          </div>

          <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-8 text-center hover:bg-white/10 transition-all duration-300">
            <BarChart3 className="w-12 h-12 text-blue-400 mx-auto mb-4" />
            <h3 className="text-2xl font-semibold text-white mb-3">Interpret</h3>
            <p className="text-violet-300">
              Understand the emotions and needs behind difficult messages. 
              See past the words to the heart.
            </p>
          </div>

          <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-8 text-center hover:bg-white/10 transition-all duration-300">
            <Heart className="w-12 h-12 text-red-400 mx-auto mb-4" />
            <h3 className="text-2xl font-semibold text-white mb-3">Heal</h3>
            <p className="text-violet-300">
              Strengthen relationships through empathetic communication. 
              Every message is a chance to connect deeper.
            </p>
          </div>
        </div>

        {/* Mission Statement */}
        <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-3xl p-12 text-center">
          <h2 className="text-3xl font-bold text-white mb-6">Built with Love, Powered by AI</h2>
          <p className="text-xl text-violet-200 mb-8 max-w-4xl mx-auto">
            Born from the desire to heal relationships and bring families together. 
            Every transformed message is a step toward better understanding, 
            every healed conversation brings people closer.
          </p>
          <div className="flex justify-center items-center space-x-8 text-violet-300">
            <div className="text-center">
              <div className="text-3xl font-bold text-white">37+</div>
              <div className="text-sm">AI Endpoints</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white">∞</div>
              <div className="text-sm">Healing Potential</div>
            </div>
            <div className="text-center">
              <Heart className="w-8 h-8 text-pink-400 mx-auto" />
              <div className="text-sm mt-1">For Every Family</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Main App Interface (matches the screenshot)
  const MainInterface = () => (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-3xl p-8 shadow-sm">
          <div className="flex items-center justify-between mb-8">
            <div className="flex flex-col items-center w-full">
              <div className="bg-purple-50 rounded-full p-4 mb-6">
                <Heart className="w-12 h-12 text-purple-800" />
              </div>
              <h1 className="text-3xl font-bold text-black mb-2">The Third Voice AI</h1>
              <p className="text-gray-500 text-center">
                Your AI companion for emotionally intelligent communication.
              </p>
            </div>
            <div className="absolute top-8 right-8 bg-gray-100 rounded-full p-3">
              <User className="w-5 h-5 text-gray-700" />
            </div>
          </div>

          {/* Relationship Selector */}
          <div className="mb-8">
            <label className="block text-lg font-medium text-black mb-4">
              First, who are you communicating with?
            </label>
            <div className="relative">
              <select 
                value={selectedRelationship}
                onChange={(e) => setSelectedRelationship(e.target.value)}
                className="w-full p-4 pr-10 bg-white border border-gray-300 rounded-xl focus:ring-2 focus:ring-gray-400 focus:border-gray-400 appearance-none text-black text-lg"
              >
                {relationshipTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
              <ChevronDown className="absolute right-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
            </div>
          </div>

          {/* Tab Buttons */}
          <div className="flex space-x-2 bg-gray-100 rounded-xl p-2 mb-8">
            <button
              onClick={() => setActiveTab('Analyze Message')}
              className={`flex-1 py-3 px-6 rounded-lg font-medium transition-all ${
                activeTab === 'Analyze Message' 
                  ? 'bg-white text-black shadow-sm' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Analyze Message
            </button>
            <button
              onClick={() => setActiveTab('Transform Message')}
              className={`flex-1 py-3 px-6 rounded-lg font-medium transition-all ${
                activeTab === 'Transform Message' 
                  ? 'bg-white text-black shadow-sm' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Transform Message
            </button>
          </div>

          {/* Message Input Area */}
          <div className="mb-6">
            <textarea
              value={messageText}
              onChange={(e) => setMessageText(e.target.value)}
              placeholder={activeTab === 'Analyze Message' 
                ? "Paste the message you received here..." 
                : "Type the message you want to send here..."
              }
              className="w-full p-6 border border-gray-300 rounded-xl focus:ring-2 focus:ring-gray-400 focus:border-gray-400 resize-none text-black placeholder-gray-400 text-lg"
              rows={8}
            />
          </div>

          {/* Action Button */}
          <button
            onClick={() => processMessage(activeTab === 'Transform Message' ? 'transform' : 'interpret')}
            disabled={!messageText.trim() || loading}
            className="w-full bg-purple-200 text-purple-800 py-4 px-6 rounded-xl font-medium text-lg hover:bg-purple-300 disabled:opacity-50 transition-all duration-200 flex items-center justify-center space-x-3"
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-purple-800/30 border-t-purple-800 rounded-full animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                <span>{activeTab === 'Transform Message' ? 'Transform' : 'Analyze'}</span>
              </>
            )}
          </button>
        </div>

        {/* Results Display */}
        {(transformedMessage || interpretedMessage) && (
          <div className="mt-6 bg-white rounded-3xl p-8 shadow-sm">
            {activeTab === 'Transform Message' && transformedMessage && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-semibold text-green-700 flex items-center">
                    <CheckCircle className="w-6 h-6 mr-2" />
                    Transformed Message
                  </h3>
                  <div className="flex items-center space-x-2 bg-yellow-50 px-3 py-1 rounded-full">
                    <Star className="w-4 h-4 text-yellow-500" />
                    <span className="text-sm font-medium text-yellow-700">
                      Healing Score: {healingScore}/10
                    </span>
                  </div>
                </div>
                
                <div className="bg-gray-50 rounded-xl p-6 border border-gray-200 mb-4">
                  <p className="text-black leading-relaxed text-lg">{transformedMessage}</p>
                </div>
                
                <button
                  onClick={() => copyToClipboard(transformedMessage)}
                  className="bg-gray-800 text-white px-6 py-3 rounded-lg hover:bg-gray-700 transition-colors flex items-center space-x-2 font-medium"
                >
                  <Copy className="w-4 h-4" />
                  <span>Copy Message</span>
                </button>
              </div>
            )}

            {activeTab === 'Analyze Message' && interpretedMessage && (
              <div>
                <h3 className="text-xl font-semibold text-blue-700 flex items-center mb-6">
                  <BarChart3 className="w-6 h-6 mr-2" />
                  Message Analysis
                </h3>
                
                <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
                  <p className="text-black leading-relaxed text-lg">{interpretedMessage}</p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Demo Notice */}
        <div className="mt-8 text-center">
          <div className="inline-flex items-center space-x-2 bg-gray-100 text-gray-600 px-4 py-2 rounded-full text-sm font-medium">
            <Sparkles className="w-4 h-4" />
            <span>Demo Mode</span>
          </div>
        </div>
      </div>
    </div>
  );

  if (user) {
    return <MainInterface />;
  }

  return <LandingPage />;
}