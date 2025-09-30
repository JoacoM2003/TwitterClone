import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Layout } from '../components/layout/Layout';
import { TweetForm } from '../components/tweet/TweetForm';
import { tweetService } from '../services/tweetService';
import { Tweet } from '../types/tweet';

export const TweetDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [tweet, setTweet] = useState<Tweet | null>(null);
  const [replies, setReplies] = useState<Tweet[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTweet();
  }, [id]);

  const loadTweet = async () => {
    if (!id) return;
    
    setLoading(true);
    try {
      const [tweetData, repliesData] = await Promise.all([
        tweetService.getTweet(Number(id)),
        tweetService.getReplies(Number(id)),
      ]);
      setTweet(tweetData);
      setReplies(repliesData);
    } catch (error) {
      console.error('Error loading tweet:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async (tweetId: number, isLiked: boolean) => {
    try {
      if (isLiked) {
        await tweetService.unlikeTweet(tweetId);
      } else {
        await tweetService.likeTweet(tweetId);
      }
      loadTweet();
    } catch (error) {
      console.error('Error toggling like:', error);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-twitter-blue"></div>
        </div>
      </Layout>
    );
  }

  if (!tweet) {
    return (
      <Layout>
        <div className="p-8 text-center">Tweet no encontrado</div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div>
        {/* Header con botón de volver */}
        <div className="border-b border-gray-200 p-4 flex items-center space-x-4">
          <button
            onClick={() => navigate(-1)}
            className="text-xl hover:bg-gray-100 p-2 rounded-full"
          >
            ←
          </button>
          <h2 className="font-bold text-xl">Tweet</h2>
        </div>

        {/* Tweet original si es una respuesta */}
        {tweet.reply_to && (
          <div
            className="border-b border-gray-200 p-4 bg-gray-50 cursor-pointer hover:bg-gray-100"
            onClick={() => navigate(`/tweet/${tweet.reply_to?.id}`)}
          >
            <div className="flex space-x-3">
              <div className="w-10 h-10 bg-gray-400 rounded-full flex items-center justify-center text-white font-bold">
                {tweet.reply_to.author.username[0].toUpperCase()}
              </div>
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <span className="font-bold">{tweet.reply_to.author.full_name || tweet.reply_to.author.username}</span>
                  <span className="text-gray-500">@{tweet.reply_to.author.username}</span>
                </div>
                <p className="text-gray-700 mt-1">{tweet.reply_to.content}</p>
              </div>
            </div>
          </div>
        )}

        {/* Tweet principal */}
        <div className="border-b border-gray-200 p-4">
          <div className="flex items-start space-x-3">
            <div className="w-12 h-12 bg-twitter-blue rounded-full flex items-center justify-center text-white font-bold text-xl">
              {tweet.author.username[0].toUpperCase()}
            </div>
            <div className="flex-1">
              <div
                className="cursor-pointer hover:underline"
                onClick={() => navigate(`/profile/${tweet.author.username}`)}
              >
                <p className="font-bold">{tweet.author.full_name || tweet.author.username}</p>
                <p className="text-gray-500">@{tweet.author.username}</p>
              </div>
            </div>
          </div>

          <p className="text-xl mt-4 whitespace-pre-wrap">{tweet.content}</p>

          <p className="text-gray-500 text-sm mt-4">
            {new Date(tweet.created_at).toLocaleString('es-ES', {
              hour: '2-digit',
              minute: '2-digit',
              day: 'numeric',
              month: 'long',
              year: 'numeric'
            })}
          </p>

          <div className="flex items-center space-x-8 mt-4 pt-4 border-t border-gray-200">
            <div className="flex items-center space-x-2">
              <span className="font-bold">{tweet.replies_count}</span>
              <span className="text-gray-500">Respuestas</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="font-bold">{tweet.likes_count}</span>
              <span className="text-gray-500">Me gusta</span>
            </div>
          </div>

          <div className="flex items-center justify-around mt-4 pt-4 border-t border-gray-200">
            <button className="flex items-center space-x-2 text-gray-500 hover:text-twitter-blue transition-colors p-2">
              <span className="text-xl">💬</span>
            </button>
            <button className="flex items-center space-x-2 text-gray-500 hover:text-green-500 transition-colors p-2">
              <span className="text-xl">🔄</span>
            </button>
            <button
              onClick={() => handleLike(tweet.id, tweet.is_liked_by_user)}
              className={`flex items-center space-x-2 transition-colors p-2 ${
                tweet.is_liked_by_user ? 'text-red-500' : 'text-gray-500 hover:text-red-500'
              }`}
            >
              <span className="text-xl">{tweet.is_liked_by_user ? '❤️' : '🤍'}</span>
            </button>
          </div>
        </div>

        {/* Formulario para responder */}
        <TweetForm replyToId={tweet.id} onTweetCreated={loadTweet} />

        {/* Respuestas */}
        <div>
          {replies.length > 0 ? (
            replies.map((reply) => (
              <div
                key={reply.id}
                className="border-b border-gray-200 p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => navigate(`/tweet/${reply.id}`)}
              >
                <div className="flex space-x-3">
                  <div className="w-10 h-10 bg-twitter-blue rounded-full flex items-center justify-center text-white font-bold">
                    {reply.author.username[0].toUpperCase()}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold">{reply.author.full_name || reply.author.username}</span>
                      <span className="text-gray-500">@{reply.author.username}</span>
                      <span className="text-gray-500">·</span>
                      <span className="text-gray-500 text-sm">
                        {new Date(reply.created_at).toLocaleDateString('es-ES')}
                      </span>
                    </div>
                    <p className="mt-1 text-gray-900">{reply.content}</p>
                    
                    <div className="flex items-center space-x-6 mt-2 text-gray-500 text-sm">
                      <span>💬 {reply.replies_count}</span>
                      <span>🤍 {reply.likes_count}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="p-8 text-center text-gray-500">
              No hay respuestas aún. ¡Sé el primero en responder!
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};