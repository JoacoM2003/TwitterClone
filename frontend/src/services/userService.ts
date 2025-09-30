import axios from '../api/axios';
import { User, UserPublic } from '../types/user';

export const userService = {
  getUser: async (username: string): Promise<UserPublic> => {
    const response = await axios.get(`/users/${username}`);
    return response.data;
  },

  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await axios.put('/users/me', data);
    return response.data;
  },

  followUser: async (username: string): Promise<void> => {
    await axios.post(`/users/${username}/follow`);
  },

  unfollowUser: async (username: string): Promise<void> => {
    await axios.delete(`/users/${username}/follow`);
  },

  isFollowing: async (username: string): Promise<boolean> => {
    const response = await axios.get(`/users/${username}/is-following`);
    return response.data.is_following;
  },
};