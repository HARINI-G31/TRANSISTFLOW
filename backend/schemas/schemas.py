from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    role: str

class UserCreate(UserBase):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class RouteSchema(BaseModel):
    id: int
    name: str
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    base_occupancy: float
    available_buses: int
    current_headway: int

    class Config:
        from_attributes = True

class SimulationParams(BaseModel):
    weather: str = "clear"
    event_flag: bool = False
    peak_hour: bool = False

class PredictionResponse(BaseModel):
    route_id: int
    predicted_occupancy: float
    surge_probability: float
    status: str
