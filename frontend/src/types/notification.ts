export interface Notification {
  type: 'connection' | 'new_tweet' | 'new_like' | 'new_retweet' | 'new_reply' | 'new_follower';
  data?: any;
  message?: string;
  timestamp: string;
}