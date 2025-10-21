import { Notification } from '../types/notification';

const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/api/v1/ws';

console.log('🔌 WebSocket URL:', WS_URL);

class WebSocketService {
  private ws: WebSocket | null = null;
  private listeners: ((notification: Notification) => void)[] = [];
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private token: string | null = null;

  connect(token: string) {
    this.token = token;
    const wsUrl = `${WS_URL}/notifications?token=${token}`;
    console.log('Connecting to WebSocket:', wsUrl);
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('✅ WebSocket connected');
    };

    this.ws.onmessage = (event) => {
      const notification: Notification = JSON.parse(event.data);
      this.listeners.forEach((listener) => listener(notification));
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.reconnectTimeout = setTimeout(() => {
        if (this.token) {
          this.connect(this.token);
        }
      }, 5000);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send('ping');
      }
    }, 30000);
  }

  disconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.token = null;
  }

  subscribe(callback: (notification: Notification) => void) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== callback);
    };
  }
}

export const websocketService = new WebSocketService();