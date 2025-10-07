export interface Notification {
  id?: number;
  type: 'connection' | 'new_tweet' | 'new_like' | 'new_retweet' | 'new_reply' | 'new_follower' | 'new_message';
  message: string;
  related_id?: number;
  related_username?: string;
  is_read?: boolean;
  created_at?: string;
  data?: any;
  timestamp: string;
}