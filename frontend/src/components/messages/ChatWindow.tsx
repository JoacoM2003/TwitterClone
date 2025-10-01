import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { messageService } from '../../services/messageService';
import { websocketService } from '../../services/websocketService';
import { Message } from '../../types/message';
import { useAuth } from '../../contexts/AuthContext';

interface ChatWindowProps {
  username: string;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ username }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user: currentUser } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    loadMessages();
    
    // Suscribirse a nuevos mensajes
    const unsubscribe = websocketService.subscribe((notification) => {
      if (notification.type === 'new_message' && 
          notification.data?.sender_username === username) {
        loadMessages();
      }
    });

    return unsubscribe;
  }, [username]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadMessages = async () => {
    try {
      const data = await messageService.getMessages(username);
      setMessages(data);
      await messageService.markAsRead(username);
    } catch (error) {
      console.error('Error loading messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim() || sending) return;

    setSending(true);
    try {
      await messageService.sendMessage({
        receiver_username: username,
        content: newMessage.trim()
      });
      setNewMessage('');
      await loadMessages();
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setSending(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-twitter-blue"></div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b border-gray-200 p-4 flex items-center space-x-3 bg-white">
        <button
          onClick={() => navigate('/messages')}
          className="text-xl hover:bg-gray-100 p-2 rounded-full"
        >
          ←
        </button>
        <div
          className="flex items-center space-x-3 flex-1 cursor-pointer"
          onClick={() => navigate(`/profile/${username}`)}
        >
          <div className="w-10 h-10 bg-twitter-blue rounded-full flex items-center justify-center text-white font-bold">
            {username[0].toUpperCase()}
          </div>
          <div>
            <p className="font-bold">@{username}</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <p className="text-4xl mb-2">💬</p>
            <p>No hay mensajes aún</p>
            <p className="text-sm mt-2">Envía el primer mensaje</p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => {
              const isOwnMessage = message.sender.username === currentUser?.username;
              
              return (
                <div
                  key={message.id}
                  className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl ${
                      isOwnMessage
                        ? 'bg-twitter-blue text-white'
                        : 'bg-white border border-gray-200'
                    }`}
                  >
                    <p className="break-words">{message.content}</p>
                    <p
                      className={`text-xs mt-1 ${
                        isOwnMessage ? 'text-blue-100' : 'text-gray-500'
                      }`}
                    >
                      {new Date(message.created_at).toLocaleTimeString('es-ES', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                </div>
              );
            })}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSend} className="border-t border-gray-200 p-4 bg-white">
        <div className="flex space-x-2">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Escribe un mensaje..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:border-twitter-blue"
            maxLength={500}
          />
          <button
            type="submit"
            disabled={!newMessage.trim() || sending}
            className="btn-primary disabled:opacity-50"
          >
            {sending ? '...' : 'Enviar'}
          </button>
        </div>
      </form>
    </div>
  );
};