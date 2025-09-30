import React, { createContext, useState, useEffect, useContext } from 'react';
import { User } from '../types/user';
import { authService } from '../services/authService';
import { websocketService } from '../services/websocketService';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const currentUser = await authService.getCurrentUser();
          setUser(currentUser);
          
          // Conectar WebSocket
          websocketService.connect(token);
        } catch (error) {
          console.error('Error loading user:', error);
          localStorage.removeItem('token');
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (username: string, password: string) => {
    await authService.login({ username, password });
    const currentUser = await authService.getCurrentUser();
    setUser(currentUser);
    
    // Conectar WebSocket
    const token = localStorage.getItem('token');
    if (token) {
      websocketService.connect(token);
    }
  };

  const register = async (username: string, email: string, password: string, fullName?: string) => {
    await authService.register({ username, email, password, full_name: fullName });
    await login(username, password);
  };

  const logout = () => {
    authService.logout();
    websocketService.disconnect();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};