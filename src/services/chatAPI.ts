// API service for chatbot integration
const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

export interface ChatMessage {
  id: string;
  text: string;
  sender: "user" | "bot";
  timestamp: Date;
}

export interface APIMessage {
  message: string;
  response: string;
  timestamp: string;
  session_id?: number;
}

export interface ChatSession {
  id: number;
  session_name: string;
  created_at: string;
  updated_at: string;
}

class ChatAPI {
  // Send message without authentication (for popup chatbot)
  async sendAnonymousMessage(message: string): Promise<APIMessage> {
    const response = await fetch(`${API_BASE_URL}/chat/message-anonymous`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error("Failed to send message");
    }

    return response.json();
  }

  // Send message with authentication (for logged-in users)
  async sendMessage(
    message: string,
    sessionId?: number,
    token?: string
  ): Promise<APIMessage> {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/chat/message`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    });

    if (!response.ok) {
      throw new Error("Failed to send message");
    }

    return response.json();
  }

  // Create new chat session
  async createChatSession(
    sessionName?: string,
    token?: string
  ): Promise<ChatSession> {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
      method: "POST",
      headers,
      body: JSON.stringify({ session_name: sessionName }),
    });

    if (!response.ok) {
      throw new Error("Failed to create chat session");
    }

    return response.json();
  }

  // Get all chat sessions
  async getChatSessions(token: string): Promise<ChatSession[]> {
    const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to get chat sessions");
    }

    return response.json();
  }

  // Get messages for a specific session
  async getChatMessages(
    sessionId: number,
    token: string
  ): Promise<APIMessage[]> {
    const response = await fetch(
      `${API_BASE_URL}/chat/sessions/${sessionId}/messages`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error("Failed to get chat messages");
    }

    return response.json();
  }

  // Check if backend is available
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}

export const chatAPI = new ChatAPI();
