from ortools.linear_solver import pywraplp

class DispatchOptimizer:
    def optimize(self, routes_data: list):
        """
        routes_data: list of dicts {id, current_load, buses_available, headway}
        Objective: Minimize (Wait Time + Overcrowding + Fuel Cost)
        """
        solver = pywraplp.Solver.CreateSolver('SCIP')
        if not solver:
            return []

        results = []
        for route in routes_data:
            # x: change in number of vehicles (-3 to +5)
            x = solver.IntVar(-3, 5, f'adj_{route["id"]}')
            
            # Constraints
            # Cannot remove more buses than available
            solver.Add(x + route['buses_available'] >= 1)
            
            # Objective for this route:
            # Penalty for load > 0.8: 1000 * (load - 0.8)
            # Penalty for cost: 50 per additional bus
            # Benefit of reduction: 30 per bus removed
            load = route['current_load']
            overcrowding_penalty = max(0, (load - 0.8)) * 1000
            
            # Decision influence: adding buses reduces load (approx 10% per bus)
            # Minimize: (FutureLoadPenalty) + (OperationalCost)
            solver.Minimize( (load - x*0.1) * 500 + x * 50 )
            
            status = solver.Solve()
            adjustment = 0
            if status == pywraplp.Solver.OPTIMAL:
                adjustment = int(x.solution_value())

            action = "STABLE"
            if adjustment > 1: action = "DEADHEADING_DEPLOY"
            elif adjustment < -1: action = "SHORT_TURN_RECALL"
            elif adjustment != 0: action = "HEADWAY_ADJUST"

            results.append({
                "route_id": route["id"],
                "adjustment": adjustment,
                "new_headway": max(5, route['headway'] - (adjustment * 2)),
                "action": action
            })
            
        return results

optimizer = DispatchOptimizer()
