import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Layout } from '../components/layout/Layout';
import { TweetList } from '../components/tweet/TweetList';
import { searchService } from '../services/searchService';
import { Tweet } from '../types/tweet';
import { UserPublic } from '../types/user';

export const Search: React.FC = () => {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  const [activeTab, setActiveTab] = useState<'tweets' | 'users' | 'hashtags'>('tweets');
  const [tweets, setTweets] = useState<Tweet[]>([]);
  const [users, setUsers] = useState<UserPublic[]>([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (query) {
      loadResults();
    }
  }, [query, activeTab]);

  const loadResults = async () => {
    setLoading(true);
    try {
      if (activeTab === 'tweets') {
        const results = await searchService.searchTweets(query);
        setTweets(results);
      } else if (activeTab === 'users') {
        const results = await searchService.searchUsers(query, 50);
        setUsers(results);
      } else if (activeTab === 'hashtags') {
        const results = await searchService.searchHashtags(query);
        setTweets(results);
      }
    } catch (error) {
      console.error('Error loading search results:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div>
        {/* Header */}
        <div className="border-b border-gray-200 p-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate(-1)}
              className="text-xl hover:bg-gray-100 p-2 rounded-full"
            >
              ←
            </button>
            <div>
              <h2 className="font-bold text-xl">Resultados de búsqueda</h2>
              <p className="text-gray-500 text-sm">"{query}"</p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 flex">
          <button
            onClick={() => setActiveTab('tweets')}
            className={`flex-1 py-4 font-medium transition-colors ${
              activeTab === 'tweets'
                ? 'border-b-2 border-twitter-blue text-twitter-blue'
                : 'text-gray-500 hover:bg-gray-50'
            }`}
          >
            Tweets
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`flex-1 py-4 font-medium transition-colors ${
              activeTab === 'users'
                ? 'border-b-2 border-twitter-blue text-twitter-blue'
                : 'text-gray-500 hover:bg-gray-50'
            }`}
          >
            Usuarios
          </button>
          <button
            onClick={() => setActiveTab('hashtags')}
            className={`flex-1 py-4 font-medium transition-colors ${
              activeTab === 'hashtags'
                ? 'border-b-2 border-twitter-blue text-twitter-blue'
                : 'text-gray-500 hover:bg-gray-50'
            }`}
          >
            Hashtags
          </button>
        </div>

        {/* Results */}
        <div>
          {loading ? (
            <div className="flex justify-center items-center p-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-twitter-blue"></div>
            </div>
          ) : activeTab === 'tweets' || activeTab === 'hashtags' ? (
            <TweetList tweets={tweets} onUpdate={loadResults} />
          ) : (
            <div>
              {users.length > 0 ? (
                users.map((user) => (
                  <div
                    key={user.id}
                    onClick={() => navigate(`/profile/${user.username}`)}
                    className="flex items-center justify-between p-4 border-b border-gray-200 hover:bg-gray-50 cursor-pointer"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 bg-twitter-blue rounded-full flex items-center justify-center text-white font-bold">
                        {user.username[0].toUpperCase()}
                      </div>
                      <div>
                        <p className="font-bold">{user.full_name || user.username}</p>
                        <p className="text-gray-500 text-sm">@{user.username}</p>
                        {user.bio && (
                          <p className="text-gray-700 text-sm mt-1">{user.bio}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-8 text-center text-gray-500">
                  No se encontraron usuarios
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};