import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-white border-b border-gray-200 px-4 py-3">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <h1
          onClick={() => navigate('/')}
          className="text-2xl font-bold text-twitter-blue cursor-pointer"
        >
          🐦 Twitter Clone
        </h1>

        {user && (
          <div className="flex items-center space-x-4">
            <span
              onClick={() => navigate(`/profile/${user.username}`)}
              className="font-medium cursor-pointer hover:underline"
            >
              @{user.username}
            </span>
            <button onClick={handleLogout} className="btn-outline text-sm">
              Cerrar Sesión
            </button>
          </div>
        )}
      </div>
    </nav>
  );
};