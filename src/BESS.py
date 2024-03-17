import PySAM.StandAloneBattery as StandAloneBattery

class BESS:
    def __init__(self, capacity_kwh, voltage, current, depth_of_discharge=0.9):
        """
        Initialize the PySAM-based BESS model.

        Parameters:
        - capacity_kwh: Float. The total energy capacity of the battery in kWh.
        - voltage: Float. The nominal voltage of the battery system.
        - current: Float. The nominal current of the battery system.
        - depth_of_discharge: Float. The depth of discharge allowed for the battery.
        """
        self.battery_model = StandAloneBattery.new()
        self.battery_model.BatterySystem.batt_computed_strings = 0
        self.battery_model.BatterySystem.batt_computed_series = 0
        self.battery_model.BatterySystem.batt_current_charge_max = current
        self.battery_model.BatterySystem.batt_current_discharge_max = current
        self.battery_model.BatterySystem.batt_power_charge_max_kwdc = (voltage * current) / 1000.0
        self.battery_model.BatterySystem.batt_power_discharge_max_kwdc = (voltage * current) / 1000.0
        self.battery_model.BatterySystem.batt_voltage_nominal = voltage
        self.battery_model.BatterySystem.batt_voltage_minimum = voltage * depth_of_discharge
        self.battery_model.BatterySystem.batt_capacity_kwh = capacity_kwh
        # Setup the rest of the model parameters as needed...

        self.battery_model.execute(0)  # Executes the model to initialize

    def charge(self, power_kw, timestep):
        """
        Charge the battery with a certain power input.

        Parameters:
        - power_kw: Float. The power with which to charge the battery in kW.
        - timestep: Integer. The time step duration in hours.
        """
        self.battery_model.BatteryPower.batt_power_charge_max_kwdc = power_kw
        # Execute model for the given timestep
        self.battery_model.execute(timestep)

    def discharge(self, power_kw, timestep):
        """
        Discharge the battery with a certain power output.

        Parameters:
        - power_kw: Float. The power with which to discharge the battery in kW.
        - timestep: Integer. The time step duration in hours.
        """
        self.battery_model.BatteryPower.batt_power_discharge_max_kwdc = power_kw
        # Execute model for the given timestep
        self.battery_model.execute(timestep)

    def get_state_of_charge(self):
        """
        Get the current state of charge of the battery.

        Returns:
        - The state of charge as a percentage.
        """
        soc = self.battery_model.BatteryState.batt_SOC
        return soc

# Usage example
battery_system = BESS(capacity_kwh=20, voltage=400, current=50)
battery_system.charge(power_kw=10, timestep=1)  # Charge for 1 hour with 10 kW
battery_system.discharge(power_kw=5, timestep=1)  # Discharge for 1 hour with 5 kW
current_soc = battery_system.get_state_of_charge()
print(f"Current state of charge: {current_soc}%")
