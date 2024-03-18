import numpy as np
from scipy.optimize import minimize

class mFRR:
    def __init__(self, max_load_reduction, storage_capacity, initial_storage_level):
        self.max_load_reduction = max_load_reduction
        self.storage_capacity = storage_capacity
        self.storage_level = initial_storage_level

    def decide_action(self, load_forecast, generation_forecast):
        # Net load (demand - generation), positive values indicate shortfall
        net_load = np.array(load_forecast) - np.array(generation_forecast)
        total_shortfall = np.sum(net_load[net_load > 0])

        if total_shortfall <= 0:
            return 0, 0  # No action needed if no shortfall

        def objective(x):
            load_shed, reserve_used = x
            # First priority is covering the shortfall, then minimize load shed and reserve use
            return (load_shed + reserve_used - total_shortfall)**2 + load_shed + reserve_used

        # Constraints to ensure load shed and reserve use are within capabilities and needs
        constraints = [{'type': 'ineq', 'fun': lambda x: self.max_load_reduction - x[0]},  # load shed limit
                       {'type': 'ineq', 'fun': lambda x: self.storage_level - x[1]},  # reserve usage limit
                       {'type': 'ineq', 'fun': lambda x: x[0] + x[1] - 0.01}]  # Ensure some action is taken if shortfall

        # Bounds for each variable (load shed and reserve use)
        bounds = [(0, min(self.max_load_reduction, total_shortfall)), (0, min(self.storage_level, total_shortfall))]

        # Initial guess (try to cover shortfall with reserves first, then shedding load)
        initial_guess = [0, min(self.storage_level, total_shortfall)]

        # Solve the optimization
        result = minimize(objective, initial_guess, constraints=constraints, bounds=bounds, method='SLSQP')

        if result.success:
            load_shed, reserve_used = result.x
        else:
            load_shed, reserve_used = 0, 0

        # Update storage level
        self.storage_level -= reserve_used

        return load_shed, reserve_used

# Example usage
mFRR = mFRR(max_load_reduction=500, storage_capacity=1000, initial_storage_level=500)
load_forecast = [800, 900, 1000, 1100]  # Forecasted load in kW for 4 periods
generation_forecast = [700, 800, 900, 1000]  # Forecasted generation in kW for 4 periods

load_shed, reserve_used = mFRR.decide_action(load_forecast, generation_forecast)
print(f"Load to shed: {load_shed} kW")
print(f"Reserve used: {reserve_used} kWh")
