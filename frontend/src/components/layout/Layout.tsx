import React from 'react';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';
import { NotificationPanel } from '../notifications/NotificationPanel';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-7xl mx-auto flex">
        <Sidebar />
        <main className="flex-1 border-r border-gray-200 bg-white">
          {children}
        </main>
        <NotificationPanel />
      </div>
    </div>
  );
};