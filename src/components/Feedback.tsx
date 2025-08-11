import React, { useState, useEffect } from "react";
import { Star, MessageCircle, Send, CheckCircle, AlertTriangle } from "lucide-react";
import { Client, Databases, ID } from 'appwrite';

const APPWRITE_ENDPOINT = import.meta.env.VITE_APPWRITE_ENDPOINT; 
const APPWRITE_PROJECT_ID = import.meta.env.VITE_APPWRITE_PROJECT_ID; 
const APPWRITE_DATABASE_ID = import.meta.env.VITE_APPWRITE_DATABASE_ID; 
const APPWRITE_COLLECTION_ID = import.meta.env.VITE_APPWRITE_COLLECTION1_ID;

const client = new Client();

if (APPWRITE_PROJECT_ID) {
    client
        .setEndpoint(APPWRITE_ENDPOINT)
        .setProject(APPWRITE_PROJECT_ID);
}

const databases = new Databases(client);

const Feedback = () => {
  
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [feedbackType, setFeedbackType] = useState("general");
  const [message, setMessage] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState(null);
  const [isConfigured, setIsConfigured] = useState(true);


  useEffect(() => {
    if (!APPWRITE_PROJECT_ID || !APPWRITE_DATABASE_ID) {
      console.error("Appwrite environment variables are not set. Please check your .env.local file.");
      setError("This form is not configured correctly. Please contact support.");
      setIsConfigured(false);
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isConfigured) return; 

    setIsSubmitting(true);
    setError(null);

    if (rating === 0 || message.trim() === "") {
        setError("Please provide a rating and a message before submitting.");
        setIsSubmitting(false);
        return;
    }

    try {
      await databases.createDocument(
        APPWRITE_DATABASE_ID,
        APPWRITE_COLLECTION_ID,
        ID.unique(),
        {
          rating: rating,
          type: feedbackType,
          message: message,
          name: name,
          email: email,
        }
      );
      
      setIsSubmitted(true);
      setTimeout(() => {

        setIsSubmitted(false);
        setRating(0);
        setFeedbackType("general");
        setMessage("");
        setName("");
        setEmail("");
      }, 3000);

    } catch (err) {
      console.error("Appwrite submission error:", err);
      setError("Sorry, something went wrong. Please try again later.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const feedbackTypes = [
    { id: "general", label: "General Feedback", description: "Overall experience with MedScope AI" },
    { id: "bug", label: "Bug Report", description: "Report technical issues or errors" },
    { id: "feature", label: "Feature Request", description: "Suggest new features or improvements" },
    { id: "ui", label: "UI/UX Feedback", description: "Interface design and usability feedback" },
  ];
  
  if (isSubmitted) {
    return (
      <div className="space-y-6 bg-slate-900 text-slate-100 p-6 min-h-screen flex items-center justify-center">
          <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl shadow-lg border border-slate-700/50 p-8 max-w-md w-full">
            <div className="text-center">
              <CheckCircle className="w-16 h-16 text-emerald-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Thank You!</h3>
              <p className="text-slate-300 mb-4">Your feedback has been submitted successfully.</p>
              <p className="text-sm text-slate-400">We appreciate your input and will review it shortly.</p>
            </div>
          </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 bg-slate-900 text-slate-100 p-6 min-h-screen">
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">Feedback & Support</h2>
        <p className="text-slate-400">Help us improve MedScope AI with your valuable feedback</p>
      </div>

      <div className="max-w-4xl mx-auto">
        <form onSubmit={handleSubmit}>
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
                <label className="block text-sm font-medium text-slate-300 mb-3">Overall Rating *</label>
                <div className="flex items-center space-x-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button type="button" key={star} onClick={() => setRating(star)} onMouseEnter={() => setHoveredRating(star)} onMouseLeave={() => setHoveredRating(0)} className="focus:outline-none">
                      <Star className={`w-8 h-8 transition-colors ${(hoveredRating || rating) >= star ? "text-amber-400 fill-current" : "text-slate-500"}`} />
                    </button>
                  ))}
                  {rating > 0 && <span className="ml-2 text-sm text-slate-400">{["Very Poor", "Poor", "Average", "Good", "Excellent"][rating - 1]}</span>}
                </div>
              </div>

              {/* Feedback Type */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-3">Feedback Type</label>
                <div className="space-y-2">
                  {feedbackTypes.map((type) => (
                    <label key={type.id} className="flex items-start space-x-3 cursor-pointer">
                      <input type="radio" name="feedbackType" value={type.id} checked={feedbackType === type.id} onChange={(e) => setFeedbackType(e.target.value)} className="mt-1 w-4 h-4 text-blue-500 bg-slate-700 border-slate-600 focus:ring-blue-500 focus:ring-2" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-slate-200">{type.label}</p>
                        <p className="text-xs text-slate-400">{type.description}</p>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Message */}
              <div>
                <label htmlFor="feedback-message" className="block text-sm font-medium text-slate-300 mb-2">Your Feedback *</label>
                <textarea id="feedback-message" rows={4} value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Please share your thoughts, suggestions, or report any issues..." className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none" />
              </div>

              {/* Contact Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-slate-300 mb-2">Name (Optional)</label>
                  <input id="name" type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Your name" className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
                </div>
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-slate-300 mb-2">Email (Optional)</label>
                  <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="your@email.com" className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
                </div>
              </div>

              {/* Error Message */}
              {error && (
                  <div className="bg-red-900/50 border border-red-500/30 text-red-300 text-sm rounded-lg p-3 flex items-center space-x-2">
                      <AlertTriangle className="w-5 h-5" />
                      <span>{error}</span>
                  </div>
              )}

              {/* Submit Button */}
              <button type="submit" disabled={isSubmitting || !isConfigured} className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg transition-colors flex items-center justify-center space-x-2 border border-blue-500/30">
                <Send className="w-4 h-4" />
                <span>{isSubmitting ? 'Submitting...' : 'Submit Feedback'}</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Feedback;
