import React, { useState, useRef, useEffect } from "react";
import {
  Send,
  Bot,
  User,
  Zap,
  FileText,
  Brain,
  Wifi,
  WifiOff,
} from "lucide-react";
import { useChatbot } from "../hooks/useChatbot";

const Chatbot: React.FC = () => {
  const [inputText, setInputText] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Use the custom hook for chatbot functionality
  const { messages, isTyping, sendMessage, isConnected } = useChatbot(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputText.trim() || isTyping) return;

    const messageToSend = inputText;
    setInputText("");
    await sendMessage(messageToSend);
  };

  const quickQuestions = [
    "What does this MRI finding mean?",
    "Explain my CT scan results",
    "How to interpret contrast enhancement?",
    "What are normal brain MRI findings?",
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          AI Medical Assistant
        </h2>
        <p className="text-gray-600">
          Get instant answers to your medical imaging questions
        </p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 h-96">
        {/* Chat Header */}
        <div className="p-4 border-b border-gray-200 flex items-center space-x-3">
          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
            <Bot className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h3 className="font-medium text-gray-900">MedScope AI Assistant</h3>
            <div className="flex items-center space-x-1">
              {isConnected ? (
                <>
                  <Wifi className="w-3 h-3 text-green-500" />
                  <p className="text-sm text-green-600">Online</p>
                </>
              ) : (
                <>
                  <WifiOff className="w-3 h-3 text-red-500" />
                  <p className="text-sm text-red-600">Connection issues</p>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 h-64">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`flex items-start space-x-2 max-w-xs lg:max-w-md ${
                  message.sender === "user"
                    ? "flex-row-reverse space-x-reverse"
                    : ""
                }`}
              >
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    message.sender === "user" ? "bg-blue-600" : "bg-gray-200"
                  }`}
                >
                  {message.sender === "user" ? (
                    <User className="w-4 h-4 text-white" />
                  ) : (
                    <Bot className="w-4 h-4 text-gray-600" />
                  )}
                </div>
                <div
                  className={`rounded-lg px-4 py-2 ${
                    message.sender === "user"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-gray-900"
                  }`}
                >
                  <p className="text-sm">{message.text}</p>
                  <p
                    className={`text-xs mt-1 ${
                      message.sender === "user"
                        ? "text-blue-200"
                        : "text-gray-500"
                    }`}
                  >
                    {message.timestamp.toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                </div>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex justify-start">
              <div className="flex items-start space-x-2">
                <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                  <Bot className="w-4 h-4 text-gray-600" />
                </div>
                <div className="bg-gray-100 rounded-lg px-4 py-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0.1s" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0.2s" }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex space-x-2">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) =>
                e.key === "Enter" && !e.shiftKey && handleSendMessage()
              }
              placeholder="Ask about medical imaging, reports, or clinical questions..."
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputText.trim() || isTyping}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white p-2 rounded-lg transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          {!isConnected && (
            <p className="text-xs text-red-500 mt-2">
              Connection lost. Messages will be processed when connection is
              restored.
            </p>
          )}
        </div>
      </div>

      {/* Quick Questions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Zap className="w-5 h-5 mr-2 text-blue-600" />
            Quick Questions
          </h3>
        </div>
        <div className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {quickQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => setInputText(question)}
                className="text-left p-3 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
              >
                <p className="text-sm text-gray-700">{question}</p>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* AI Capabilities */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <Brain className="w-8 h-8 text-blue-600 mb-2" />
          <h4 className="font-medium text-blue-900 mb-1">Advanced Analysis</h4>
          <p className="text-sm text-blue-800">
            Deep learning-powered medical image interpretation
          </p>
        </div>

        <div className="bg-teal-50 border border-teal-200 rounded-lg p-4">
          <FileText className="w-8 h-8 text-teal-600 mb-2" />
          <h4 className="font-medium text-teal-900 mb-1">
            Report Interpretation
          </h4>
          <p className="text-sm text-teal-800">
            Clear explanations of complex medical terminology
          </p>
        </div>

        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <Zap className="w-8 h-8 text-purple-600 mb-2" />
          <h4 className="font-medium text-purple-900 mb-1">
            Real-time Support
          </h4>
          <p className="text-sm text-purple-800">
            Instant answers to clinical questions 24/7
          </p>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
