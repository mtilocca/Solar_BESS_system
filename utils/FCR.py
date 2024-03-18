import numpy as np
from scipy.optimize import minimize

class FCR:
    def __init__(self, base_min_reserve, max_reserve_increase_factor=1.5):
        """
        Initialize the optimized FCR system with dynamic and optimized reserve management.

        Parameters:
        - base_min_reserve: Float. The baseline minimum reserve energy to maintain in kWh.
        - max_reserve_increase_factor: Float. The maximum factor by which the reserve can increase.
        """
        self.base_min_reserve = base_min_reserve
        self.max_reserve_increase_factor = max_reserve_increase_factor
        self.current_min_reserve = base_min_reserve

    def optimize_reserve(self, stored_energy, demand_forecast, renewable_forecast):
        """
        Use optimization to find the optimal reserve considering demand and renewable energy forecasts.

        Parameters:
        - stored_energy: Float. The current amount of energy stored in kWh.
        - demand_forecast: Array-like. Forecasted demand for the upcoming period in kWh.
        - renewable_forecast: Array-like. Forecasted renewable energy generation in kWh.
        """
        # Define the optimization objective function: Minimize reserve while meeting demand
        def objective_function(reserve):
            # Calculate net demand after accounting for renewable generation
            net_demand = np.maximum(demand_forecast - renewable_forecast - reserve, 0)
            # Objective is to minimize the sum of unmet demand (if any) and excess reserve
            return np.sum(net_demand) + np.sum(np.maximum(reserve - stored_energy, 0))

        # Constraints: Reserve cannot be negative and cannot exceed the increase factor times the base_min_reserve
        bounds = [(0, self.base_min_reserve * self.max_reserve_increase_factor)]

        # Initial guess for the reserve
        initial_guess = [self.base_min_reserve]

        # Perform optimization
        result = minimize(objective_function, initial_guess, bounds=bounds)
        
        if result.success:
            optimized_reserve = result.x[0]
        else:
            optimized_reserve = self.base_min_reserve

        # Update current_min_reserve based on optimization result
        self.current_min_reserve = optimized_reserve

    def update_reserve_requirements(self, grid_frequency, nominal_frequency=50.0, frequency_threshold=0.1):
        """
        Dynamically update the reserve requirements based on the current grid frequency.

        Parameters:
        - grid_frequency: Float. The current frequency of the grid in Hz.
        - nominal_frequency: Float. The nominal grid frequency in Hz.
        - frequency_threshold: Float. The frequency deviation threshold for increasing the reserve.
        """
        frequency_deviation = abs(grid_frequency - nominal_frequency)
        
        if frequency_deviation > frequency_threshold:
            # Increase the reserve requirements based on the severity of frequency deviation
            deviation_factor = min(frequency_deviation / frequency_threshold, self.max_reserve_increase_factor)
            self.current_min_reserve = self.base_min_reserve * deviation_factor
        else:
            # Reset to base minimum reserve if the frequency is within acceptable bounds
            self.current_min_reserve = self.base_min_reserve


    def regulate_grid_frequency(self, stored_energy, demand, grid_frequency, demand_forecast, renewable_forecast):
        """
        Decide the amount of energy to release to the grid based on optimized reserve requirements, demand, and grid frequency.

        Parameters:
        - stored_energy: Float. The amount of energy available in storage in kWh.
        - demand: Float. The energy demand of the grid in kWh.
        - grid_frequency: Float. The current frequency of the grid in Hz.
        - demand_forecast: Array-like. Forecasted demand for the upcoming period in kWh.
        - renewable_forecast: Array-like. Forecasted renewable energy generation in kWh.
        """
        # Update reserve requirements based on grid frequency
        self.update_reserve_requirements(grid_frequency)
        
        # Optimize reserve considering forecasts
        self.optimize_reserve(stored_energy, demand_forecast, renewable_forecast)
        
        # Decide on the energy to release
        if stored_energy > self.current_min_reserve:
            energy_to_release = min(stored_energy - self.current_min_reserve, demand)
            return energy_to_release
        return 0
