import axios from '../api/axios';
import { Notification } from '../types/notification';

export const notificationService = {
  getNotifications: async (skip = 0, limit = 50, unreadOnly = false): Promise<Notification[]> => {
    const response = await axios.get('/notifications/', {
      params: { skip, limit, unread_only: unreadOnly }
    });
    return response.data;
  },

  getUnreadCount: async (): Promise<number> => {
    const response = await axios.get('/notifications/unread-count');
    return response.data.count;
  },

  markAsRead: async (notificationId: number): Promise<void> => {
    await axios.post(`/notifications/${notificationId}/read`);
  },

  markAllAsRead: async (): Promise<void> => {
    await axios.post('/notifications/read-all');
  },
};