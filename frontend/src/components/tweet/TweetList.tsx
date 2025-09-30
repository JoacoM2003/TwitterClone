import React from 'react';
import { Tweet } from '../../types/tweet';
import { TweetCard } from './TweetCard';

interface TweetListProps {
  tweets: Tweet[];
  loading?: boolean;
  onUpdate?: () => void;
}

export const TweetList: React.FC<TweetListProps> = ({ tweets, loading, onUpdate }) => {
  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-twitter-blue"></div>
      </div>
    );
  }

  if (tweets.length === 0) {
    return (
      <div className="text-center p-8 text-gray-500">
        No hay tweets para mostrar
      </div>
    );
  }

  return (
    <div>
      {tweets.map((tweet) => (
        <TweetCard key={tweet.id} tweet={tweet} onUpdate={onUpdate} />
      ))}
    </div>
  );
};