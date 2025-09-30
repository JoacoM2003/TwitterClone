import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { trendingService, TrendingHashtag } from '../../services/trendingService';

export const TrendingPanel: React.FC = () => {
  const [trending, setTrending] = useState<TrendingHashtag[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadTrending();
  }, []);

  const loadTrending = async () => {
    try {
      const data = await trendingService.getTrendingHashtags();
      setTrending(data);
    } catch (error) {
      console.error('Error loading trending:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 mb-4">
      <div className="p-4 border-b border-gray-200">
        <h3 className="font-bold text-lg">Tendencias</h3>
      </div>

      {loading ? (
        <div className="p-4 text-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-twitter-blue mx-auto"></div>
        </div>
      ) : trending.length > 0 ? (
        <div>
          {trending.map((item, index) => (
            <div
              key={item.tag}
              onClick={() => navigate(`/search?q=${encodeURIComponent('#' + item.tag)}`)}
              className="p-4 hover:bg-gray-50 cursor-pointer transition-colors border-b border-gray-200 last:border-b-0"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <p className="text-sm text-gray-500">#{index + 1} · Tendencia</p>
                  <p className="font-bold text-lg">#{item.tag}</p>
                  <p className="text-sm text-gray-500">{item.tweets_count} tweets</p>
                </div>
                <span className="text-2xl">📈</span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-4 text-center text-gray-500">
          No hay tendencias disponibles
        </div>
      )}
    </div>
  );
};