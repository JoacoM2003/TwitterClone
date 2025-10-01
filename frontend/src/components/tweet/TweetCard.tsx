import React from 'react';
import { Tweet } from '../../types/tweet';
import { tweetService } from '../../services/tweetService';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface TweetCardProps {
  tweet: Tweet;
  onUpdate?: () => void;
  showReplyIndicator?: boolean;
}

const formatTweetContent = (content: string, navigate: any) => {
  const parts = content.split(/(\s+)/);
  
  return parts.map((part, index) => {
    if (part.startsWith('#')) {
      return (
        <span
          key={index}
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/search?q=${encodeURIComponent(part)}`);
          }}
          className="text-twitter-blue hover:underline cursor-pointer font-medium"
        >
          {part}
        </span>
      );
    }
    
    if (part.startsWith('@')) {
      const username = part.substring(1).replace(/[^a-zA-Z0-9_-]/g, '');
      return (
        <span
          key={index}
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/profile/${username}`);
          }}
          className="text-twitter-blue hover:underline cursor-pointer font-medium"
        >
          {part}
        </span>
      );
    }
    
    return <span key={index}>{part}</span>;
  });
};

export const TweetCard: React.FC<TweetCardProps> = ({ tweet, onUpdate, showReplyIndicator = false }) => {
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  const [isLiked, setIsLiked] = React.useState(tweet.is_liked_by_user);
  const [likesCount, setLikesCount] = React.useState(tweet.likes_count);
  const [isRetweeted, setIsRetweeted] = React.useState(tweet.is_retweeted_by_user);
  const [retweetsCount, setRetweetsCount] = React.useState(tweet.retweets_count);
  const [retweetLoading, setRetweetLoading] = React.useState(false);
  const [retweetMessage, setRetweetMessage] = React.useState<string | null>(null);
  const [showMenu, setShowMenu] = React.useState(false);
  const [deleteLoading, setDeleteLoading] = React.useState(false);

  const isOwnTweet = currentUser?.id === tweet.author_id;

  const handleLike = async (e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      if (isLiked) {
        await tweetService.unlikeTweet(tweet.id);
        setLikesCount(likesCount - 1);
      } else {
        await tweetService.likeTweet(tweet.id);
        setLikesCount(likesCount + 1);
      }
      setIsLiked(!isLiked);
    } catch (error) {
      console.error('Error toggling like:', error);
    }
  };

  const handleRetweet = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setRetweetLoading(true);
    setRetweetMessage(null);
    try {
      if (isRetweeted) {
        await tweetService.unretweet(tweet.id);
        setRetweetsCount(retweetsCount - 1);
        setRetweetMessage('Retweet eliminado');
      } else {
        await tweetService.retweet(tweet.id);
        setRetweetsCount(retweetsCount + 1);
        setRetweetMessage('Retweeteado');
      }
      setIsRetweeted(!isRetweeted);
      if (onUpdate) onUpdate();
    } catch (error) {
      setRetweetMessage('Error al retweetear');
      console.error('Error toggling retweet:', error);
    } finally {
      setRetweetLoading(false);
      setTimeout(() => setRetweetMessage(null), 2000);
    }
  };

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (!window.confirm('¿Estás seguro de que quieres eliminar este tweet?')) {
      return;
    }

    setDeleteLoading(true);
    try {
      await tweetService.deleteTweet(tweet.id);
      if (onUpdate) onUpdate();
    } catch (error) {
      console.error('Error deleting tweet:', error);
      alert('Error al eliminar el tweet');
    } finally {
      setDeleteLoading(false);
      setShowMenu(false);
    }
  };

  const handleCardClick = () => {
    navigate(`/tweet/${tweet.id}`);
  };

  return (
    <div
      onClick={handleCardClick}
      className="border-b border-gray-200 p-4 hover:bg-gray-50 cursor-pointer transition-colors relative"
    >
      {showReplyIndicator && tweet.reply_to && (
        <p className="text-sm text-gray-500 mb-2 ml-14">
          💬 Respondiendo a @{tweet.reply_to.author.username}
        </p>
      )}

      <div className="flex space-x-3">
        <div className="flex-shrink-0">
          <div className="w-12 h-12 bg-twitter-blue rounded-full flex items-center justify-center text-white font-bold">
            {tweet.author.username[0].toUpperCase()}
          </div>
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span
                className="font-bold hover:underline"
                onClick={(e) => {
                  e.stopPropagation();
                  navigate(`/profile/${tweet.author.username}`);
                }}
              >
                {tweet.author.full_name || tweet.author.username}
              </span>
              <span className="text-gray-500">@{tweet.author.username}</span>
              <span className="text-gray-500">·</span>
              <span className="text-gray-500 text-sm">
                {new Date(tweet.created_at).toLocaleDateString('es-ES', {
                  day: 'numeric',
                  month: 'short'
                })}
              </span>
            </div>

            {/* Menú de opciones (solo si es tu tweet) */}
            {isOwnTweet && (
              <div className="relative">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowMenu(!showMenu);
                  }}
                  className="text-gray-500 hover:text-twitter-blue p-2 hover:bg-blue-50 rounded-full"
                >
                  ⋯
                </button>

                {showMenu && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
                    <button
                      onClick={handleDelete}
                      disabled={deleteLoading}
                      className="w-full text-left px-4 py-3 hover:bg-gray-50 text-red-600 font-bold flex items-center space-x-2 disabled:opacity-50"
                    >
                      <span>🗑️</span>
                      <span>{deleteLoading ? 'Eliminando...' : 'Eliminar'}</span>
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>

          <p className="mt-2 text-gray-900 whitespace-pre-wrap">
            {formatTweetContent(tweet.content, navigate)}
          </p>

          <div className="flex items-center space-x-8 mt-3 text-gray-500">
            <button
              onClick={(e) => {
                e.stopPropagation();
                navigate(`/tweet/${tweet.id}`);
              }}
              className="flex items-center space-x-2 hover:text-twitter-blue transition-colors"
            >
              <span>💬</span>
              <span>{tweet.replies_count}</span>
            </button>

            <div className="relative">
              <button
                onClick={handleRetweet}
                disabled={retweetLoading}
                className={`flex items-center space-x-2 transition-colors ${
                  isRetweeted ? 'text-green-500' : 'hover:text-green-500'
                } ${retweetLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {retweetLoading ? (
                  <span className="animate-spin h-5 w-5 border-b-2 border-green-500 rounded-full"></span>
                ) : (
                  <span>🔄</span>
                )}
                <span>{retweetsCount}</span>
              </button>
              {retweetMessage && (
                <span className="absolute left-0 top-8 bg-green-600 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                  {retweetMessage}
                </span>
              )}
            </div>

            <button
              onClick={handleLike}
              className={`flex items-center space-x-2 transition-colors ${
                isLiked ? 'text-red-500' : 'hover:text-red-500'
              }`}
            >
              <span>{isLiked ? '❤️' : '🤍'}</span>
              <span>{likesCount}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};