"use client";

import React, { useState, useRef } from 'react';
import { Heart, MessageCircle, BarChart3, Send, Copy, Sparkles, User, ChevronDown, CheckCircle, Star, ArrowRight, Loader2 } from 'lucide-react';

const API_BASE = 'http://100.71.78.118:8000';

interface User {
  name: string;
  email: string;
  isDemo: boolean;
  token: string;
}

export default function TheThirdVoiceApp() {
  const [currentPage, setCurrentPage] = useState<string>('landing');
  const [activeTab, setActiveTab] = useState<string>('Analyze Message');
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [selectedRelationship, setSelectedRelationship] = useState<string>('Co-parent');
  
  // Form states
  const [messageText, setMessageText] = useState<string>('');
  const [transformedMessage, setTransformedMessage] = useState<string>('');
  const [interpretedMessage, setInterpretedMessage] = useState<string>('');
  const [healingScore, setHealingScore] = useState<number>(0);
  
  const textAreaRef = useRef<HTMLTextAreaElement>(null);

  // Properly typed event handlers
  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessageText(e.target.value);
  };

  const handleInputInteraction = (e: React.TouchEvent<HTMLTextAreaElement> | React.FocusEvent<HTMLTextAreaElement>) => {
    // Removed focus() call to avoid keyboard retraction on Android
  };

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

  // Demo authentication - simplified version that always works
  const startDemo = () => {
    setLoading(true);
    
    // For demo purposes, just set user immediately
    setTimeout(() => {
      setUser({ 
        name: 'Demo User', 
        email: 'demo@thirdvoice.ai', 
        isDemo: true,
        token: 'demo_token'
      });
      setCurrentPage('main');
      setLoading(false);
    }, 500); // Small delay to show loading state
  };

  const processMessage = async (type: 'transform' | 'interpret') => {
    if (!messageText.trim()) return;
    
    setLoading(true);
    setTransformedMessage('');
    setInterpretedMessage('');
    
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
          setTransformedMessage('I understand you\'re feeling frustrated. Could we talk about this together and find a solution that works for both of us?');
          setHealingScore(8);
        } else {
          setInterpretedMessage('They may be feeling unheard or overwhelmed. Behind the frustration, they might need support or reassurance.');
        }
      }
    } catch (error) {
      console.error(`${type} failed:`, error);
      if (type === 'transform') {
        setTransformedMessage('I\'d love to discuss this with you. Can we find a time to talk about what\'s important to both of us?');
        setHealingScore(7);
      } else {
        setInterpretedMessage('This message suggests they may be feeling stressed or need more connection. Consider responding with empathy.');
      }
    }
    setLoading(false);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const resetForm = () => {
    setMessageText('');
    setTransformedMessage('');
    setInterpretedMessage('');
    setHealingScore(0);
  };

  // Landing Page Component
  const LandingPage = () => (
    <div className="min-h-screen bg-gradient-to-br from-violet-900 via-purple-900 to-indigo-900">
      <div className="container mx-auto px-4 sm:px-6 py-8 sm:py-12">
        <div className="text-center text-white mb-12 sm:mb-16">
          <div className="flex justify-center mb-6 sm:mb-8">
            <div className="bg-white/10 backdrop-blur-lg rounded-full p-4 sm:p-6 shadow-2xl">
              <Heart className="w-12 h-12 sm:w-16 sm:h-16 text-pink-300" />
            </div>
          </div>
          
          <h1 className="text-4xl sm:text-6xl md:text-8xl font-bold mb-4 sm:mb-6 bg-gradient-to-r from-white via-pink-200 to-violet-200 bg-clip-text text-transparent leading-tight">
            The Third Voice
          </h1>
          
          <p className="text-lg sm:text-2xl md:text-3xl font-light mb-6 sm:mb-8 text-violet-200 px-2">
            Your AI companion for emotionally intelligent communication.
          </p>
          
          <p className="text-base sm:text-xl mb-8 sm:mb-12 text-violet-300 max-w-3xl mx-auto px-4">
            When both people are speaking from pain, someone must be the third voice. 
            Let AI help you communicate with love, understanding, and healing.
          </p>

          <button
            onClick={startDemo}
            disabled={loading}
            className="w-full sm:w-auto group bg-gradient-to-r from-pink-500 to-violet-600 hover:from-pink-600 hover:to-violet-700 text-white font-bold py-4 sm:py-6 px-8 sm:px-12 rounded-2xl text-lg sm:text-xl transition-all duration-300 transform hover:scale-105 shadow-2xl disabled:opacity-50 mx-4"
          >
            {loading ? (
              <div className="flex items-center justify-center space-x-3">
                <Loader2 className="w-6 h-6 animate-spin" />
                <span>Starting your journey...</span>
              </div>
            ) : (
              <div className="flex items-center justify-center space-x-3">
                <Sparkles className="w-6 h-6" />
                <span>Try Demo - No Signup Required</span>
                <ArrowRight className="w-6 h-6 transition-transform group-hover:translate-x-1" />
              </div>
            )}
          </button>
          
          <p className="text-violet-400 mt-4 text-sm sm:text-base px-4">
            ⚡ Instant access • 🚫 No email required • ✨ See results immediately
          </p>
        </div>

        <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-6 sm:gap-8 mb-12 sm:mb-16 px-2">
          <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6 sm:p-8 text-center hover:bg-white/10 transition-all duration-300">
            <MessageCircle className="w-10 h-10 sm:w-12 sm:h-12 text-pink-400 mx-auto mb-4" />
            <h3 className="text-xl sm:text-2xl font-semibold text-white mb-3">Transform</h3>
            <p className="text-violet-300 text-sm sm:text-base">
              Turn harsh words into loving communication. Transform negative messages into positive ones.
            </p>
          </div>

          <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6 sm:p-8 text-center hover:bg-white/10 transition-all duration-300">
            <BarChart3 className="w-10 h-10 sm:w-12 sm:h-12 text-blue-400 mx-auto mb-4" />
            <h3 className="text-xl sm:text-2xl font-semibold text-white mb-3">Interpret</h3>
            <p className="text-violet-300 text-sm sm:text-base">
              Understand the emotions and needs behind difficult messages. 
              See past the words to the heart.
            </p>
          </div>

          <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6 sm:p-8 text-center hover:bg-white/10 transition-all duration-300 sm:col-span-2 md:col-span-1">
            <Heart className="w-10 h-10 sm:w-12 sm:h-12 text-red-400 mx-auto mb-4" />
            <h3 className="text-xl sm:text-2xl font-semibold text-white mb-3">Heal</h3>
            <p className="text-violet-300 text-sm sm:text-base">
              Strengthen relationships through empathetic communication. 
              Every message is a chance to connect deeper.
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  // Memoized MessageInput to prevent unnecessary re-renders
  const MessageInput = React.memo(() => (
    <textarea
      ref={textAreaRef}
      value={messageText}
      onChange={handleTextChange}
      onTouchStart={handleInputInteraction}
      onFocus={handleInputInteraction}
      placeholder={activeTab === 'Analyze Message' 
        ? "Paste the message you received here..." 
        : "Type your message here..."
      }
      className="w-full p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 resize-none text-gray-900 placeholder-gray-400"
      rows={6}
      style={{ 
        minHeight: '150px',
        fontSize: '16px',
        lineHeight: '1.5'
      }}
    />
  ));

  // Main App Interface
  const MainInterface = () => (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200 px-4 py-3 sm:px-6 sm:py-4 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-purple-100 rounded-full p-2">
              <Heart className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <h1 className="text-lg sm:text-xl font-bold text-gray-900">The Third Voice</h1>
              <p className="text-xs sm:text-sm text-gray-500">AI Communication Assistant</p>
            </div>
          </div>
          <div className="bg-gray-100 rounded-full p-2">
            <User className="w-5 h-5 text-gray-600" />
          </div>
        </div>
      </div>

      <div className="px-4 py-6 sm:px-6 max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl p-4 sm:p-6 shadow-sm mb-4 sm:mb-6">
          <label className="block text-base sm:text-lg font-medium text-gray-900 mb-3 sm:mb-4">
            Who are you communicating with?
          </label>
          <div className="relative">
            <select 
              value={selectedRelationship}
              onChange={(e) => setSelectedRelationship(e.target.value)}
              className="w-full p-3 sm:p-4 pr-10 bg-white border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 appearance-none text-gray-900 text-base sm:text-lg"
            >
              {relationshipTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 sm:right-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
          </div>
        </div>

        <div className="bg-white rounded-2xl p-2 shadow-sm mb-4 sm:mb-6">
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => {
                setActiveTab('Analyze Message');
                resetForm();
              }}
              className={`py-3 px-4 rounded-xl font-medium transition-all text-sm sm:text-base ${
                activeTab === 'Analyze Message' 
                  ? 'bg-purple-100 text-purple-800 shadow-sm' 
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
                  ? 'bg-purple-100 text-purple-800 shadow-sm' 
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              Transform Message
            </button>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
          <div className="p-4 sm:p-6 border-b border-gray-100">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              {activeTab === 'Analyze Message' 
                ? "Message you received:" 
                : "Message you want to send:"
              }
            </label>
            <MessageInput />
            
            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-gray-500">
                {messageText.length} characters
              </div>
              
              <button
                onClick={() => processMessage(activeTab === 'Transform Message' ? 'transform' : 'interpret')}
                disabled={!messageText.trim() || loading}
                className="bg-purple-600 text-white py-3 px-6 rounded-xl font-medium hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center space-x-2 text-sm sm:text-base"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>{activeTab === 'Transform Message' ? 'Transform' : 'Analyze'}</span>
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="p-4 sm:p-6 bg-gray-50 min-h-[200px]">
            {loading ? (
              <div className="flex flex-col items-center justify-center py-8 space-y-4">
                <Loader2 className="w-8 h-8 text-purple-600 animate-spin" />
                <div className="text-center">
                  <p className="text-gray-600 font-medium">Processing your message...</p>
                  <p className="text-sm text-gray-500 mt-1">This may take a few seconds</p>
                </div>
              </div>
            ) : (transformedMessage || interpretedMessage) ? (
              <div>
                {activeTab === 'Transform Message' && transformedMessage && (
                  <div>
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 space-y-2 sm:space-y-0">
                      <h3 className="text-lg font-semibold text-green-700 flex items-center">
                        <CheckCircle className="w-5 h-5 mr-2" />
                        Suggested Response
                      </h3>
                      <div className="flex items-center space-x-2 bg-yellow-100 px-3 py-1 rounded-full self-start">
                        <Star className="w-4 h-4 text-yellow-600" />
                        <span className="text-sm font-medium text-yellow-700">
                          Healing Score: {healingScore}/10
                        </span>
                      </div>
                    </div>
                    
                    <div className="bg-white rounded-xl p-4 sm:p-6 border border-gray-200 shadow-sm relative mb-4">
                      <p className="text-gray-900 leading-relaxed text-base italic">{transformedMessage}</p>
                      <button
                        onClick={() => copyToClipboard(transformedMessage)}
                        className="absolute top-4 right-4 p-2 text-gray-400 hover:text-gray-600 transition-colors"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                    </div>
                    
                    <button
                      onClick={resetForm}
                      className="w-full sm:w-auto bg-gray-200 text-gray-700 px-6 py-3 rounded-xl hover:bg-gray-300 transition-colors font-medium text-sm sm:text-base"
                    >
                      Transform Another Message
                    </button>
                  </div>
                )}

                {activeTab === 'Analyze Message' && interpretedMessage && (
                  <div>
                    <h3 className="text-lg font-semibold text-blue-700 flex items-center mb-4">
                      <BarChart3 className="w-5 h-5 mr-2" />
                      Message Analysis
                    </h3>
                    
                    <div className="bg-white rounded-xl p-4 sm:p-6 border border-gray-200 mb-4 shadow-sm">
                      <p className="text-gray-900 leading-relaxed text-base sm:text-lg">{interpretedMessage}</p>
                    </div>

                    <button
                      onClick={resetForm}
                      className="w-full sm:w-auto bg-gray-200 text-gray-700 px-6 py-3 rounded-xl hover:bg-gray-300 transition-colors font-medium text-sm sm:text-base"
                    >
                      Analyze Another Message
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <div className="bg-purple-100 rounded-full p-4 mb-4">
                  {activeTab === 'Transform Message' ? (
                    <MessageCircle className="w-8 h-8 text-purple-600" />
                  ) : (
                    <BarChart3 className="w-8 h-8 text-purple-600" />
                  )}
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Ready to {activeTab === 'Transform Message' ? 'transform' : 'analyze'} your message
                </h3>
                <p className="text-gray-500 text-sm sm:text-base max-w-sm">
                  {activeTab === 'Transform Message' 
                    ? 'Enter a message above and I\'ll help make it more loving and effective.'
                    : 'Paste a message you received and I\'ll help you understand the emotions behind it.'
                  }
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="text-center mt-6">
          <div className="inline-flex items-center space-x-2 bg-white text-gray-600 px-4 py-2 rounded-full text-xs sm:text-sm font-medium shadow-sm border border-gray-200">
            <Sparkles className="w-4 h-4" />
            <span>Demo Mode</span>
          </div>
        </div>
      </div>
    </div>
  );

  // Use currentPage state properly
  if (user) {
    return <MainInterface />;
  }

  return <LandingPage />;
}
