import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchService } from '../../services/searchService';
import { UserPublic } from '../../types/user';

export const SearchBar: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<UserPublic[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const searchRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    const searchUsers = async () => {
      if (query.trim().length < 2) {
        setResults([]);
        return;
      }

      setLoading(true);
      try {
        const users = await searchService.searchUsers(query);
        setResults(users);
        setIsOpen(true);
      } catch (error) {
        console.error('Error searching users:', error);
      } finally {
        setLoading(false);
      }
    };

    const debounce = setTimeout(searchUsers, 300);
    return () => clearTimeout(debounce);
  }, [query]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query.trim())}`);
      setIsOpen(false);
    }
  };

  return (
    <div ref={searchRef} className="relative w-full max-w-md">
      <form onSubmit={handleSubmit}>
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Buscar usuarios, tweets, #hashtags..."
            className="w-full px-4 py-2 pl-10 pr-4 rounded-full bg-gray-100 focus:bg-white focus:outline-none focus:ring-2 focus:ring-twitter-blue transition-colors"
          />
          <span className="absolute left-3 top-2.5 text-gray-500 text-xl">🔍</span>
        </div>
      </form>

      {isOpen && (
        <div className="absolute top-full mt-2 w-full bg-white rounded-lg shadow-lg border border-gray-200 max-h-96 overflow-y-auto z-50">
          {loading ? (
            <div className="p-4 text-center text-gray-500">Buscando...</div>
          ) : results.length > 0 ? (
            <div>
              <div className="px-4 py-2 bg-gray-50 border-b border-gray-200 font-semibold text-sm text-gray-600">
                Usuarios
              </div>
              {results.map((user) => (
                <div
                  key={user.id}
                  onClick={() => {
                    navigate(`/profile/${user.username}`);
                    setIsOpen(false);
                    setQuery('');
                  }}
                  className="flex items-center space-x-3 px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors"
                >
                  <div className="w-10 h-10 bg-twitter-blue rounded-full flex items-center justify-center text-white font-bold">
                    {user.username[0].toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-bold truncate">{user.full_name || user.username}</p>
                    <p className="text-sm text-gray-500 truncate">@{user.username}</p>
                  </div>
                </div>
              ))}
              {query.trim() && (
                <div
                  onClick={() => {
                    navigate(`/search?q=${encodeURIComponent(query.trim())}`);
                    setIsOpen(false);
                  }}
                  className="px-4 py-3 text-twitter-blue hover:bg-gray-50 cursor-pointer border-t border-gray-200"
                >
                  Ver todos los resultados para "{query}"
                </div>
              )}
            </div>
          ) : query.trim().length >= 2 ? (
            <div className="p-4 text-center text-gray-500">
              No se encontraron resultados
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
};