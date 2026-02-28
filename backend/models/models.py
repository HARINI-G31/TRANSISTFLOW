from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String) # 'admin' or 'passenger'

class Route(Base):
    __tablename__ = "routes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    start_lat = Column(Float)
    start_lng = Column(Float)
    end_lat = Column(Float)
    end_lng = Column(Float)
    base_occupancy = Column(Float, default=0.2)
    available_buses = Column(Integer, default=5)
    current_headway = Column(Integer, default=15) # minutes

class TripUpdate(Base):
    __tablename__ = "trip_updates"
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    predicted_load = Column(Float)
    actual_load = Column(Float)
    surge_risk = Column(Float)
    status = Column(String) # Green, Yellow, Red
