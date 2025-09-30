import React, { useState, useEffect } from 'react';
import { UserPublic } from '../../types/user';
import { Tweet } from '../../types/tweet';
import { userService } from '../../services/userService';
import { tweetService } from '../../services/tweetService';
import { TweetList } from '../tweet/TweetList';
import { useAuth } from '../../contexts/AuthContext';

interface UserProfileProps {
  username: string;
}

export const UserProfile: React.FC<UserProfileProps> = ({ username }) => {
  const [user, setUser] = useState<UserPublic | null>(null);
  const [tweets, setTweets] = useState<Tweet[]>([]);
  const [loading, setLoading] = useState(true);
  const [isFollowing, setIsFollowing] = useState(false);
  const [followLoading, setFollowLoading] = useState(false);
  const { user: currentUser } = useAuth();
  const isOwnProfile = currentUser?.username === username;

  useEffect(() => {
    loadProfile();
  }, [username]);

  const loadProfile = async () => {
    setLoading(true);
    try {
      const userData = await userService.getUser(username);
      const userTweets = await tweetService.getUserTweets(username);
      
      setUser(userData);
      setTweets(userTweets);

      // Verificar si ya lo estamos siguiendo
      if (!isOwnProfile) {
        const following = await userService.isFollowing(username);
        setIsFollowing(following);
      }
    } catch (error) {
      console.error('Error loading profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFollow = async () => {
    if (followLoading) return;
    
    setFollowLoading(true);
    try {
      if (isFollowing) {
        await userService.unfollowUser(username);
        setIsFollowing(false);
      } else {
        await userService.followUser(username);
        setIsFollowing(true);
      }
      loadProfile();
    } catch (error) {
      console.error('Error toggling follow:', error);
    } finally {
      setFollowLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-twitter-blue"></div>
      </div>
    );
  }

  if (!user) {
    return <div className="p-8 text-center">Usuario no encontrado</div>;
  }

  return (
    <div>
      <div className="border-b border-gray-200 p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-20 h-20 bg-twitter-blue rounded-full flex items-center justify-center text-white text-3xl font-bold">
              {user.username[0].toUpperCase()}
            </div>
            <div>
              <h2 className="text-2xl font-bold">{user.full_name || user.username}</h2>
              <p className="text-gray-500">@{user.username}</p>
            </div>
          </div>

          {!isOwnProfile && (
            <button
              onClick={handleFollow}
              disabled={followLoading}
              className={`px-6 py-2 rounded-full font-bold transition-colors disabled:opacity-50 ${
                isFollowing
                  ? 'bg-white border-2 border-red-500 text-red-500 hover:bg-red-50'
                  : 'btn-primary'
              }`}
            >
              {followLoading ? 'Cargando...' : isFollowing ? 'Dejar de seguir' : 'Seguir'}
            </button>
          )}
        </div>

        {user.bio && <p className="mt-4 text-gray-700">{user.bio}</p>}

        <div className="flex space-x-6 mt-4 text-sm">
          <div>
            <span className="font-bold">{user.following_count || 0}</span>
            <span className="text-gray-500 ml-1">Siguiendo</span>
          </div>
          <div>
            <span className="font-bold">{user.followers_count || 0}</span>
            <span className="text-gray-500 ml-1">Seguidores</span>
          </div>
        </div>
      </div>

      <div className="border-b border-gray-200 p-4">
        <h3 className="font-bold text-lg">Tweets</h3>
      </div>

      <TweetList tweets={tweets} onUpdate={loadProfile} />
    </div>
  );
};