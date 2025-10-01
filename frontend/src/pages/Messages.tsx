import React from 'react';
import { useParams } from 'react-router-dom';
import { Layout } from '../components/layout/Layout';
import { ConversationList } from '../components/messages/ConversationList';
import { ChatWindow } from '../components/messages/ChatWindow';

export const Messages: React.FC = () => {
  const { username } = useParams<{ username?: string }>();

  return (
    <Layout>
      <div className="h-screen flex flex-col">
        {/* Header */}
        <div className="border-b border-gray-200 p-4">
          <h2 className="font-bold text-xl">Mensajes</h2>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden">
          {username ? (
            <ChatWindow username={username} />
          ) : (
            <ConversationList />
          )}
        </div>
      </div>
    </Layout>
  );
};