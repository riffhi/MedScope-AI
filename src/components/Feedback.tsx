import React, { useState } from 'react';
import { Star, MessageCircle, Send, CheckCircle } from 'lucide-react';

const Feedback: React.FC = () => {
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [feedbackType, setFeedbackType] = useState('general');
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
    { id: 'general', label: 'General Feedback', description: 'Overall experience with MedScope AI' },
    { id: 'bug', label: 'Bug Report', description: 'Report technical issues or errors' },
    { id: 'feature', label: 'Feature Request', description: 'Suggest new features or improvements' },
    { id: 'ui', label: 'UI/UX Feedback', description: 'Interface design and usability feedback' }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Feedback & Support</h2>
        <p className="text-gray-600">Help us improve MedScope AI with your valuable feedback</p>
      </div>

      {isSubmitted ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <div className="text-center">
            <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Thank You!</h3>
            <p className="text-gray-600 mb-4">Your feedback has been submitted successfully.</p>
            <p className="text-sm text-gray-500">We appreciate your input and will review it shortly.</p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Feedback Form */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <MessageCircle className="w-5 h-5 mr-2 text-blue-600" />
                Submit Feedback
              </h3>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Rating */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
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
                            ? 'text-yellow-400 fill-current'
                            : 'text-gray-300'
                        }`}
                      />
                    </button>
                  ))}
                  {rating > 0 && (
                    <span className="ml-2 text-sm text-gray-600">
                      {rating === 5 ? 'Excellent' : rating === 4 ? 'Good' : rating === 3 ? 'Average' : rating === 2 ? 'Poor' : 'Very Poor'}
                    </span>
                  )}
                </div>
              </div>

              {/* Feedback Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
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
                        className="mt-1 w-4 h-4 text-blue-600 focus:ring-blue-500"
                      />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">{type.label}</p>
                        <p className="text-xs text-gray-500">{type.description}</p>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Message */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Your Feedback
                </label>
                <textarea
                  rows={4}
                  placeholder="Please share your thoughts, suggestions, or report any issues..."
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                />
              </div>

              {/* Contact Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Name (Optional)
                  </label>
                  <input
                    type="text"
                    placeholder="Your name"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email (Optional)
                  </label>
                  <input
                    type="email"
                    placeholder="your@email.com"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Submit Button */}
              <button
                onClick={handleSubmit}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors flex items-center justify-center space-x-2"
              >
                <Send className="w-4 h-4" />
                <span>Submit Feedback</span>
              </button>
            </div>
          </div>

          {/* Contact & Support */}
          <div className="space-y-6">
            {/* Quick Support */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Quick Support</h3>
              </div>
              <div className="p-6 space-y-4">
                <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <MessageCircle className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Live Chat</h4>
                    <p className="text-sm text-gray-600">Get instant help from our AI assistant</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
                  <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                    <span className="text-green-600 font-semibold">?</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Documentation</h4>
                    <p className="text-sm text-gray-600">Browse our comprehensive user guides</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3 p-3 bg-purple-50 rounded-lg">
                  <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                    <span className="text-purple-600 font-semibold">📧</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Email Support</h4>
                    <p className="text-sm text-gray-600">support@medscope-ai.com</p>
                  </div>
                </div>
              </div>
            </div>

            {/* System Status */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">System Status</h3>
              </div>
              <div className="p-6 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700">API Status</span>
                  <span className="flex items-center text-sm text-green-600">
                    <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                    Operational
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700">AI Processing</span>
                  <span className="flex items-center text-sm text-green-600">
                    <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                    Normal
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700">File Upload</span>
                  <span className="flex items-center text-sm text-green-600">
                    <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                    Available
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700">3D Visualization</span>
                  <span className="flex items-center text-sm text-yellow-600">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></div>
                    Maintenance
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Feedback;