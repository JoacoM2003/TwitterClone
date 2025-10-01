import axios from '../api/axios';
import { Message, Conversation, SendMessageData } from '../types/message';

export const messageService = {
  sendMessage: async (data: SendMessageData): Promise<void> => {
    await axios.post('/messages/send', data);
  },

  getConversations: async (): Promise<Conversation[]> => {
    const response = await axios.get('/messages/conversations');
    return response.data;
  },

  getMessages: async (username: string, skip = 0, limit = 50): Promise<Message[]> => {
    const response = await axios.get(`/messages/${username}`, {
      params: { skip, limit }
    });
    return response.data;
  },

  markAsRead: async (username: string): Promise<void> => {
    await axios.post(`/messages/${username}/read`);
  },
};