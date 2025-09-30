import React, { useState } from 'react';
import { tweetService } from '../../services/tweetService';

interface TweetFormProps {
  replyToId?: number;
  onTweetCreated?: () => void;
}

export const TweetForm: React.FC<TweetFormProps> = ({ replyToId, onTweetCreated }) => {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;

    setLoading(true);
    try {
      await tweetService.createTweet({
        content,
        reply_to_id: replyToId,
      });
      setContent('');
      onTweetCreated?.();
    } catch (error) {
      console.error('Error creating tweet:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-b border-gray-200 p-4">
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder={replyToId ? "Escribe tu respuesta..." : "¿Qué está pasando?"}
        className="w-full p-2 text-lg resize-none focus:outline-none"
        rows={3}
        maxLength={280}
      />
      
      <div className="flex justify-between items-center mt-2">
        <span className="text-sm text-gray-500">{content.length}/280</span>
        <button
          type="submit"
          disabled={loading || !content.trim()}
          className="btn-primary disabled:opacity-50"
        >
          {loading ? 'Publicando...' : replyToId ? 'Responder' : 'Twittear'}
        </button>
      </div>
    </form>
  );
};