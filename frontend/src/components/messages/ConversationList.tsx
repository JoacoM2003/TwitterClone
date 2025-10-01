import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { messageService } from '../../services/messageService';
import { Conversation } from '../../types/message';

export const ConversationList: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const data = await messageService.getConversations();
      setConversations(data);
    } catch (error) {
      console.error('Error loading conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-twitter-blue"></div>
      </div>
    );
  }

  if (conversations.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500">
        <p className="text-xl mb-2">📭</p>
        <p>No tienes conversaciones</p>
        <p className="text-sm mt-2">Busca un usuario y envíale un mensaje</p>
      </div>
    );
  }

  return (
    <div>
      {conversations.map((conversation) => (
        <div
          key={conversation.id}
          onClick={() => navigate(`/messages/${conversation.other_user.username}`)}
          className="flex items-center space-x-3 p-4 border-b border-gray-200 hover:bg-gray-50 cursor-pointer transition-colors"
        >
          <div className="w-12 h-12 bg-twitter-blue rounded-full flex items-center justify-center text-white font-bold flex-shrink-0">
            {conversation.other_user.username[0].toUpperCase()}
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <p className="font-bold truncate">
                {conversation.other_user.full_name || conversation.other_user.username}
              </p>
              {conversation.last_message && (
                <span className="text-xs text-gray-500">
                  {new Date(conversation.last_message.created_at).toLocaleDateString('es-ES', {
                    day: 'numeric',
                    month: 'short'
                  })}
                </span>
              )}
            </div>
            
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-500 truncate">
                @{conversation.other_user.username}
                {conversation.last_message && ` · ${conversation.last_message.content}`}
              </p>
              {conversation.unread_count > 0 && (
                <span className="bg-twitter-blue text-white text-xs px-2 py-1 rounded-full ml-2">
                  {conversation.unread_count}
                </span>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};