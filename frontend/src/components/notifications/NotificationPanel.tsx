import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { websocketService } from '../../services/websocketService';
import { notificationService } from '../../services/notificationService';
import { Notification } from '../../types/notification';

export const NotificationPanel: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(true);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadNotifications();
    loadUnreadCount();

    // Suscribirse a notificaciones en tiempo real
    const unsubscribe = websocketService.subscribe((notification) => {
      if (notification.type !== 'connection') {
        // Agregar al principio de la lista
        setNotifications((prev) => [notification, ...prev]);
        setUnreadCount((prev) => prev + 1);
      }
    });

    return unsubscribe;
  }, []);

  const loadNotifications = async () => {
    try {
      const data = await notificationService.getNotifications(0, 20);
      setNotifications(data);
    } catch (error) {
      console.error('Error loading notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUnreadCount = async () => {
    try {
      const count = await notificationService.getUnreadCount();
      setUnreadCount(count);
    } catch (error) {
      console.error('Error loading unread count:', error);
    }
  };

  const handleNotificationClick = async (notification: Notification) => {
    // Marcar como leída si tiene ID
    if (notification.id) {
      try {
        await notificationService.markAsRead(notification.id);
        setNotifications((prev) =>
          prev.map((n) => (n.id === notification.id ? { ...n, is_read: true } : n))
        );
        setUnreadCount((prev) => Math.max(0, prev - 1));
      } catch (error) {
        console.error('Error marking as read:', error);
      }
    }

    // Navegar según el tipo
    switch (notification.type) {
      case 'new_like':
      case 'new_reply':
      case 'new_retweet':
        if (notification.related_id) {
          navigate(`/tweet/${notification.related_id}`);
        }
        break;
      case 'new_follower':
        if (notification.related_username) {
          navigate(`/profile/${notification.related_username}`);
        }
        break;
      case 'new_message':
        if (notification.data?.sender_username || notification.related_username) {
          navigate(`/messages/${notification.data?.sender_username || notification.related_username}`);
        }
        break;
      case 'new_tweet':
        if (notification.data?.author?.username) {
          navigate(`/profile/${notification.data.author.username}`);
        }
        break;
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await notificationService.markAllAsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (error) {
      console.error('Error marking all as read:', error);
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'new_like':
        return '❤️';
      case 'new_reply':
        return '💬';
      case 'new_retweet':
        return '🔄';
      case 'new_follower':
        return '👤';
      case 'new_message':
        return '✉️';
      case 'new_tweet':
        return '📝';
      default:
        return '🔔';
    }
  };

  const getNotificationMessage = (notification: Notification) => {
    // Si tiene mensaje directo, usarlo
    if (notification.message) {
      return notification.message;
    }

    // Fallback para notificaciones WebSocket sin persistencia
    switch (notification.type) {
      case 'new_tweet':
        return `@${notification.data?.author?.username} publicó un tweet`;
      case 'new_like':
        return notification.data?.message || 'Le gustó tu tweet';
      case 'new_reply':
        return notification.data?.message || 'Respondió a tu tweet';
      case 'new_follower':
        return notification.data?.message || 'Empezó a seguirte';
      case 'new_message':
        return `Nuevo mensaje de @${notification.data?.sender_username}`;
      case 'new_retweet':
        return notification.data?.message || 'Retweeteó tu tweet';
      default:
        return 'Nueva notificación';
    }
  };

  return (
    <div className="w-80 p-4 sticky top-0 h-screen overflow-y-auto">
      <div className="bg-white rounded-lg border border-gray-200">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <h3 className="font-bold text-lg">Notificaciones</h3>
            {unreadCount > 0 && (
              <span className="bg-twitter-blue text-white text-xs rounded-full px-2 py-1">
                {unreadCount}
              </span>
            )}
          </div>
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="text-gray-500 hover:text-gray-700"
          >
            {isOpen ? '▼' : '▶'}
          </button>
        </div>

        {isOpen && (
          <>
            {/* Botón marcar todas como leídas */}
            {unreadCount > 0 && (
              <div className="p-2 border-b border-gray-200">
                <button
                  onClick={handleMarkAllAsRead}
                  className="w-full text-center text-sm text-twitter-blue hover:bg-blue-50 py-2 rounded"
                >
                  Marcar todas como leídas
                </button>
              </div>
            )}

            {/* Lista de notificaciones */}
            <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
              {loading ? (
                <div className="p-4 text-center">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-twitter-blue mx-auto"></div>
                </div>
              ) : notifications.length === 0 ? (
                <div className="p-4 text-center text-gray-500">
                  No hay notificaciones
                </div>
              ) : (
                notifications.map((notification, index) => (
                  <div
                    key={notification.id || index}
                    onClick={() => handleNotificationClick(notification)}
                    className={`p-4 hover:bg-gray-50 transition-colors cursor-pointer ${
                      !notification.is_read ? 'bg-blue-50' : ''
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <span className="text-2xl flex-shrink-0">
                        {getNotificationIcon(notification.type)}
                      </span>
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm ${!notification.is_read ? 'font-medium' : ''}`}>
                          {getNotificationMessage(notification)}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {notification.created_at
                            ? new Date(notification.created_at).toLocaleDateString('es-ES', {
                                day: 'numeric',
                                month: 'short',
                                hour: '2-digit',
                                minute: '2-digit',
                              })
                            : new Date(notification.timestamp).toLocaleTimeString('es-ES', {
                                hour: '2-digit',
                                minute: '2-digit',
                              })}
                        </p>
                      </div>
                      {!notification.is_read && (
                        <div className="w-2 h-2 bg-twitter-blue rounded-full flex-shrink-0 mt-1"></div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};