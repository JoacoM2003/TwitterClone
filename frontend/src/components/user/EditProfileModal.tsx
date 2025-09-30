import React, { useState } from 'react';
import { User } from '../../types/user';
import { userService } from '../../services/userService';

interface EditProfileModalProps {
  user: User;
  isOpen: boolean;
  onClose: () => void;
  onUpdate: () => void;
}

export const EditProfileModal: React.FC<EditProfileModalProps> = ({
  user,
  isOpen,
  onClose,
  onUpdate,
}) => {
  const [formData, setFormData] = useState({
    full_name: user.full_name || '',
    bio: user.bio || '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await userService.updateProfile(formData);
      onUpdate();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al actualizar perfil');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg max-w-lg w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 sticky top-0 bg-white">
          <div className="flex items-center space-x-4">
            <button
              onClick={onClose}
              className="text-xl hover:bg-gray-100 p-2 rounded-full"
            >
              ✕
            </button>
            <h2 className="font-bold text-xl">Editar perfil</h2>
          </div>
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="btn-primary disabled:opacity-50"
          >
            {loading ? 'Guardando...' : 'Guardar'}
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="mx-4 mt-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {/* Avatar placeholder */}
          <div className="relative">
            <div className="h-32 bg-gradient-to-r from-twitter-blue to-blue-400 rounded-t-lg"></div>
            <div className="absolute -bottom-12 left-4">
              <div className="w-24 h-24 bg-twitter-blue rounded-full flex items-center justify-center text-white text-3xl font-bold border-4 border-white">
                {user.username[0].toUpperCase()}
              </div>
            </div>
          </div>

          <div className="pt-12 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nombre
              </label>
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) =>
                  setFormData({ ...formData, full_name: e.target.value })
                }
                className="input-field"
                maxLength={50}
              />
              <p className="text-xs text-gray-500 mt-1">
                {formData.full_name.length}/50
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Biografía
              </label>
              <textarea
                value={formData.bio}
                onChange={(e) =>
                  setFormData({ ...formData, bio: e.target.value })
                }
                className="input-field resize-none"
                rows={4}
                maxLength={160}
                placeholder="Cuéntanos sobre ti..."
              />
              <p className="text-xs text-gray-500 mt-1">
                {formData.bio.length}/160
              </p>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};