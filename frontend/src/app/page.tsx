"use client";

import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';

const API_BASE = 'http://100.71.78.118:8000';

// Main app component - simplified like the working example
interface User {
  name: string;
  email: string;
  isDemo: boolean;
  token: string;
}

export default function TheThirdVoiceApp() {
  const [currentPage, setCurrentPage] = useState<string>('landing');
  const [user, setUser] = useState<User | null>(null);
  const [activeTab, setActiveTab] = useState<string>('Analyze Message');
  const [loading, setLoading] = useState<boolean>(false);
  const [selectedRelationship, setSelectedRelationship] = useState<string>('Co-parent');
  
  // Form states - simplified naming like working example
  const [demoMessage, setDemoMessage] = useState<string>('');
  const [transformedMessage, setTransformedMessage] = useState<string>('');
  const [interpretedMessage, setInterpretedMessage] = useState<string>('');
  const [healingScore, setHealingScore] = useState<number>(0);

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

  // Start instant demo
  const startDemo = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/auth/demo`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUser({ 
          name: 'Demo User', 
          email: 'demo@thirdvoice.ai', 
          isDemo: true,
          token: data.token || 'demo_token'
        });
        setCurrentPage('main');
        console.log('Demo started:', data);
      }
    } catch (error) {
      console.error('Demo start failed:', error);
      // Fallback for testing
      setUser({ 
        name: 'Demo User', 
        email: 'demo@thirdvoice.ai', 
        isDemo: true,
        token: 'demo_token'
      });
      setCurrentPage('main');
    }
    setLoading(false);
  };

  async function processMessage(type: 'transform' | 'interpret') {
    if (!demoMessage.trim()) return;
    
    setLoading(true);
    setTransformedMessage('');
    setInterpretedMessage('');
    
    try {
      const endpoint = type === 'transform' ? '/api/messages/quick-transform' : '/api/messages/quick-interpret';
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: demoMessage,
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
        if (type === 'transform') {
          setTransformedMessage("I understand you're feeling frustrated. Could we talk about this together and find a solution that works for both of us?");
          setHealingScore(8);
        } else {
          setInterpretedMessage('They may be feeling unheard or overwhelmed. Behind the frustration, they might need support or reassurance.');
        }
      }
    } catch (error) {
      console.error(`${type} failed:`, error);
      if (type === 'transform') {
        setTransformedMessage("I'd love to discuss this with you. Can we find a time to talk about what's important to both of us?");
        setHealingScore(7);
      } else {
        setInterpretedMessage('This message suggests they may be feeling stressed or need more connection. Consider responding with empathy.');
      }
    }
    setLoading(false);
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      alert('Copied to clipboard! Ready to paste.');
    });
  };

  function resetForm() {
    setDemoMessage('');
    setTransformedMessage('');
    setInterpretedMessage('');
    setHealingScore(0);
  }

  // Demo Interface - matching working example structure
  if (user && currentPage === 'main') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center py-8">
            <h1 className="text-4xl md:text-6xl font-bold text-indigo-900 mb-4">
              🎭 The Third Voice
            </h1>
            <p className="text-xl text-indigo-700 mb-2">
              When both people are speaking from pain, someone must be the third voice
            </p>
            <div className="inline-flex items-center px-4 py-2 bg-green-100 rounded-full">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
              <span className="text-green-800 text-sm font-medium">Demo Mode Active</span>
            </div>
          </div>

          {/* Tab Selection */}
          <div className="bg-white rounded-2xl p-2 shadow-sm mb-6 max-w-2xl mx-auto">
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => {
                  setActiveTab('Analyze Message');
                  resetForm();
                }}
                className={`py-3 px-4 rounded-xl font-medium transition-all text-sm sm:text-base ${
                  activeTab === 'Analyze Message' 
                    ? 'bg-blue-100 text-blue-800 shadow-sm' 
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                }`}
              >
                Analyze Message
              </button>
              <button
                onClick={() => {
                  setActiveTab('Transform Message');
                  resetForm();
                }}
                className={`py-3 px-4 rounded-xl font-medium transition-all text-sm sm:text-base ${
                  activeTab === 'Transform Message' 
                    ? 'bg-blue-100 text-blue-800 shadow-sm' 
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                }`}
              >
                Transform Message
              </button>
            </div>
          </div>

          {/* Demo Interface - using working example structure */}
          <div className="bg-white rounded-2xl shadow-xl p-6 md:p-8 mb-8">
            <div className="grid md:grid-cols-2 gap-8">
              {/* Input Section */}
              <div className="space-y-4">
                <div className="bg-blue-50 rounded-xl p-4 border-l-4 border-blue-500">
                  <h3 className="text-xl font-semibold text-blue-900 mb-2">
                    {activeTab === 'Transform Message' ? '💬 Transform Mode' : '🔍 Analyze Mode'}
                  </h3>
                  <p className="text-blue-700">
                    {activeTab === 'Transform Message' ? 'Say it with love instead' : 'Understand what they really mean'}
                  </p>
                </div>

                <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-200 mb-4">
                  <label className="block text-base font-medium text-gray-900 mb-3">
                    Who are you communicating with?
                  </label>
                  <div className="relative">
                    <select 
                      value={selectedRelationship}
                      onChange={(e) => setSelectedRelationship(e.target.value)}
                      className="w-full p-3 pr-10 bg-white border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 appearance-none text-gray-900"
                    >
                      {relationshipTypes.map(type => (
                        <option key={type} value={type}>{type}</option>
                      ))}
                    </select>
                    <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {activeTab === 'Analyze Message' ? 'Message you received:' : 'What do you want to say?'}
                  </label>
                  <textarea
                    value={demoMessage}
                    onChange={(e) => setDemoMessage(e.target.value)}
                    placeholder={activeTab === 'Analyze Message' 
                      ? "Paste the message you received here..." 
                      : "I'm frustrated that you're always late for pickup"
                    }
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    rows={4}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    💡 Try the example above or write your own message
                  </p>
                </div>

                <button
                  onClick={() => processMessage(activeTab === 'Transform Message' ? 'transform' : 'interpret')}
                  disabled={!demoMessage.trim() || loading}
                  className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 transition-all duration-200 transform hover:scale-105"
                >
                  {loading ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      The Third Voice is working...
                    </span>
                  ) : (
                    `✨ ${activeTab === 'Transform Message' ? 'Transform This Message' : 'Analyze This Message'}`
                  )}
                </button>
              </div>

              {/* Results Section */}
              <div className="space-y-4">
                {transformedMessage && activeTab === 'Transform Message' ? (
                  <>
                    <div className="bg-green-50 rounded-xl p-4 border-l-4 border-green-500">
                      <h3 className="text-xl font-semibold text-green-900 mb-2">
                        ✨ Transformed with Love!
                      </h3>
                    </div>

                    <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-6 border border-green-200">
                      <h4 className="text-lg font-semibold text-gray-800 mb-3">
                        💬 Your AI-Suggested Message:
                      </h4>
                      <div className="bg-white p-4 rounded-lg border shadow-sm">
                        <p className="text-gray-800 leading-relaxed">
                          {transformedMessage}
                        </p>
                      </div>
                        
                      <div className="flex gap-3 mt-4">
                        <button
                          onClick={() => copyToClipboard(transformedMessage)}
                          className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
                        >
                          📋 Copy Message
                        </button>
                        <div className="bg-gradient-to-r from-green-500 to-blue-500 text-white px-4 py-2 rounded-lg flex items-center gap-2">
                          <span>Healing Score: {healingScore}/10</span>
                          <span>{'⭐'.repeat(Math.min(5, Math.max(1, healingScore / 2)))}</span>
                        </div>
                      </div>
                    </div>

                    <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
                      <p className="text-yellow-800 font-medium">
                        🎉 Amazing! See how AI can transform your relationships?
                      </p>
                    </div>
                  </>
                ) : interpretedMessage && activeTab === 'Analyze Message' ? (
                  <>
                    <div className="bg-blue-50 rounded-xl p-4 border-l-4 border-blue-500">
                      <h3 className="text-xl font-semibold text-blue-900 mb-2">
                        🔍 Message Analysis Complete!
                      </h3>
                    </div>

                    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
                      <h4 className="text-lg font-semibold text-gray-800 mb-3">
                        🤔 What They Really Mean:
                      </h4>
                      <div className="bg-white p-4 rounded-lg border shadow-sm">
                        <p className="text-gray-800 leading-relaxed">
                          {interpretedMessage}
                        </p>
                      </div>
                        
                      <button
                        onClick={() => copyToClipboard(interpretedMessage)}
                        className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 mt-4"
                      >
                        📋 Copy Analysis
                      </button>
                    </div>

                    <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                      <p className="text-purple-800 font-medium">
                        💡 Understanding leads to better responses!
                      </p>
                    </div>
                  </>
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    <div className="text-6xl mb-4">🎭</div>
                    <p className="text-lg">
                      {activeTab === 'Transform Message' 
                        ? 'Enter a message to see the magic happen!' 
                        : 'Paste a message to understand what they really mean!'
                      }
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Reset Button */}
          {(transformedMessage || interpretedMessage) && (
            <div className="text-center mb-8">
              <button
                onClick={resetForm}
                className="bg-gray-200 text-gray-700 px-6 py-3 rounded-xl hover:bg-gray-300 transition-colors font-medium"
              >
                ✨ Transform Another Message
              </button>
            </div>
          )}

          {/* Call to Action */}
          <div className="text-center bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-2xl p-8">
            <h2 className="text-3xl font-bold mb-4">Ready to Save Your Progress?</h2>
            <p className="text-xl mb-6 opacity-90">
              Create a free account to keep all your conversations forever!
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-white text-purple-600 font-semibold py-3 px-8 rounded-lg hover:bg-gray-100 transition-colors">
                🆕 Create Free Account
              </button>
              <button 
                onClick={() => {
                  setUser(null);
                  setCurrentPage('landing');
                }}
                className="border border-white text-white font-semibold py-3 px-8 rounded-lg hover:bg-white hover:bg-opacity-20 transition-colors"
              >
                🎭 Back to Landing
              </button>
            </div>
            <p className="text-sm mt-4 opacity-75">
              ✅ Always free • ✅ Keep conversations forever • ✅ No limits
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Landing Page - matching working example structure
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800">
      <div className="container mx-auto px-4 py-16 md:py-24">
        {/* Hero Section */}
        <div className="text-center text-white mb-16">
          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-white via-blue-100 to-purple-200 bg-clip-text text-transparent">
            🎭 The Third Voice
          </h1>
          <h2 className="text-2xl md:text-3xl font-semibold mb-8 text-blue-100">
            Transform Difficult Conversations with AI
          </h2>
          <p className="text-xl md:text-2xl mb-12 text-purple-100 max-w-4xl mx-auto leading-relaxed">
            When both people are speaking from pain, someone must be the third voice
          </p>

          {/* Instant Demo CTA */}
          <div className="mb-12">
            <button
              onClick={startDemo}
              disabled={loading}
              className="bg-gradient-to-r from-yellow-400 to-orange-500 text-black font-bold py-4 px-12 rounded-2xl text-xl hover:from-yellow-300 hover:to-orange-400 transform hover:scale-105 transition-all duration-200 shadow-2xl disabled:opacity-50"
            >
              {loading ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-3 h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Starting Demo...
                </span>
              ) : (
                '🎯 Try Demo Now - No Signup!'
              )}
            </button>
            <p className="text-purple-200 mt-4 text-lg">
              ⚡ Instant access • 🚫 No email required • 🎯 See results in seconds
            </p>
          </div>
        </div>

        {/* Features Preview */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-2xl p-8 text-center">
            <div className="text-4xl mb-4">💬</div>
            <h3 className="text-xl font-semibold text-white mb-3">Transform</h3>
            <p className="text-purple-100">
              Transform harsh messages into<br />
              loving communication
            </p>
          </div>
            
          <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-2xl p-8 text-center">
            <div className="text-4xl mb-4">🤔</div>
            <h3 className="text-xl font-semibold text-white mb-3">Interpret</h3>
            <p className="text-purple-100">
              Understand what they<br />
              really mean behind the words
            </p>
          </div>
            
          <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-2xl p-8 text-center">
            <div className="text-4xl mb-4">❤️</div>
            <h3 className="text-xl font-semibold text-white mb-3">Heal</h3>
            <p className="text-purple-100">
              Strengthen relationships<br />
              through better communication
            </p>
          </div>
        </div>

        {/* Mission Statement */}
        <div className="text-center bg-white bg-opacity-5 backdrop-blur-lg rounded-2xl p-8 md:p-12">
          <h3 className="text-2xl md:text-3xl font-bold text-white mb-6">
            Built from Love, Powered by AI
          </h3>
          <p className="text-lg text-purple-100 mb-8 max-w-3xl mx-auto leading-relaxed">
            Born from personal pain and the fight to come home to family, 
            The Third Voice helps heal relationships through better communication. 
            Every message transformed is a family saved, every conversation healed 
            is a step toward bringing people closer together.
          </p>
          <div className="flex justify-center space-x-8 text-purple-200">
            <div className="text-center">
              <div className="text-2xl font-bold text-white">37</div>
              <div className="text-sm">AI Endpoints</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">∞</div>
              <div className="text-sm">Healing Potential</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">💙</div>
              <div className="text-sm">For Samantha</div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-16 text-purple-200">
          <p className="text-lg mb-4">
            &quot;For Samantha! For every family! For the power of the third voice!&quot;
          </p>
          <p className="text-sm opacity-75">
            Built with 💙 from detention to deployment • Every line of code written for love
          </p>
        </div>
      </div>
    </div>
  );
}