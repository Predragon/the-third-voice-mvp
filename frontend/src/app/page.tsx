"use client";

import React, { useState } from 'react';
import { Copy, Heart, Lightbulb, ChevronDown, Brain } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

interface ApiResult {
  explanation?: string;
  suggested_responses?: string[];
  suggested_response?: string;
  healing_score?: number;
  sentiment?: string;
  emotional_state?: string;
  model_used?: string;
  subtext?: string;
  needs?: string[];
  analysis_depth?: string;
  communication_patterns?: string[];
  relationship_dynamics?: string[];
  transformed_message?: string;
  alternatives?: string[];
}

export default function TheThirdVoice() {
  const [step, setStep] = useState(1); // 1: context, 2: mode, 3: input, 4: results
  const [context, setContext] = useState('coparenting');
  const [mode, setMode] = useState(''); // 'analyze' or 'transform'
  const [useDeepAnalysis, setUseDeepAnalysis] = useState(false);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ApiResult | null>(null);
  const [copyStatus, setCopyStatus] = useState('');

  const relationships = [
    { value: 'coparenting', label: 'Co-parent' },
    { value: 'partner', label: 'Partner' },
    { value: 'spouse', label: 'Spouse' },
    { value: 'ex-partner', label: 'Ex-partner' },
    { value: 'family', label: 'Family Member' },
    { value: 'friend', label: 'Friend' },
    { value: 'colleague', label: 'Colleague' },
    { value: 'other', label: 'Other' }
  ];

  const processMessage = async () => {
    if (!message.trim()) return;
    
    setLoading(true);
    const endpoint = mode === 'analyze' 
      ? '/api/messages/quick-interpret'
      : '/api/messages/quick-transform';
    
    try {
      const requestBody = {
        message: message.trim(),
        contact_context: context,
        contact_name: context.charAt(0).toUpperCase() + context.slice(1),
        use_deep_analysis: mode === 'analyze' ? useDeepAnalysis : false,
        mode: mode
      };

      console.log('Sending request:', requestBody);

      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (response.ok) {
        const data = await response.json();
        console.log('API Response:', data);
        setResult(data);
        setStep(4);
      } else {
        const errorText = await response.text();
        console.error('API Error:', response.status, errorText);
        const fallback = mode === 'analyze' 
          ? {
              explanation: "I'm having trouble analyzing this specific message right now, but I can offer some general guidance for thoughtful communication.",
              suggested_responses: [
                "I want to make sure I understand what you're saying. Can you help me see this from your perspective?",
                "Thank you for sharing this with me. How can we work together to address your concerns?",
                "I appreciate you reaching out. What would be most helpful for you right now?"
              ],
              healing_score: 6,
              sentiment: "neutral",
              emotional_state: "understanding",
              model_used: "Fallback Response",
              subtext: "Communication is important, and finding understanding is key.",
              needs: ["clarity", "understanding", "connection"],
              analysis_depth: useDeepAnalysis ? "deep" : "quick"
            }
          : {
              transformed_message: "I'd like to communicate about this in a way that works for both of us. Can we discuss this together?",
              alternatives: [
                "I'm hoping we can find a good way to talk about this. What works best for you?",
                "I want to make sure we're both comfortable with how we handle this situation.",
                "Let's work together to find a solution that feels good for everyone involved."
              ],
              healing_score: 7,
              sentiment: "positive",
              emotional_state: "collaborative",
              explanation: "This approach focuses on mutual respect and finding common ground in communication.",
              model_used: "Fallback Response"
            };
        
        setResult(fallback);
        setStep(4);
      }
    } catch (error) {
      console.error('Network error:', error);
      const fallback = mode === 'analyze' 
          ? {
              explanation: "I'm experiencing technical difficulties, but I can still offer some helpful communication suggestions.",
              suggested_responses: [
                "I'm having some technical issues right now, but I want to make sure we can still communicate effectively.",
                "There seems to be a connection problem on my end. Can we try a different way to discuss this?",
                "I apologize for the technical difficulty. Your message is important - how can we best continue this conversation?"
              ],
              healing_score: 5,
              sentiment: "neutral",
              emotional_state: "apologetic",
              model_used: "Network Fallback",
              subtext: "Technical issues shouldn't stop meaningful communication.",
              needs: ["connection", "understanding", "patience"],
              analysis_depth: useDeepAnalysis ? "deep" : "quick"
            }
          : {
              transformed_message: "I'm having some technical difficulties, but I'm committed to communicating with you. How can we best continue our conversation?",
              alternatives: [
                "There's a technical issue on my end, but I value our communication. Can we find another way to discuss this?",
                "I'm experiencing some connectivity problems, but your message is important to me. Let's work through this together."
              ],
              healing_score: 6,
              sentiment: "positive",
              emotional_state: "determined",
              explanation: "This acknowledges technical issues while emphasizing the importance of maintaining communication.",
              model_used: "Network Fallback"
            };
      setResult(fallback);
      setStep(4);
    }
    
    setLoading(false);
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopyStatus('Copied!');
      setTimeout(() => setCopyStatus(''), 2000);
    } catch (err) {
      console.error('Copy failed:', err);
    }
  };

  const startOver = () => {
    setStep(1);
    setContext('coparenting');
    setMode('');
    setUseDeepAnalysis(false);
    setMessage('');
    setResult(null);
    setCopyStatus('');
  };

  const goBack = () => {
    if (step > 1) {
      setStep(prevStep => {
        if (prevStep <= 3) {
          setMessage('');
          if (prevStep === 2) {
              setMode('');
              setUseDeepAnalysis(false);
          }
        }
        return prevStep - 1;
      });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Copy notification */}
      {copyStatus && (
        <div className="fixed top-4 right-4 bg-green-500 text-white px-3 py-2 rounded-lg shadow-lg z-50 text-sm">
          {copyStatus}
        </div>
      )}

      <div className="container mx-auto px-3 py-4 max-w-sm sm:max-w-md sm:px-4 sm:py-6">
        
        {/* Header */}
        <div className="text-center mb-6 sm:mb-8">
          <div className="w-12 h-12 sm:w-16 sm:h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3 sm:mb-4">
            <Heart className="w-6 h-6 sm:w-8 sm:h-8 text-purple-600" />
          </div>
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2">
            The Third Voice AI
          </h1>
          <p className="text-gray-600 text-xs sm:text-sm px-2">
            Your AI companion for emotionally intelligent communication.
          </p>
        </div>

        {/* Step 1: Choose Relationship Context */}
        {step === 1 && (
          <div className="bg-white rounded-xl shadow-sm p-4 sm:p-6">
            <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-4 sm:mb-6">
              First, who are you communicating with?
            </h2>
            
            <div className="relative mb-4 sm:mb-6">
              <select
                value={context}
                onChange={(e) => setContext(e.target.value)}
                className="w-full p-3 sm:p-4 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 appearance-none text-gray-900 text-base sm:text-lg"
                style={{ fontSize: '16px' }}
              >
                {relationships.map(rel => (
                  <option key={rel.value} value={rel.value}>{rel.label}</option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 sm:right-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
            </div>

            <button
              onClick={() => setStep(2)}
              className="w-full bg-purple-600 text-white font-semibold py-3 sm:py-4 px-6 rounded-xl hover:bg-purple-700 active:bg-purple-800 transition-colors text-base sm:text-lg"
              style={{ minHeight: '44px', minWidth: '44px' }}
            >
              Continue
            </button>
          </div>
        )}

        {/* Step 2: Choose Mode */}
        {step === 2 && (
          <div className="bg-white rounded-xl shadow-sm p-4 sm:p-6">
            <div className="flex gap-4 mb-4 sm:mb-6">
              <button 
                onClick={goBack}
                className="text-purple-600 text-sm"
                style={{ minHeight: '44px', minWidth: '44px' }}
              >
                ← Back
              </button>
            </div>

            <div className="space-y-3 sm:space-y-4">
              <button
                onClick={() => {
                  setMode('analyze');
                  setStep(3);
                }}
                className="w-full p-4 sm:p-6 bg-blue-50 border-2 border-blue-200 rounded-xl hover:bg-blue-100 active:bg-blue-200 transition-colors text-left"
                style={{ minHeight: '44px', minWidth: '44px' }}
              >
                <div className="flex items-start">
                  <Lightbulb className="w-5 h-5 sm:w-6 sm:h-6 text-blue-600 mr-3 mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold text-blue-900 mb-1 text-sm sm:text-base">Analyze Message</h3>
                    <p className="text-blue-700 text-xs sm:text-sm">
                      I received a message and want to understand what they really mean
                    </p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => {
                  setMode('transform');
                  setStep(3);
                }}
                className="w-full p-4 sm:p-6 bg-green-50 border-2 border-green-200 rounded-xl hover:bg-green-100 active:bg-green-200 transition-colors text-left"
                style={{ minHeight: '44px', minWidth: '44px' }}
              >
                <div className="flex items-start">
                  <Heart className="w-5 h-5 sm:w-6 sm:h-6 text-green-600 mr-3 mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold text-green-900 mb-1 text-sm sm:text-base">Transform Message</h3>
                    <p className="text-green-700 text-xs sm:text-sm">
                      I want to send a message but say it in a better way
                    </p>
                  </div>
                </div>
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Input Message */}
        {step === 3 && (
          <div className="bg-white rounded-xl shadow-sm p-4 sm:p-6">
            <div className="flex gap-4 mb-4 sm:mb-6">
              <button 
                onClick={goBack}
                className="text-purple-600 text-sm"
                style={{ minHeight: '44px', minWidth: '44px' }}
              >
                ← Back
              </button>
            </div>

            {/* Deep Analysis Toggle - Only show for analyze mode */}
            {mode === 'analyze' && (
              <div className="mb-4 sm:mb-6 p-3 sm:p-4 bg-purple-50 rounded-xl border border-purple-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Brain className="w-4 h-4 sm:w-5 sm:h-5 text-purple-600 mr-2" />
                    <span className="text-sm sm:text-base font-medium text-purple-900">
                      Deep Analysis
                    </span>
                  </div>
                  <button
                    onClick={() => setUseDeepAnalysis(!useDeepAnalysis)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      useDeepAnalysis ? 'bg-purple-600' : 'bg-gray-200'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        useDeepAnalysis ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
                <p className="text-xs sm:text-sm text-purple-700 mt-2">
                  {useDeepAnalysis 
                    ? 'Deeper insights (15-25 sec) - Uses advanced reasoning' 
                    : 'Faster response (2-5 sec) - Quick interpretation'
                  }
                </p>
              </div>
            )}

            <div className="mb-4">
              <h3 className="font-semibold text-gray-900 mb-2 text-sm sm:text-base">
                {mode === 'analyze' ? 'Message you received:' : 'What do you want to say?'}
              </h3>
              <p className="text-xs sm:text-sm text-gray-600 mb-4">
                {mode === 'analyze' 
                  ? 'Copy and paste the message from your texting app' 
                  : 'Type what you want to communicate'
                }
              </p>
            </div>

            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder={mode === 'analyze'
                ? "Paste the message you received here..."
                : "Type your message here..."
              }
              className="w-full h-36 sm:h-40 p-3 sm:p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 resize-none text-sm sm:text-base"
              style={{ fontSize: '16px' }}
              maxLength={500}
            />
            
            <div className="flex justify-between items-center mt-2 sm:mt-3 text-xs sm:text-sm text-gray-500 mb-4 sm:mb-6">
              <span>{message.length}/500 characters</span>
            </div>

            <button
              onClick={processMessage}
              disabled={!message.trim() || loading}
              className="w-full bg-purple-600 text-white font-semibold py-3 sm:py-4 px-6 rounded-xl hover:bg-purple-700 active:bg-purple-800 disabled:opacity-50 transition-all duration-200 flex items-center justify-center text-sm sm:text-base"
              style={{ minHeight: '44px', minWidth: '44px' }}
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 sm:w-5 sm:h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                  {useDeepAnalysis ? 'Deep Analysis...' : 'Processing...'}
                </>
              ) : (
                <>
                  {mode === 'analyze' ? (
                    useDeepAnalysis ? <Brain className="w-4 h-4 sm:w-5 sm:h-5 mr-2" /> : <Lightbulb className="w-4 h-4 sm:w-5 sm:h-5 mr-2" />
                  ) : (
                    <Heart className="w-4 h-4 sm:w-5 sm:h-5 mr-2" />
                  )}
                  {mode === 'analyze' 
                    ? (useDeepAnalysis ? 'Deep Analyze' : 'Quick Analyze')
                    : 'Transform'
                  }
                </>
              )}
            </button>
          </div>
        )}

        {/* Step 4: Results */}
        {step === 4 && result && (
          <div className="space-y-4 sm:space-y-6">
            <div className="flex gap-4 mb-4 sm:mb-6">
              <button 
                onClick={goBack}
                className="text-purple-600 text-sm"
                style={{ minHeight: '44px', minWidth: '44px' }}
              >
                ← Back
              </button>
              <button 
                onClick={startOver}
                className="text-purple-600 text-sm ml-auto"
                style={{ minHeight: '44px', minWidth: '44px' }}
              >
                Start Over
              </button>
            </div>

            {mode === 'analyze' ? (
              /* Analysis Results */
              <div className="space-y-3 sm:space-y-4">
                <div className="bg-white rounded-xl shadow-sm p-4 sm:p-6">
                  <h3 className="font-semibold text-gray-900 mb-3 sm:mb-4 flex items-start sm:items-center flex-col sm:flex-row gap-2">
                    <div className="flex items-center">
                      {result.analysis_depth === 'deep' ? (
                        <Brain className="w-4 h-4 sm:w-5 sm:h-5 mr-2 text-purple-600" />
                      ) : (
                        <Lightbulb className="w-4 h-4 sm:w-5 sm:h-5 mr-2 text-blue-600" />
                      )}
                      <span className="text-sm sm:text-base">
                        {result.analysis_depth === 'deep' ? 'Deep Analysis' : 'Quick Analysis'}
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-1 sm:gap-2 sm:ml-auto">
                        {result.healing_score && (
                          <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                            Healing: {result.healing_score}/10
                          </span>
                        )}
                        {result.sentiment && (
                            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                                Sentiment: {result.sentiment}
                            </span>
                        )}
                        {result.emotional_state && (
                            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                                Emotion: {result.emotional_state}
                            </span>
                        )}
                        {result.model_used && (
                          <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded-full">
                            {result.model_used}
                          </span>
                        )}
                    </div>
                  </h3>
                  
                  {result.explanation && (
                    <div className="bg-blue-50 p-3 sm:p-4 rounded-lg mb-3 sm:mb-4">
                      <p className="text-gray-800 leading-relaxed text-sm sm:text-base">
                        {result.explanation}
                      </p>
                    </div>
                  )}

                  {result.subtext && (
                    <div className="mt-3 sm:mt-4 p-3 sm:p-4 bg-gray-50 rounded-lg">
                      <p className="text-xs sm:text-sm text-gray-700">
                        <strong>Deeper feelings:</strong> {result.subtext}
                      </p>
                    </div>
                  )}
                  
                  {result.needs && result.needs.length > 0 && (
                    <div className="mt-3 sm:mt-4 p-3 sm:p-4 bg-gray-50 rounded-lg">
                      <p className="text-xs sm:text-sm text-gray-700 mb-1">
                        <strong>Underlying needs:</strong>
                      </p>
                      <ul className="list-disc list-inside text-xs sm:text-sm text-gray-700">
                        {result.needs.map((need: string, i: number) => <li key={i}>{need}</li>)}
                      </ul>
                    </div>
                  )}

                  {result.analysis_depth === 'deep' && result.communication_patterns && result.communication_patterns.length > 0 && (
                    <div className="mt-3 sm:mt-4 p-3 sm:p-4 bg-purple-50 rounded-lg">
                      <p className="text-xs sm:text-sm text-purple-800 mb-1">
                        <strong>Communication patterns:</strong>
                      </p>
                      <ul className="list-disc list-inside text-xs sm:text-sm text-purple-700">
                        {result.communication_patterns.map((pattern: string, i: number) => <li key={i}>{pattern}</li>)}
                      </ul>
                    </div>
                  )}

                  {result.analysis_depth === 'deep' && result.relationship_dynamics && result.relationship_dynamics.length > 0 && (
                    <div className="mt-3 sm:mt-4 p-3 sm:p-4 bg-purple-50 rounded-lg">
                      <p className="text-xs sm:text-sm text-purple-800 mb-1">
                        <strong>Relationship dynamics:</strong>
                      </p>
                      <ul className="list-disc list-inside text-xs sm:text-sm text-purple-700">
                        {result.relationship_dynamics.map((dynamic: string, i: number) => <li key={i}>{dynamic}</li>)}
                      </ul>
                    </div>
                  )}
                </div>

                <div className="bg-white rounded-xl shadow-sm p-4 sm:p-6">
                  <h3 className="font-semibold text-gray-900 mb-3 sm:mb-4 text-sm sm:text-base">
                    Suggested Responses
                  </h3>
                  
                  <div className="space-y-2 sm:space-y-3">
                    {(() => {
                      // Handle both suggested_responses (array) and suggested_response (string) formats                      
                      let responses: string[] = [];
                      if (result.suggested_responses && Array.isArray(result.suggested_responses) && result.suggested_responses.length > 0) {
                        responses = result.suggested_responses;
                      } else if (result.suggested_response && result.suggested_response.trim()) {
                        responses = [result.suggested_response];
                      }
                      
                      if (responses.length > 0) {
                        return responses.map((response: string, index: number) => (
                          <div key={index} className="bg-gray-50 p-3 sm:p-4 rounded-lg">
                            <p className="text-gray-800 italic mb-2 sm:mb-3 text-sm sm:text-base leading-relaxed">
                              &ldquo;{response}&rdquo;
                            </p>
                            <button
                              onClick={() => copyToClipboard(response)}
                              className="bg-blue-600 text-white px-3 py-2 rounded-lg hover:bg-blue-700 active:bg-blue-800 transition-colors flex items-center text-xs sm:text-sm"
                              style={{ minHeight: '44px', minWidth: '44px' }}
                            >
                              <Copy className="w-3 h-3 sm:w-4 sm:h-4 mr-2" />
                              Copy
                            </button>
                          </div>
                        ));
                      } else {
                        // Generate context-aware responses based on the analysis
                        const contextualResponses = [];
                        
                        // Base response acknowledging the analysis insights
                        if (result.subtext || result.emotional_state) {
                          const emotionalContext = result.subtext || `you're feeling ${result.emotional_state}`;
                          contextualResponses.push(`I can see that ${emotionalContext}. You're absolutely right to feel this way, and I want to address this with you.`);
                        }
                        
                        // Context-specific responses based on relationship type
                        if (context === 'coparenting') {
                          if (result.subtext && result.subtext.includes('time')) {
                            contextualResponses.push("You're right - our children deserve consistency, and I need to do better with communication and timing. How can we set up a system that works for both of us?");
                            contextualResponses.push("I hear you about the time and schedule issues. Our kids' routine is important, and I want to be more reliable. What would help make this smoother?");
                          }
                          if (result.emotional_state && (result.emotional_state.includes('frustrated') || result.emotional_state.includes('disrespected'))) {
                            contextualResponses.push("I understand I've been letting you down with communication and timing. That's not fair to you or the kids. What can I do differently going forward?");
                          }
                        } else if (context === 'partner' || context === 'spouse') {
                          if (result.subtext && result.subtext.includes('respect')) {
                            contextualResponses.push("I hear that you need me to be more considerate of your time and our commitments. You deserve that respect, and I want to do better.");
                          }
                          if (result.emotional_state && result.emotional_state.includes('frustrated')) {
                            contextualResponses.push("I can see how frustrated this has made you, and I understand why. Your time and our plans matter to me. How can we fix this pattern?");
                          }
                        }
                        
                        // Add needs-based responses
                        if (result.needs && Array.isArray(result.needs)) {
                          result.needs.forEach((need: string) => {
                            if (need.includes('reliability') || need.includes('communication')) {
                              contextualResponses.push(`I hear that you need more ${need} from me. That's completely fair, and I'm committed to making changes. What specific steps would help?`);
                            }
                            if (need.includes('respect')) {
                              contextualResponses.push(`You deserve respect for your time and efforts. I haven't been showing that consistently, and I want to change that. Can we talk about what that looks like?`);
                            }
                          });
                        }
                        
                        // Generic empathetic fallback if no specific context was captured
                        if (contextualResponses.length === 0) {
                          contextualResponses.push("I want to understand what you're going through. Can you help me see this from your perspective?");
                          contextualResponses.push("Thank you for sharing this with me. Your feelings are valid, and I want to work together to address this.");
                        }
                        
                        // Remove duplicates and limit to 3-4 responses
                        const uniqueResponses = [...new Set(contextualResponses)].slice(0, 4);
                        
                        return (
                          <div className="bg-blue-50 p-3 sm:p-4 rounded-lg">
                            <p className="text-sm text-blue-800 font-medium mb-3">
                              Based on the analysis, here are thoughtful responses that address their underlying needs:
                            </p>
                            <div className="space-y-3">
                              {uniqueResponses.map((response, index) => (
                                <div key={index} className="bg-white p-3 rounded-lg shadow-sm">
                                  <p className="text-gray-800 italic mb-2 text-sm leading-relaxed">
                                    &ldquo;{response}&rdquo;
                                  </p>
                                  <button
                                    onClick={() => copyToClipboard(response)}
                                    className="bg-blue-600 text-white px-3 py-2 rounded-lg hover:bg-blue-700 active:bg-blue-800 transition-colors flex items-center text-xs"
                                    style={{ minHeight: '36px', minWidth: '44px' }}
                                  >
                                    <Copy className="w-3 h-3 mr-1" />
                                    Copy
                                  </button>
                                </div>
                              ))}
                            </div>
                          </div>
                        );
                      }
                    })()}
                  </div>
                </div>
              </div>
            ) : (
              /* Transform Results */
              <div className="space-y-3 sm:space-y-4">
                <div className="bg-white rounded-xl shadow-sm p-4 sm:p-6">
                  <h3 className="font-semibold text-gray-900 mb-3 sm:mb-4 flex items-start sm:items-center flex-col sm:flex-row gap-2">
                    <div className="flex items-center">
                      <Heart className="w-4 h-4 sm:w-5 sm:h-5 mr-2 text-green-600" />
                      <span className="text-sm sm:text-base">Transformed Message</span>
                    </div>
                    <div className="flex flex-wrap gap-1 sm:gap-2 sm:ml-auto">
                      {result.healing_score && (
                        <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                          Healing: {result.healing_score}/10
                        </span>
                      )}
                      {result.sentiment && (
                        <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                          Sentiment: {result.sentiment}
                        </span>
                      )}
                      {result.emotional_state && (
                        <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                          Emotion: {result.emotional_state}
                        </span>
                      )}
                      {result.model_used && (
                        <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded-full">
                          {result.model_used}
                        </span>
                      )}
                    </div>
                  </h3>
                  
                  <div className="bg-green-50 p-3 sm:p-4 rounded-lg mb-3 sm:mb-4">
                    <p className="text-gray-800 italic text-sm sm:text-lg leading-relaxed">
                      &ldquo;{result.transformed_message}&rdquo;
                    </p>
                  </div>

                  <div className="flex gap-2 mb-3 sm:mb-4">
                    <button
                      onClick={() => copyToClipboard(result.transformed_message)}
                      className="bg-green-600 text-white px-3 py-2 rounded-lg hover:bg-green-700 active:bg-green-800 transition-colors flex items-center text-xs sm:text-sm"
                      style={{ minHeight: '44px', minWidth: '44px' }}
                    >
                      <Copy className="w-3 h-3 sm:w-4 sm:h-4 mr-2" />
                      Copy
                    </button>
                  </div>
                  
                  {result.explanation && (
                    <div className="p-3 sm:p-4 bg-gray-50 rounded-lg">
                      <p className="text-xs sm:text-sm text-gray-700">
                        <strong>Why this works:</strong> {result.explanation}
                      </p>
                    </div>
                  )}
                </div>

                {/* Alternative suggestions */}
                {result.alternatives && result.alternatives.length > 0 && (
                  <div className="bg-white rounded-xl shadow-sm p-4 sm:p-6">
                    <h3 className="font-semibold text-gray-900 mb-3 sm:mb-4 text-sm sm:text-base">
                      Alternative Options
                    </h3>
                    
                    <div className="space-y-2 sm:space-y-3">
                      {result.alternatives.map((alternative: string, index: number) => (
                        <div key={index} className="bg-gray-50 p-3 sm:p-4 rounded-lg">
                          <p className="text-gray-800 italic mb-2 sm:mb-3 text-sm sm:text-base leading-relaxed">
                            &ldquo;{alternative}&rdquo;
                          </p>
                          <button
                            onClick={() => copyToClipboard(alternative)}
                            className="bg-green-600 text-white px-3 py-2 rounded-lg hover:bg-green-700 active:bg-green-800 transition-colors flex items-center text-xs sm:text-sm"
                            style={{ minHeight: '44px', minWidth: '44px' }}
                          >
                            <Copy className="w-3 h-3 sm:w-4 sm:h-4 mr-2" />
                            Copy
                          </button>
                        </div>
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