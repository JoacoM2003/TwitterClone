import React, { useState, useEffect } from 'react';
import { websocketService } from '../../services/websocketService';
import { Notification } from '../../types/notification';

export const NotificationPanel: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isOpen, setIsOpen] = useState(true);

  useEffect(() => {
    const unsubscribe = websocketService.subscribe((notification) => {
      if (notification.type !== 'connection') {
        setNotifications((prev) => [notification, ...prev.slice(0, 9)]);
      }
    });

    return unsubscribe;
  }, []);

  const getNotificationMessage = (notification: Notification) => {
    switch (notification.type) {
      case 'new_tweet':
        return `📝 @${notification.data?.author?.username} publicó un tweet`;
      case 'new_like':
        return `❤️ ${notification.data?.message}`;
      case 'new_reply':
        return `💬 ${notification.data?.message}`;
      case 'new_follower':
        return `👤 ${notification.data?.message}`;
      case 'new_message': // NUEVO
        return `✉️ Nuevo mensaje de @${notification.data?.sender_username}`;
      default:
        return notification.message || 'Nueva notificación';
    }
  };

  return (
    <div className="w-80 p-4 sticky top-0 h-screen overflow-y-auto">
      <div className="bg-white rounded-lg border border-gray-200">
        <div
          className="flex items-center justify-between p-4 border-b border-gray-200 cursor-pointer"
          onClick={() => setIsOpen(!isOpen)}
        >
          <h3 className="font-bold text-lg">Notificaciones</h3>
          {notifications.length > 0 && (
            <span className="bg-twitter-blue text-white text-xs rounded-full px-2 py-1">
              {notifications.length}
            </span>
          )}
        </div>

        {isOpen && (
          <div className="divide-y divide-gray-200">
            {notifications.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                No hay notificaciones
              </div>
            ) : (
              notifications.map((notification, index) => (
                <div
                  key={index}
                  className="p-4 hover:bg-gray-50 transition-colors"
                >
                  <p className="text-sm">{getNotificationMessage(notification)}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(notification.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};