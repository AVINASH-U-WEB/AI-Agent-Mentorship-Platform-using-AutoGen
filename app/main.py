import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.core.config import settings
from app.db.database import engine, Base
from app.api.v1 import mentorship, users
from app.api.websockets import manager

app = FastAPI(title=settings.PROJECT_NAME)

@app.on_event("startup")
async def startup():
    """Initializes the database and creates tables on application startup."""
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Use cautiously for development
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("shutdown")
async def shutdown():
    """Disposes of the database engine connection on application shutdown."""
    await engine.dispose()

# Include API routers
app.include_router(users.router, prefix="/api/v1", tags=["Users"])
app.include_router(mentorship.router, prefix="/api/v1", tags=["Mentorship"])

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """Handles WebSocket connections for real-time session communication."""
    await manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Session {session_id} says: {data}", session_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
        await manager.broadcast(f"A user has left session {session_id}", session_id)

@app.get("/")
async def root():
    """Root endpoint for the API."""
    return {"message": "Skill-Exchange Mentor Network API is running."}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)