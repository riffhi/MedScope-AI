import React, { useState } from "react";
import { Star, MessageCircle, Send, CheckCircle } from "lucide-react";

const Feedback: React.FC = () => {
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [feedbackType, setFeedbackType] = useState("general");
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = () => {
    // Here you would normally submit to Google Forms
    // For demo purposes, we'll just show success
    setIsSubmitted(true);
    setTimeout(() => {
      setIsSubmitted(false);
      setRating(0);
    }, 3000);
  };

  const feedbackTypes = [
    {
      id: "general",
      label: "General Feedback",
      description: "Overall experience with MedScope AI",
    },
    {
      id: "bug",
      label: "Bug Report",
      description: "Report technical issues or errors",
    },
    {
      id: "feature",
      label: "Feature Request",
      description: "Suggest new features or improvements",
    },
    {
      id: "ui",
      label: "UI/UX Feedback",
      description: "Interface design and usability feedback",
    },
  ];

  return (
    <div className="space-y-6 bg-slate-900 text-slate-100 p-6 min-h-screen">
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">
          Feedback & Support
        </h2>
        <p className="text-slate-400">
          Help us improve MedScope AI with your valuable feedback
        </p>
      </div>

      {isSubmitted ? (
        <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl shadow-lg border border-slate-700/50 p-8">
          <div className="text-center">
            <CheckCircle className="w-16 h-16 text-emerald-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">
              Thank You!
            </h3>
            <p className="text-slate-300 mb-4">
              Your feedback has been submitted successfully.
            </p>
            <p className="text-sm text-slate-400">
              We appreciate your input and will review it shortly.
            </p>
          </div>
        </div>
      ) : (
        <div className="max-w-4xl mx-auto">
          {/* Feedback Form */}
          <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl shadow-lg border border-slate-700/50">
            <div className="p-6 border-b border-slate-700/50">
              <h3 className="text-lg font-semibold text-white flex items-center">
                <MessageCircle className="w-5 h-5 mr-2 text-blue-400" />
                Submit Feedback
              </h3>
            </div>

            <div className="p-6 space-y-6">
              {/* Rating */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-3">
                  Overall Rating
                </label>
                <div className="flex items-center space-x-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      onClick={() => setRating(star)}
                      onMouseEnter={() => setHoveredRating(star)}
                      onMouseLeave={() => setHoveredRating(0)}
                      className="focus:outline-none"
                    >
                      <Star
                        className={`w-8 h-8 transition-colors ${
                          (hoveredRating || rating) >= star
                            ? "text-amber-400 fill-current"
                            : "text-slate-500"
                        }`}
                      />
                    </button>
                  ))}
                  {rating > 0 && (
                    <span className="ml-2 text-sm text-slate-400">
                      {rating === 5
                        ? "Excellent"
                        : rating === 4
                        ? "Good"
                        : rating === 3
                        ? "Average"
                        : rating === 2
                        ? "Poor"
                        : "Very Poor"}
                    </span>
                  )}
                </div>
              </div>

              {/* Feedback Type */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-3">
                  Feedback Type
                </label>
                <div className="space-y-2">
                  {feedbackTypes.map((type) => (
                    <label key={type.id} className="flex items-start space-x-3">
                      <input
                        type="radio"
                        name="feedbackType"
                        value={type.id}
                        checked={feedbackType === type.id}
                        onChange={(e) => setFeedbackType(e.target.value)}
                        className="mt-1 w-4 h-4 text-blue-500 bg-slate-700 border-slate-600 focus:ring-blue-500 focus:ring-2"
                      />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-slate-200">
                          {type.label}
                        </p>
                        <p className="text-xs text-slate-400">
                          {type.description}
                        </p>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Message */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Your Feedback
                </label>
                <textarea
                  rows={4}
                  placeholder="Please share your thoughts, suggestions, or report any issues..."
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                />
              </div>

              {/* Contact Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Name (Optional)
                  </label>
                  <input
                    type="text"
                    placeholder="Your name"
                    className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Email (Optional)
                  </label>
                  <input
                    type="email"
                    placeholder="your@email.com"
                    className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Submit Button */}
              <button
                onClick={handleSubmit}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors flex items-center justify-center space-x-2 border border-blue-500/30"
              >
                <Send className="w-4 h-4" />
                <span>Submit Feedback</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Feedback;
