import React, { useState } from "react";
import { X, Star, Send, CheckCircle } from "lucide-react";

interface FeedbackPopupProps {
  isVisible: boolean;
  onClose: () => void;
  analysisId?: string;
  onFeedbackSubmitted?: () => void;
}

const FeedbackPopup: React.FC<FeedbackPopupProps> = ({
  isVisible,
  onClose,
  analysisId = "unknown",
  onFeedbackSubmitted,
}) => {
  const [feedback, setFeedback] = useState("");
  const [rating, setRating] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [category, setCategory] = useState("");

  const categories = [
    { value: "accuracy", label: "Analysis Accuracy" },
    { value: "speed", label: "Processing Speed" },
    { value: "usability", label: "Ease of Use" },
    { value: "report_quality", label: "Report Quality" },
    { value: "suggestions", label: "Suggestions" },
    { value: "other", label: "Other" },
  ];

  const handleSubmit = async () => {
    if (!feedback.trim() || rating === 0) {
      return;
    }

    setIsSubmitting(true);

    try {
      const feedbackData = {
        feedback: feedback.trim(),
        rating,
        category,
        analysis_id: analysisId,
        timestamp: new Date().toISOString(),
      };

      const response = await fetch(
        "http://localhost:8000/api/v1/scan/feedback",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(feedbackData),
        }
      );

      if (response.ok) {
        setIsSubmitted(true);
        if (onFeedbackSubmitted) {
          onFeedbackSubmitted();
        }

        // Auto close after 2 seconds
        setTimeout(() => {
          handleClose();
        }, 2000);
      } else {
        console.error("Failed to submit feedback");
      }
    } catch (error) {
      console.error("Error submitting feedback:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setFeedback("");
    setRating(0);
    setCategory("");
    setIsSubmitted(false);
    setIsSubmitting(false);
    onClose();
  };

  const renderStars = () => {
    return [...Array(5)].map((_, index) => (
      <button
        key={index}
        type="button"
        onClick={() => setRating(index + 1)}
        className={`text-2xl transition-colors ${
          index < rating
            ? "text-yellow-400"
            : "text-gray-300 hover:text-yellow-300"
        }`}
      >
        <Star className={`w-6 h-6 ${index < rating ? "fill-current" : ""}`} />
      </button>
    ));
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b">
          <h3 className="text-lg font-semibold text-gray-800">
            {isSubmitted ? "Thank You!" : "How was your experience?"}
          </h3>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {isSubmitted ? (
            <div className="text-center py-8">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <h4 className="text-xl font-semibold text-gray-800 mb-2">
                Feedback Submitted!
              </h4>
              <p className="text-gray-600">
                Thank you for helping us improve our AI analysis for better
                patient care.
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Rating */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Overall Rating
                </label>
                <div className="flex space-x-1">{renderStars()}</div>
                <p className="text-xs text-gray-500 mt-1">
                  {rating === 0 && "Please rate your experience"}
                  {rating === 1 && "Very Poor"}
                  {rating === 2 && "Poor"}
                  {rating === 3 && "Fair"}
                  {rating === 4 && "Good"}
                  {rating === 5 && "Excellent"}
                </p>
              </div>

              {/* Category */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Feedback Category
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select a category</option>
                  {categories.map((cat) => (
                    <option key={cat.value} value={cat.value}>
                      {cat.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Feedback Text */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Your Feedback
                </label>
                <textarea
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  placeholder="Please share your thoughts about the analysis accuracy, suggestions for improvement, or any issues you encountered..."
                  rows={4}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                />
                <p className="text-xs text-gray-500 mt-1">
                  {feedback.length}/500 characters
                </p>
              </div>

              {/* Submit Button */}
              <div className="flex space-x-3">
                <button
                  onClick={handleClose}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
                >
                  Skip
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={!feedback.trim() || rating === 0 || isSubmitting}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
                >
                  {isSubmitting ? (
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Submitting...
                    </div>
                  ) : (
                    <>
                      <Send className="w-4 h-4 mr-2" />
                      Submit
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        {!isSubmitted && (
          <div className="px-6 pb-6">
            <p className="text-xs text-gray-500 text-center">
              Your feedback helps us improve our AI analysis for better
              healthcare outcomes. All feedback is anonymous and used solely for
              improving our service.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default FeedbackPopup;
