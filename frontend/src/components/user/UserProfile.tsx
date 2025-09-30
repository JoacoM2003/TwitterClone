import React, { useState, useEffect } from 'react';
import { UserPublic } from '../../types/user';
import { Tweet } from '../../types/tweet';
import { userService } from '../../services/userService';
import { tweetService } from '../../services/tweetService';
import { TweetList } from '../tweet/TweetList';
import { useAuth } from '../../contexts/AuthContext';
import { EditProfileModal } from './EditProfileModal';

interface UserProfileProps {
  username: string;
}

export const UserProfile: React.FC<UserProfileProps> = ({ username }) => {
  const [user, setUser] = useState<UserPublic | null>(null);
  const [tweets, setTweets] = useState<Tweet[]>([]);
  const [loading, setLoading] = useState(true);
  const [isFollowing, setIsFollowing] = useState(false);
  const [followLoading, setFollowLoading] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
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
      {/* Banner y foto de perfil */}
      <div className="relative">
        <div className="h-48 bg-gradient-to-r from-twitter-blue to-blue-400"></div>
        <div className="absolute -bottom-16 left-4">
          <div className="w-32 h-32 bg-twitter-blue rounded-full flex items-center justify-center text-white text-4xl font-bold border-4 border-white">
            {user.username[0].toUpperCase()}
          </div>
        </div>
      </div>

      {/* Info del perfil */}
      <div className="border-b border-gray-200 px-4 pt-20 pb-4">
        <div className="flex justify-end mb-4">
          {isOwnProfile ? (
            <button
              onClick={() => setIsEditModalOpen(true)}
              className="btn-outline"
            >
              Editar perfil
            </button>
          ) : (
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

        <div>
          <h2 className="text-2xl font-bold">{user.full_name || user.username}</h2>
          <p className="text-gray-500">@{user.username}</p>
        </div>

        {user.bio && (
          <p className="mt-3 text-gray-700">{user.bio}</p>
        )}

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

      {/* Tweets */}
      <div className="border-b border-gray-200 p-4">
        <h3 className="font-bold text-lg">Tweets</h3>
      </div>

      <TweetList tweets={tweets} onUpdate={loadProfile} />

      {/* Modal de edición */}
      {isOwnProfile && currentUser && (
        <EditProfileModal
          user={currentUser}
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          onUpdate={loadProfile}
        />
      )}
    </div>
  );
};