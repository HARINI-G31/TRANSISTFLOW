import numpy as np

class DemandPredictor:
    def __init__(self):
        # Hidden state simulation for LSTM-like memory
        self.state_buffer = {}

    def predict(self, route_id: int, base_load: float, weather: str = "clear", is_event: bool = False, is_peak: bool = False):
        # Simple LSTM-style transition: Current state depends on previous state + inputs
        prev_state = self.state_buffer.get(route_id, base_load)
        
        # Environmental multipliers
        weather_mult = 1.3 if weather == "rainy" else 1.0
        event_mult = 1.6 if is_event else 1.0
        peak_mult = 1.4 if is_peak else 1.0
        
        # Stochastic growth with sigmoid squashing to keep load [0, 1.2]
        noise = np.random.normal(0, 0.05)
        raw_pred = (prev_state * 0.4) + (base_load * 0.6 * weather_mult * event_mult * peak_mult) + noise
        
        # Clamp value
        predicted_load = float(np.clip(raw_pred, 0.1, 1.1))
        self.state_buffer[route_id] = predicted_load
        
        surge_risk = 0.0
        if predicted_load > 0.85:
            surge_risk = (predicted_load - 0.8) / 0.3
            
        status = "Green"
        if predicted_load > 0.5: status = "Yellow"
        if predicted_load > 0.8: status = "Red"
        
        return {
            "predicted_occupancy": round(predicted_load, 3),
            "surge_probability": round(float(np.clip(surge_risk, 0, 1)), 2),
            "status": status
        }

predictor = DemandPredictor()
