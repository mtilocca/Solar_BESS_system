import json
import matplotlib.pyplot as plt
from solar import SolarPanel
from BESS import BESS
import os 
import sys 

# Determine the project directory by going up one level from the script's directory
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the project directory to sys.path if it's not already there
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from utils.FCR import FCRSystem

def load_profile(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def simulate_day(solar_panel, bess, fcr_system, sunlight_profile, grid_demand_profile):
    produced_energy_list = []
    stored_charge_percentage_list = []
    released_energy_list = []
    
    for time_step, (sunlight_intensity, grid_demand) in enumerate(zip(sunlight_profile["sunlight_intensity"], grid_demand_profile["grid_demand"])):
        produced_energy = solar_panel.generate_power(sunlight_intensity)
        bess.store_energy(produced_energy)
        
        energy_to_release = fcr_system.regulate_grid_frequency(bess.stored_energy, grid_demand)
        released_energy = bess.release_energy(energy_to_release)
        
        produced_energy_list.append(produced_energy)
        stored_charge_percentage_list.append(bess.get_state_of_charge())
        released_energy_list.append(released_energy)
        
        print(f"Time step {time_step}: Produced {produced_energy:.2f} kW, Stored {bess.get_state_of_charge():.2f}% charge, Released {released_energy:.2f} kW to grid")
    
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
    plt.show()

def main():
    sunlight_profile = load_profile('sunlight_profile.json')
    grid_demand_profile = load_profile('grid_demand_profile.json')

    solar_panel = SolarPanel(efficiency=0.15, area=20)
    bess = BESS(capacity=100, efficiency=0.95)
    fcr_system = FCRSystem(min_reserve=10)

    produced_energy, stored_charge_percentage, released_energy = simulate_day(solar_panel, bess, fcr_system, sunlight_profile, grid_demand_profile)
    
    plot_results(produced_energy, stored_charge_percentage, released_energy)

if __name__ == "__main__":
    main()