import React from 'react';
import { Tweet } from '../../types/tweet';
import { tweetService } from '../../services/tweetService';
import { useNavigate } from 'react-router-dom';

interface TweetCardProps {
  tweet: Tweet;
  onUpdate?: () => void;
  showReplyIndicator?: boolean;
}

// Función helper para formatear contenido con hashtags y menciones clickeables
const formatTweetContent = (content: string, navigate: any) => {
  const parts = content.split(/(\s+)/);
  
  return parts.map((part, index) => {
    // Hashtags
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
    
    // Menciones
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
    
    // Texto normal
    return <span key={index}>{part}</span>;
  });
};

export const TweetCard: React.FC<TweetCardProps> = ({ tweet, onUpdate, showReplyIndicator = false }) => {
  const navigate = useNavigate();
  const [isLiked, setIsLiked] = React.useState(tweet.is_liked_by_user);
  const [likesCount, setLikesCount] = React.useState(tweet.likes_count);
  const [isRetweeted, setIsRetweeted] = React.useState(tweet.is_retweeted_by_user);
  const [retweetsCount, setRetweetsCount] = React.useState(tweet.retweets_count);
  const [retweetLoading, setRetweetLoading] = React.useState(false);
  const [retweetMessage, setRetweetMessage] = React.useState<string | null>(null);

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

  const handleCardClick = () => {
    navigate(`/tweet/${tweet.id}`);
  };

  return (
    <div
      onClick={handleCardClick}
      className="border-b border-gray-200 p-4 hover:bg-gray-50 cursor-pointer transition-colors"
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

          {/* Contenido del tweet con hashtags y menciones clickeables */}
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