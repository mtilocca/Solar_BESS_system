import numpy as np

class LithiumBatteryBESS:
    def __init__(self, nominal_capacity_kWh, temperature=25.0):
        """
        Initialize the Advanced Lithium Battery BESS model.

        Parameters:
        - nominal_capacity_kWh: float. The total energy capacity of the battery when new in kWh.
        - temperature: float. The ambient temperature in degrees Celsius.
        """
        self.nominal_capacity_kWh = nominal_capacity_kWh
        self.current_capacity_kWh = nominal_capacity_kWh  # Initial capacity
        self.temperature = temperature
        self.soc = 0.0  # State of Charge (0-1)
        self.cycles = 0  # Completed cycles
        self.cycle_depth = 0.0  # Depth of the last cycle

    def charge(self, energy_kWh, charge_rate_C):
        """
        Charge the battery with a given amount of energy and at a specific rate, considering temperature effects.

        Parameters:
        - energy_kWh: float. The amount of energy to charge the battery in kWh.
        - charge_rate_C: float. The charge rate in terms of C (capacity of the battery).
        """
        # Calculate charge efficiency based on temperature and charge rate
        charge_efficiency = self._calculate_efficiency(charge_rate_C, self.temperature)
        
        # Adjust energy to charge based on efficiency
        effective_charge_kWh = energy_kWh * charge_efficiency
        
        # Update SOC
        self._update_soc(effective_charge_kWh, increase=True)

    def discharge(self, energy_kWh, discharge_rate_C):
        """
        Discharge the battery by a given amount of energy and at a specific rate, considering temperature effects.

        Parameters:
        - energy_kWh: float. The amount of energy to discharge from the battery in kWh.
        - discharge_rate_C: float. The discharge rate in terms of C (capacity of the battery).
        """
        # Calculate discharge efficiency based on temperature and discharge rate
        discharge_efficiency = self._calculate_efficiency(discharge_rate_C, self.temperature)
        
        # Adjust energy to discharge based on efficiency
        effective_discharge_kWh = energy_kWh / discharge_efficiency
        
        # Update SOC
        self._update_soc(effective_discharge_kWh, increase=False)

    def _calculate_efficiency(self, rate_C, temp):
        """
        Calculate the charging/discharging efficiency based on rate and temperature.

        Parameters:
        - rate_C: float. The charge/discharge rate in terms of C.
        - temp: float. The temperature in degrees Celsius.

        Returns:
        - efficiency: float. The efficiency of charging or discharging.
        """
        # Simplified model: Efficiency decreases with increasing rate and deviating temperature from 25 C
        efficiency = np.clip(1 - 0.01 * np.abs(temp - 25) - 0.05 * (rate_C - 1), 0.7, 1)
        return efficiency

    def _update_soc(self, energy_kWh, increase=True):
        """
        Update the state of charge of the battery after charging or discharging.

        Parameters:
        - energy_kWh: float. The amount of energy in kWh.
        - increase: bool. True if charging, False if discharging.
        """
        delta_soc = energy_kWh / self.current_capacity_kWh
        self.soc = np.clip(self.soc + delta_soc if increase else self.soc - delta_soc, 0, 1)

    def cycle(self, depth):
        """
        Simulate a full charge-discharge cycle with a specified depth and update capacity.

        Parameters:
        - depth: float. The depth of discharge (DOD) of the cycle (0-1).
        """
        self.cycles += 1
        self.cycle_depth = depth
        self._calculate_capacity_fade()

    def _calculate_capacity_fade(self):
        """
        Update the battery's capacity based on the cycle depth and temperature.
        """
        # Simplified fade calculation: capacity decreases faster with deeper cycles and higher temperatures
        fade_factor = 0.0001 * self.cycle_depth * (1 + 0.01 * np.abs(self.temperature - 25))
        self.current_capacity_kWh *= (1 - fade_factor)
        
    def get_state_of_charge(self):
        """
        Get the current state of charge of the battery.

        Returns:
        - soc: float. The state of charge of the battery (0-1).
        """
        return self.soc

    def get_remaining_capacity_percent(self):
        """
        Get the current remaining capacity as a percentage of nominal capacity.

        Returns:
        - remaining_capacity_percent: float. The remaining capacity as a percentage.
        """
        return (self.current_capacity_kWh / self.nominal_capacity_kWh) * 100



# Initialize the battery
battery = LithiumBatteryBESS(nominal_capacity_kWh=10, temperature=25.0)

# Simulate charging in the morning at 0.5C rate
# Assuming the battery starts at 0% SOC
print("Morning charging...")
battery.charge(energy_kWh=5, charge_rate_C=0.5)  # Charge 5 kWh at 0.5C rate
print(f"State of Charge after charging: {battery.get_state_of_charge()*100:.2f}%")
print(f"Remaining capacity: {battery.get_remaining_capacity_percent():.2f}%\n")

# Simulate using the battery to supply energy in the evening at 1C rate
print("Evening discharging...")
battery.discharge(energy_kWh=5, discharge_rate_C=1)  # Discharge 5 kWh at 1C rate
print(f"State of Charge after discharging: {battery.get_state_of_charge()*100:.2f}%")
print(f"Remaining capacity: {battery.get_remaining_capacity_percent():.2f}%\n")

# Simulate a full cycle to account for capacity fade
battery.cycle(depth=0.5)  # Assuming a depth of discharge (DOD) of 50%

# Check battery status after one cycle
print("After one cycle:")
print(f"State of Charge: {battery.get_state_of_charge()*100:.2f}%")
print(f"Remaining capacity: {battery.get_remaining_capacity_percent():.2f}%\n")

# Repeat for more cycles to see the effect of degradation over time
for i in range(1, 11):  # Simulate 10 more cycles
    battery.cycle(depth=0.5)

print("After 11 total cycles:")
print(f"Remaining capacity: {battery.get_remaining_capacity_percent():.2f}%")
