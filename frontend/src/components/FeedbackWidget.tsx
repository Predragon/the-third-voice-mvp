import { useState } from 'react';
import { Star, X, Send, ThumbsUp, ThumbsDown, MessageCircle } from 'lucide-react';
import api from '../api';

interface FeedbackWidgetProps {
  context?: 'transform' | 'interpret' | 'general';
  onClose?: () => void;
  minimal?: boolean;
}

export default function FeedbackWidget({ context = 'general', onClose, minimal = false }: FeedbackWidgetProps) {
  const [rating, setRating] = useState<number>(0);
  const [hoverRating, setHoverRating] = useState<number>(0);
  const [feedbackText, setFeedbackText] = useState('');
  const [step, setStep] = useState<'rate' | 'details' | 'thanks'>('rate');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleQuickFeedback = async (isPositive: boolean) => {
    setLoading(true);
    try {
      await api.submitFeedback(isPositive ? 5 : 2, undefined, context);
      setStep('thanks');
      setTimeout(() => onClose?.(), 2000);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleRatingClick = (value: number) => {
    setRating(value);
    if (value >= 4) {
      // Good rating - submit immediately or show thank you
      submitFeedback(value);
    } else {
      // Lower rating - ask for details
      setStep('details');
    }
  };

  const submitFeedback = async (ratingValue?: number) => {
    setLoading(true);
    setError(null);
    try {
      await api.submitFeedback(ratingValue || rating, feedbackText || undefined, context);
      setStep('thanks');
      setTimeout(() => onClose?.(), 2000);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  // Minimal quick feedback (thumbs up/down)
  if (minimal) {
    return (
      <div className="flex items-center gap-2">
        <span className="text-xs text-gray-500">Helpful?</span>
        <button
          onClick={() => handleQuickFeedback(true)}
          disabled={loading}
          className="p-1.5 hover:bg-green-50 rounded-lg transition-colors group"
          title="Yes, helpful"
        >
          <ThumbsUp className="w-4 h-4 text-gray-400 group-hover:text-green-600" />
        </button>
        <button
          onClick={() => handleQuickFeedback(false)}
          disabled={loading}
          className="p-1.5 hover:bg-red-50 rounded-lg transition-colors group"
          title="Not helpful"
        >
          <ThumbsDown className="w-4 h-4 text-gray-400 group-hover:text-red-600" />
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-4 max-w-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <MessageCircle className="w-5 h-5 text-blue-600" />
          <h3 className="font-semibold text-gray-900">
            {step === 'thanks' ? 'Thank You!' : 'How was this?'}
          </h3>
        </div>
        {onClose && (
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
            <X className="w-4 h-4 text-gray-400" />
          </button>
        )}
      </div>

      {/* Rating Step */}
      {step === 'rate' && (
        <div className="text-center">
          <p className="text-sm text-gray-600 mb-3">
            {context === 'transform'
              ? 'How helpful was this transformation?'
              : context === 'interpret'
              ? 'Was this interpretation insightful?'
              : 'How is your experience?'}
          </p>
          <div className="flex justify-center gap-1 mb-2">
            {[1, 2, 3, 4, 5].map((value) => (
              <button
                key={value}
                onClick={() => handleRatingClick(value)}
                onMouseEnter={() => setHoverRating(value)}
                onMouseLeave={() => setHoverRating(0)}
                className="p-1 transition-transform hover:scale-110"
                disabled={loading}
              >
                <Star
                  className={`w-8 h-8 transition-colors ${
                    value <= (hoverRating || rating)
                      ? 'text-yellow-400 fill-yellow-400'
                      : 'text-gray-300'
                  }`}
                />
              </button>
            ))}
          </div>
          <p className="text-xs text-gray-400">
            {hoverRating === 1 && 'Not helpful'}
            {hoverRating === 2 && 'Could be better'}
            {hoverRating === 3 && 'Okay'}
            {hoverRating === 4 && 'Helpful'}
            {hoverRating === 5 && 'Very helpful!'}
          </p>
        </div>
      )}

      {/* Details Step */}
      {step === 'details' && (
        <div>
          <p className="text-sm text-gray-600 mb-3">
            What could we do better? Your feedback helps us improve.
          </p>
          <textarea
            value={feedbackText}
            onChange={(e) => setFeedbackText(e.target.value)}
            placeholder="Tell us more... (optional)"
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 resize-none h-24 text-sm"
          />
          {error && (
            <p className="text-red-600 text-xs mt-2">{error}</p>
          )}
          <div className="flex gap-2 mt-3">
            <button
              onClick={() => setStep('rate')}
              className="flex-1 py-2 text-gray-600 hover:bg-gray-100 rounded-lg text-sm"
            >
              Back
            </button>
            <button
              onClick={() => submitFeedback()}
              disabled={loading}
              className="flex-1 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:bg-gray-300 flex items-center justify-center gap-1"
            >
              <Send className="w-4 h-4" />
              {loading ? 'Sending...' : 'Submit'}
            </button>
          </div>
        </div>
      )}

      {/* Thanks Step */}
      {step === 'thanks' && (
        <div className="text-center py-4">
          <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <ThumbsUp className="w-6 h-6 text-green-600" />
          </div>
          <p className="text-gray-700 font-medium">Thanks for your feedback!</p>
          <p className="text-sm text-gray-500 mt-1">
            Your input helps us improve for all co-parents.
          </p>
        </div>
      )}
    </div>
  );
}

// Floating feedback button for persistent access
export function FeedbackButton() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-20 right-4 w-12 h-12 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 flex items-center justify-center z-40"
        title="Give Feedback"
      >
        <MessageCircle className="w-6 h-6" />
      </button>

      {/* Feedback Modal */}
      {isOpen && (
        <div className="fixed bottom-36 right-4 z-50">
          <FeedbackWidget onClose={() => setIsOpen(false)} />
        </div>
      )}
    </>
  );
}
