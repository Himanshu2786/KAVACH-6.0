import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { X, Star, Send, MessageSquare } from 'lucide-react';
import { api } from '../../services/api';
import { useApp } from '../../context/AppContext';

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  assessmentId?: string;
}

export const FeedbackModal: React.FC<FeedbackModalProps> = ({
  isOpen,
  onClose,
  assessmentId
}) => {
  const { showToast } = useApp();
  const [rating, setRating] = useState<number>(5);
  const [whatWorked, setWhatWorked] = useState('');
  const [whatConfusing, setWhatConfusing] = useState('');
  const [whatSlow, setWhatSlow] = useState('');
  const [bugDescription, setBugDescription] = useState('');
  const [suggestions, setSuggestions] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Close on Escape key press
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await api.submitFeedback({
        rating,
        assessment_id: assessmentId,
        what_worked: whatWorked,
        what_confusing: whatConfusing,
        what_slow: whatSlow,
        bug_description: bugDescription,
        suggestions
      });
      showToast('success', 'Feedback Submitted', res.message || 'Thank you for your valuable feedback!');
      onClose();
      // Reset form
      setRating(5);
      setWhatWorked('');
      setWhatConfusing('');
      setWhatSlow('');
      setBugDescription('');
      setSuggestions('');
    } catch (err: any) {
      showToast('error', 'Submission Failed', err.message || 'Could not submit feedback.');
    } finally {
      setSubmitting(false);
    }
  };

  const modalNode = (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200 overflow-y-auto"
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          onClose();
        }
      }}
    >
      <div
        className="w-full max-w-lg rounded-2xl border border-white/10 bg-[#0d0d10] p-6 shadow-2xl relative my-auto flex flex-col max-h-[min(90vh,760px)] overflow-hidden"
        style={{
          boxShadow: '0 25px 70px 0 rgba(0,0,0,0.95), inset 0 1px 0 0 rgba(255,255,255,0.08)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/[0.08] shrink-0">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
              <MessageSquare className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white">Share Platform Feedback</h2>
              <p className="text-[11px] font-mono text-neutral-400">Help the KAVACH development team improve your workflow</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close feedback modal"
            className="p-1.5 rounded-lg text-neutral-400 hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form with scrollable body & pinned footer */}
        <form onSubmit={handleSubmit} className="flex flex-col flex-1 min-h-0">
          {/* Scrollable Fields */}
          <div className="py-4 space-y-4 overflow-y-auto flex-1 min-h-0 pr-1.5 scrollbar-thin">
            {/* Star Rating */}
            <div>
              <label className="block text-[11px] font-mono text-neutral-400 uppercase tracking-wider mb-2">
                Overall Experience (1 to 5)
              </label>
              <div className="flex items-center space-x-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    type="button"
                    key={star}
                    onClick={() => setRating(star)}
                    className="p-1 text-neutral-600 hover:text-amber-400 transition-colors cursor-pointer"
                  >
                    <Star
                      className={`w-6 h-6 ${
                        star <= rating ? 'text-amber-400 fill-amber-400' : 'text-neutral-700'
                      }`}
                    />
                  </button>
                ))}
                <span className="text-xs font-mono text-neutral-300 ml-2">
                  {rating === 5 ? 'Excellent' : rating === 4 ? 'Good' : rating === 3 ? 'Average' : rating === 2 ? 'Needs Improvement' : 'Poor'}
                </span>
              </div>
            </div>

            {/* What worked well */}
            <div>
              <label className="block text-[11px] font-mono text-neutral-400 uppercase tracking-wider mb-1.5">
                What Worked Well?
              </label>
              <textarea
                value={whatWorked}
                onChange={(e) => setWhatWorked(e.target.value)}
                placeholder="e.g. Fast scanner execution, clear forensic evidence verification..."
                rows={2}
                className="w-full rounded-xl p-3 text-xs text-white placeholder-neutral-600 font-sans focus:outline-none focus:border-white/20 resize-none"
                style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  borderColor: 'rgba(255, 255, 255, 0.08)',
                  borderWidth: '1px'
                }}
              />
            </div>

            {/* What was confusing or difficult */}
            <div>
              <label className="block text-[11px] font-mono text-neutral-400 uppercase tracking-wider mb-1.5">
                What Was Confusing or Difficult to Use?
              </label>
              <textarea
                value={whatConfusing}
                onChange={(e) => setWhatConfusing(e.target.value)}
                placeholder="e.g. Stage stepper navigation, finding details view..."
                rows={2}
                className="w-full rounded-xl p-3 text-xs text-white placeholder-neutral-600 font-sans focus:outline-none focus:border-white/20 resize-none"
                style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  borderColor: 'rgba(255, 255, 255, 0.08)',
                  borderWidth: '1px'
                }}
              />
            </div>

            {/* Bug description */}
            <div>
              <label className="block text-[11px] font-mono text-neutral-400 uppercase tracking-wider mb-1.5">
                Bug Report / Unexpected Behavior
              </label>
              <textarea
                value={bugDescription}
                onChange={(e) => setBugDescription(e.target.value)}
                placeholder="Describe any error or unexpected glitch you observed..."
                rows={2}
                className="w-full rounded-xl p-3 text-xs text-white placeholder-neutral-600 font-sans focus:outline-none focus:border-white/20 resize-none"
                style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  borderColor: 'rgba(255, 255, 255, 0.08)',
                  borderWidth: '1px'
                }}
              />
            </div>

            {/* Suggestions */}
            <div>
              <label className="block text-[11px] font-mono text-neutral-400 uppercase tracking-wider mb-1.5">
                Feature Suggestions / Improvements
              </label>
              <textarea
                value={suggestions}
                onChange={(e) => setSuggestions(e.target.value)}
                placeholder="Any idea for improving KAVACH security workflows..."
                rows={2}
                className="w-full rounded-xl p-3 text-xs text-white placeholder-neutral-600 font-sans focus:outline-none focus:border-white/20 resize-none"
                style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  borderColor: 'rgba(255, 255, 255, 0.08)',
                  borderWidth: '1px'
                }}
              />
            </div>
          </div>

          {/* Fixed Footer Actions */}
          <div className="pt-3 border-t border-white/[0.08] flex items-center justify-end space-x-2 shrink-0">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-mono text-neutral-400 hover:text-white hover:bg-white/[0.06] transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="btn-primary px-5 py-2 rounded-xl text-xs font-semibold flex items-center space-x-1.5 disabled:opacity-50 cursor-pointer"
            >
              {submitting ? (
                <span>Submitting...</span>
              ) : (
                <>
                  <Send className="w-3.5 h-3.5" />
                  <span>Send Feedback</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );

  return typeof document !== 'undefined'
    ? createPortal(modalNode, document.body)
    : modalNode;
};

