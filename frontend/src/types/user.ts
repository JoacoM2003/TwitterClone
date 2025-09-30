export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  bio?: string;
  avatar_url?: string;
  followers_count?: number;
  following_count?: number;
  created_at: string;
}

export interface UserPublic {
  id: number;
  username: string;
  full_name?: string;
  bio?: string;
  avatar_url?: string;
  followers_count?: number;
  following_count?: number;
}