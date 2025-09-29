from typing import Dict, List
from fastapi import WebSocket
from collections import defaultdict

class ConnectionManager:
    def __init__(self):
        # user_id -> List[WebSocket]
        self.active_connections: Dict[int, List[WebSocket]] = defaultdict(list)
        
    async def connect(self, websocket: WebSocket, user_id: int):
        """Conectar un websocket para un usuario"""
        await websocket.accept()
        self.active_connections[user_id].append(websocket)  # ✅ CORREGIDO
        print(f"User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Desconectar un websocket"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            # Limpiar si no hay más conexiones
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        print(f"User {user_id} disconnected")
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Enviar mensaje a un usuario específico (todas sus conexiones)"""
        if user_id in self.active_connections:
            dead_connections = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error sending to user {user_id}: {e}")
                    dead_connections.append(connection)
            
            # Limpiar conexiones muertas
            for conn in dead_connections:
                self.disconnect(conn, user_id)
    
    async def send_to_users(self, message: dict, user_ids: List[int]):
        """Enviar mensaje a múltiples usuarios"""
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)
    
    async def broadcast(self, message: dict):
        """Enviar mensaje a todos los usuarios conectados"""
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, user_id)
    
    def get_connected_users(self) -> List[int]:
        """Obtener lista de usuarios conectados"""
        return list(self.active_connections.keys())
    
    def is_user_connected(self, user_id: int) -> bool:
        """Verificar si un usuario está conectado"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0

# Instancia global
manager = ConnectionManager()