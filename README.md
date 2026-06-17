# TransitFlow AI: Predictive Public Transport Load Balancing

A high-performance full-stack solution for smart city transit optimization. Uses a simulated LSTM for demand forecasting and Linear Programming (OR-Tools) for fleet rebalancing.




## Features
- **AI Demand Prediction**: Predicts occupancy based on historical patterns, weather, and events.
- **Dispatch Optimization**: Suggests deadheading, short-turning, or headway adjustments to minimize overcrowding.
- **Real-time Engine**: WebSockets push system updates to the Admin Dashboard instantly.
- **Role-based UI**: Detailed command center for Admins and a crowd-awareness view for Passengers.
- **Containerized**: Fully Docker-ready for immediate deployment.

## Tech Stack
- **Backend**: FastAPI (Python 3.10), SQLAlchemy, PostgreSQL
- **Logic**: Google OR-Tools (Optimizer), NumPy (Predictor)
- **Frontend**: React + Vite, Tailwind CSS, Chart.js
- **Communication**: WebSockets & REST

## Prerequisites
- Docker & Docker Compose
- (Optional) Mapbox API Key for map tiles

## Setup & Run

1.  **Clone the project**
2.  **Generate .env (Optional)**
    The project works out of the box with defaults, but you can configure the database URL in the `docker-compose.yml`.
3.  **Run with Docker Compose**
    
