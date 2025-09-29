from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
from datetime import datetime

router = APIRouter()

@router.websocket("/test")
async def websocket_test(websocket: WebSocket):
    """WebSocket de prueba sin autenticación"""
    print("Attempting to accept connection...")
    await websocket.accept()
    print("Connection accepted!")
    
    try:
        await websocket.send_json({
            "type": "connection",
            "message": "Connected successfully!",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        while True:
            data = await websocket.receive_text()
            print(f"Received: {data}")
            await websocket.send_json({
                "type": "echo",
                "message": f"Echo: {data}",
                "timestamp": datetime.utcnow().isoformat()
            })
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")

@router.websocket("/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """WebSocket con autenticación"""
    print(f"Token received: {token[:20] if token else 'None'}...")
    
    try:
        await websocket.accept()
        print("WebSocket accepted")
    except Exception as e:
        print(f"Error accepting connection: {e}")
        return
    
    # Validación del token
    if not token:
        print("No token provided")
        await websocket.send_json({"type": "error", "message": "Token missing"})
        await websocket.close(code=1008)
        return
    
    # Importar aquí para evitar problemas circulares
    from jose import jwt, JWTError
    from app.core.config import settings
    from app.db.session import SessionLocal
    from app.services.user import user_service
    from app.core.websocket_manager import manager
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        print(f"Token decoded, username: {username}")
        
        if username is None:
            await websocket.send_json({"type": "error", "message": "Invalid token"})
            await websocket.close(code=1008)
            return
    except JWTError as e:
        print(f"JWT Error: {e}")
        await websocket.send_json({"type": "error", "message": f"Token error: {str(e)}"})
        await websocket.close(code=1008)
        return
    
    # Obtener usuario
    db = SessionLocal()
    try:
        user = user_service.get_by_username(db, username=username)
        print(f"User found: {user.username if user else 'None'}")
    except Exception as e:
        print(f"Error getting user: {e}")
        await websocket.send_json({"type": "error", "message": f"Database error: {str(e)}"})
        await websocket.close(code=1008)
        return
    finally:
        db.close()
    
    if user is None:
        await websocket.send_json({"type": "error", "message": "User not found"})
        await websocket.close(code=1008)
        return
    
    # Registrar conexión
    if user.id not in manager.active_connections:
        manager.active_connections[user.id] = []
    manager.active_connections[user.id].append(websocket)
    
    print(f"✅ User {user.username} ({user.id}) connected successfully")
    
    try:
        # Enviar bienvenida
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to notifications",
            "user_id": user.id,
            "username": user.username
        })
        
        # Loop principal
        while True:
            data = await websocket.receive_text()
            print(f"Received from {user.username}: {data}")
            
            if data == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user.id)
        print(f"User {user.username} disconnected")
    except Exception as e:
        print(f"WebSocket error for {user.username}: {e}")
        manager.disconnect(websocket, user.id)

@router.get("/connected-users")
async def get_connected_users():
    from app.core.websocket_manager import manager
    return {
        "connected_users": manager.get_connected_users(),
        "total": len(manager.get_connected_users())
    }