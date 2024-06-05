import json
import matplotlib.pyplot as plt
from solar import SolarPanelSimulation as SolarPanel
from BESS import LithiumBatteryBESS as BESS
import os
import sys

# Determine the project directory by going up one level from the script's directory
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the project directory to sys.path if it's not already there
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from utils.FCR import FCR as FCRSystem

def load_profile(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def simulate_day(solar_panel, bess, fcr_system, sunlight_profile, grid_demand_profile):
    produced_energy_list = []
    stored_charge_percentage_list = []
    released_energy_list = []

    # Simulate the PV system power output
    power_output_df = solar_panel.simulate()

    # Dummy grid frequency
    grid_frequency = 50.0  # Assuming nominal frequency

    # Adjust forecasts to match the period being simulated (24-hour period in this case)
    demand_forecast = grid_demand_profile["grid_demand"][:24]  # Assuming one day forecast
    renewable_forecast = power_output_df['Power_Output_kW'].values[:24]  # Assuming one day forecast

    for time_step, (produced_energy, grid_demand) in enumerate(zip(power_output_df['Power_Output_kW'][:24], grid_demand_profile["grid_demand"][:24])):
        # Assume a constant charge/discharge rate for simplicity
        charge_rate_C = 0.5
        discharge_rate_C = 1.0

        # Charge the battery with produced energy
        bess.charge(produced_energy, charge_rate_C)

        # Determine energy to release based on FCR system
        energy_to_release = fcr_system.regulate_grid_frequency(
            bess.current_capacity_kWh, 
            grid_demand, 
            grid_frequency, 
            demand_forecast, 
            renewable_forecast
        )
        bess.discharge(energy_to_release, discharge_rate_C)

        released_energy = min(energy_to_release, bess.get_state_of_charge() * bess.current_capacity_kWh)

        produced_energy_list.append(produced_energy)
        stored_charge_percentage_list.append(bess.get_state_of_charge() * 100)
        released_energy_list.append(released_energy)

        print(f"Time step {time_step}: Produced {produced_energy:.2f} kW, Stored {bess.get_state_of_charge()*100:.2f}% charge, Released {released_energy:.2f} kW to grid")

    return produced_energy_list, stored_charge_percentage_list, released_energy_list

def plot_results(produced_energy, stored_charge_percentage, released_energy):
    time_steps = list(range(len(produced_energy)))

    plt.figure(figsize=(14, 7))

    plt.subplot(3, 1, 1)
    plt.plot(time_steps, produced_energy, label='Produced Energy (kW)')
    plt.ylabel('Energy (kW)')
    plt.title('Energy Production, Storage, and Release')
    plt.legend()

    plt.subplot(3, 1, 2)
    plt.plot(time_steps, stored_charge_percentage, label='Stored Energy (%)', color='orange')
    plt.ylabel('Charge (%)')
    plt.legend()

    plt.subplot(3, 1, 3)
    plt.plot(time_steps, released_energy, label='Released Energy (kW)', color='green')
    plt.xlabel('Time Step')
    plt.ylabel('Energy (kW)')
    plt.legend()

    plt.tight_layout()
    plt.savefig('simulation_results.png')  # Save the plot instead of showing it

def main():
    sunlight_profile = load_profile('sunlight_profile.json')
    grid_demand_profile = load_profile('grid_demand_profile.json')

    solar_panel = SolarPanel(
        latitude=-31.9505, 
        longitude=115.8605, 
        altitude=10,  # Assuming a generic altitude
        surface_tilt=15,  # This might be optimized based on specific goals
        surface_azimuth=0  # North-facing in the southern hemisphere
    )
    bess = BESS(nominal_capacity_kWh=100, temperature=25.0)
    fcr_system = FCRSystem(base_min_reserve=10)

    produced_energy, stored_charge_percentage, released_energy = simulate_day(solar_panel, bess, fcr_system, sunlight_profile, grid_demand_profile)

    plot_results(produced_energy, stored_charge_percentage, released_energy)

if __name__ == "__main__":
    main()


