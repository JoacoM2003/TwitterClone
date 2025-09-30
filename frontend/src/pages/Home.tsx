import React, { useState, useEffect } from 'react';
import { Layout } from '../components/layout/Layout';
import { TweetForm } from '../components/tweet/TweetForm';
import { TweetList } from '../components/tweet/TweetList';
import { tweetService } from '../services/tweetService';
import { Tweet } from '../types/tweet';

export const Home: React.FC = () => {
  const [tweets, setTweets] = useState<Tweet[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'feed' | 'all'>('feed');

  useEffect(() => {
    loadTweets();
  }, [activeTab]);

  const loadTweets = async () => {
    setLoading(true);
    try {
      const data =
        activeTab === 'feed'
          ? await tweetService.getFeed()
          : await tweetService.getPublicTweets();
      setTweets(data);
    } catch (error) {
      console.error('Error loading tweets:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div>
        <div className="border-b border-gray-200">
          <div className="flex">
            <button
              onClick={() => setActiveTab('feed')}
              className={`flex-1 py-4 font-medium transition-colors ${
                activeTab === 'feed'
                  ? 'border-b-2 border-twitter-blue text-twitter-blue'
                  : 'text-gray-500 hover:bg-gray-50'
              }`}
            >
              Para ti
            </button>
            <button
              onClick={() => setActiveTab('all')}
              className={`flex-1 py-4 font-medium transition-colors ${
                activeTab === 'all'
                  ? 'border-b-2 border-twitter-blue text-twitter-blue'
                  : 'text-gray-500 hover:bg-gray-50'
              }`}
            >
              Todos
            </button>
          </div>
        </div>

        <TweetForm onTweetCreated={loadTweets} />
        <TweetList tweets={tweets} loading={loading} onUpdate={loadTweets} />
      </div>
    </Layout>
  );
};