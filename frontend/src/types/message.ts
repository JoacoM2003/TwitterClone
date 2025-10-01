import { UserPublic } from './user';

export interface Message {
  id: number;
  content: string;
  sender: UserPublic;
  is_read: boolean;
  created_at: string;
}

export interface Conversation {
  id: number;
  other_user: UserPublic;
  last_message?: {
    id: number;
    content: string;
    sender_id: number;
    created_at: string;
  };
  unread_count: number;
  updated_at: string;
}

export interface SendMessageData {
  receiver_username: string;
  content: string;
}