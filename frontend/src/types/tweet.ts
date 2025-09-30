import { UserPublic } from './user';

export interface Tweet {
  id: number;
  content: string;
  image_url?: string;
  author_id: number;
  reply_to_id?: number;
  created_at: string;
  author: UserPublic;
  likes_count: number;
  retweets_count: number;
  replies_count: number;
  is_liked_by_user: boolean;
  is_retweeted_by_user: boolean;
  reply_to?: TweetSimple;
}

export interface TweetSimple {
  id: number;
  content: string;
  author: UserPublic;
  created_at: string;
}

export interface CreateTweetData {
  content: string;
  image_url?: string;
  reply_to_id?: number;
}