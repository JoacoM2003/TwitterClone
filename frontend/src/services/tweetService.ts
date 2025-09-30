import axios from '../api/axios';
import { Tweet, CreateTweetData } from '../types/tweet';

export const tweetService = {
  getPublicTweets: async (skip = 0, limit = 20): Promise<Tweet[]> => {
    const response = await axios.get('/tweets/', { params: { skip, limit } });
    // Filtrar solo tweets originales (sin reply_to_id)
    return response.data.filter((tweet: Tweet) => !tweet.reply_to_id);
  },

  getFeed: async (skip = 0, limit = 20): Promise<Tweet[]> => {
    const response = await axios.get('/tweets/feed', { params: { skip, limit } });
    // Filtrar solo tweets originales (sin reply_to_id)
    return response.data.filter((tweet: Tweet) => !tweet.reply_to_id);
  },

  getTweet: async (id: number): Promise<Tweet> => {
    const response = await axios.get(`/tweets/${id}`);
    return response.data;
  },

  createTweet: async (data: CreateTweetData): Promise<Tweet> => {
    const response = await axios.post('/tweets/', data);
    return response.data;
  },

  deleteTweet: async (id: number): Promise<void> => {
    await axios.delete(`/tweets/${id}`);
  },

  getReplies: async (tweetId: number): Promise<Tweet[]> => {
    const response = await axios.get(`/tweets/${tweetId}/replies`);
    return response.data;
  },

  getThread: async (tweetId: number) => {
    const response = await axios.get(`/tweets/${tweetId}/thread`);
    return response.data;
  },

  getUserTweets: async (username: string, skip = 0, limit = 20): Promise<Tweet[]> => {
    const response = await axios.get(`/tweets/user/${username}`, { params: { skip, limit } });
    return response.data;
  },

  likeTweet: async (tweetId: number): Promise<void> => {
    await axios.post(`/likes/${tweetId}`);
  },

  unlikeTweet: async (tweetId: number): Promise<void> => {
    await axios.delete(`/likes/${tweetId}`);
  },

  retweet: async (tweetId: number, comment?: string): Promise<void> => {
    await axios.post(`/retweets/${tweetId}`, comment ? { comment } : {});
  },

  unretweet: async (tweetId: number): Promise<void> => {
    await axios.delete(`/retweets/${tweetId}`);
  },
};