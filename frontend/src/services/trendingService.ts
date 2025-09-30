import axios from '../api/axios';

export interface TrendingHashtag {
  tag: string;
  count: number;
  tweets_count: number;
}

export const trendingService = {
  getTrendingHashtags: async (limit = 10): Promise<TrendingHashtag[]> => {
    const response = await axios.get('/trending/hashtags', {
      params: { limit }
    });
    return response.data;
  },
};