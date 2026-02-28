from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import asyncio

from database import engine, Base, get_db
from models.models import Route, TripUpdate, User
from api.v1 import auth
from ml_module.predictor import predictor
from ml_module.optimizer import optimizer
from schemas.schemas import SimulationParams

# Initialize Database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TransitFlow AI")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connection Manager for WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# ----------------- Healthcheck -----------------
@app.get("/health")
async def health_check():
    """Simple health check for Docker"""
    return {"status": "healthy"}

# ----------------- Seed Data -----------------
@app.on_event("startup")
def seed_data():
    db = next(get_db())
    if db.query(Route).count() == 0:
        routes = [
            Route(
                name="Blue Express - Downtown",
                start_lat=40.7128, start_lng=-74.0060,
                end_lat=40.7580, end_lng=-73.9855,
                base_occupancy=0.4
            ),
            Route(
                name="Green Line - Uptown",
                start_lat=40.7831, start_lng=-73.9712,
                end_lat=40.8448, end_lng=-73.9352,
                base_occupancy=0.3
            ),
            Route(
                name="Red Shuttle - Tech Hub",
                start_lat=40.6782, start_lng=-73.9442,
                end_lat=40.6892, end_lng=-74.0445,
                base_occupancy=0.6
            ),
        ]
        db.add_all(routes)
        db.commit()

# ----------------- WebSocket -----------------
@app.websocket("/ws/updates")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ----------------- Simulation Endpoint -----------------
@app.post("/api/v1/simulation/tick")
async def run_simulation_step(params: SimulationParams, db: Session = Depends(get_db)):
    """Runs a single simulation tick and broadcasts results"""
    routes = db.query(Route).all()
    updates = []
    fleet_data = []

    for r in routes:
        # 1. Predict
        pred = predictor.predict(r.id, r.base_occupancy, params.weather, params.event_flag, params.peak_hour)

        # Save Update
        new_update = TripUpdate(
            route_id=r.id,
            predicted_load=pred["predicted_occupancy"],
            actual_load=pred["predicted_occupancy"],  # Simulated actual
            surge_risk=pred["surge_probability"],
            status=pred["status"]
        )
        db.add(new_update)

        updates.append({
            "route_id": r.id,
            "name": r.name,
            **pred
        })

        fleet_data.append({
            "id": r.id,
            "current_load": pred["predicted_occupancy"],
            "buses_available": getattr(r, "available_buses", 0),
            "headway": getattr(r, "current_headway", 0)
        })

    # 2. Optimize
    optimizations = optimizer.optimize(fleet_data)

    db.commit()

    final_payload = {
        "timestamp": str(asyncio.get_event_loop().time()),
        "updates": updates,
        "optimizations": optimizations
    }

    # Broadcast to WebSocket clients
    await manager.broadcast(final_payload)
    return final_payload

# ----------------- Routes -----------------
@app.get("/api/v1/routes")
def get_routes(db: Session = Depends(get_db)):
    return db.query(Route).all()

# ----------------- Auth Router -----------------
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])

# ----------------- Run Uvicorn -----------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)