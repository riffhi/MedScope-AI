import { useState, useCallback } from "react";
import { chatAPI, APIMessage } from "../services/chatAPI";

export interface ChatMessage {
  id: string;
  text: string;
  sender: "user" | "bot";
  timestamp: Date;
}

export interface UseChatbotReturn {
  messages: ChatMessage[];
  isTyping: boolean;
  sendMessage: (message: string) => Promise<void>;
  clearMessages: () => void;
  isConnected: boolean;
}

export const useChatbot = (
  isAuthenticated = false,
  token?: string
): UseChatbotReturn => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      text: "Hello! I'm your AI medical assistant. I can help you with medical imaging analysis, interpret reports, and answer clinical questions. How can I assist you today?",
      sender: "bot",
      timestamp: new Date(),
    },
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [isConnected, setIsConnected] = useState(true);

  const sendMessage = useCallback(
    async (messageText: string) => {
      if (!messageText.trim()) return;

      // Add user message
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        text: messageText,
        sender: "user",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsTyping(true);

      try {
        let response: APIMessage;

        if (isAuthenticated && token) {
          // Use authenticated endpoint
          response = await chatAPI.sendMessage(messageText, undefined, token);
        } else {
          // Use anonymous endpoint
          response = await chatAPI.sendAnonymousMessage(messageText);
        }

        // Add bot response
        const botMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          text: response.response,
          sender: "bot",
          timestamp: new Date(response.timestamp),
        };

        setMessages((prev) => [...prev, botMessage]);
        setIsConnected(true);
      } catch (error) {
        console.error("Failed to send message:", error);
        setIsConnected(false);

        // Add fallback error message
        const errorMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          text: "I'm sorry, I'm having trouble connecting to the server right now. Please try again later or check your internet connection.",
          sender: "bot",
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsTyping(false);
      }
    },
    [isAuthenticated, token]
  );

  const clearMessages = useCallback(() => {
    setMessages([
      {
        id: "1",
        text: "Hello! I'm your AI medical assistant. I can help you with medical imaging analysis, interpret reports, and answer clinical questions. How can I assist you today?",
        sender: "bot",
        timestamp: new Date(),
      },
    ]);
  }, []);

  return {
    messages,
    isTyping,
    sendMessage,
    clearMessages,
    isConnected,
  };
};
