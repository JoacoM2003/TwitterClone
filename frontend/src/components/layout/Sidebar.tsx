import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

export const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();

  const menuItems = [
    { name: 'Inicio', path: '/', icon: '🏠' },
    { name: 'Mensajes', path: '/messages', icon: '✉️' }, // NUEVO
    { name: 'Perfil', path: `/profile/${user?.username}`, icon: '👤' },
  ];

  return (
    <div className="w-64 border-r border-gray-200 h-screen sticky top-0 p-4">
      <div className="space-y-2">
        {menuItems.map((item) => (
          <button
            key={item.path}
            onClick={() => navigate(item.path)}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-full transition-colors ${
              location.pathname === item.path
                ? 'bg-twitter-blue text-white'
                : 'hover:bg-gray-100'
            }`}
          >
            <span className="text-2xl">{item.icon}</span>
            <span className="font-medium">{item.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
};