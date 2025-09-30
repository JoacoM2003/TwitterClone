import axios from '../api/axios';
import { UserPublic } from '../types/user';
import { Tweet } from '../types/tweet';

export const searchService = {
  searchUsers: async (query: string, limit = 10): Promise<UserPublic[]> => {
    const response = await axios.get('/search/users', {
      params: { q: query, limit }
    });
    return response.data;
  },

  searchTweets: async (query: string, skip = 0, limit = 20): Promise<Tweet[]> => {
    const response = await axios.get('/search/tweets', {
      params: { q: query, skip, limit }
    });
    return response.data;
  },

  searchHashtags: async (query: string, skip = 0, limit = 20): Promise<Tweet[]> => {
    const response = await axios.get('/search/hashtags', {
      params: { q: query, skip, limit }
    });
    return response.data;
  },
};