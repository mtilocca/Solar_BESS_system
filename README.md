# Solar Energy Production and Storage Simulation

## Overview

This project simulates the production of energy using solar panels, stores this energy in a Battery Energy Storage System (BESS), and then manages the flow of energy into the grid using Frequency Containment Reserves (FCR). The goal is to efficiently balance energy production, storage, and grid demand.

## Features

- **Solar Energy Simulation**: Dynamically simulate solar energy production based on sunlight intensity data.
- **Energy Storage (BESS)**: Implement a Battery Energy Storage System with efficiency losses during energy storage and retrieval.
- **Grid Energy Management (FCR)**: Use a Frequency Containment Reserve system to regulate energy flow into the grid based on demand and stored energy.

## How to Run

Provide detailed instructions on how to run your project here, including how to install any dependencies, and any configuration steps.

Example:
```bash
python3 main.py
```

## Results

The results of the simulation show how the solar panels produce energy throughout the day, how the BESS stores and releases energy, and how the FCR system regulates the energy flow into the grid.

### Produced Energy

The graph indicates that energy production peaks during the sunniest part of the day and drops to zero during the night. 

### Stored Energy

The BESS initially accumulates energy until it reaches its capacity, after which it starts releasing energy to the grid to meet the demand, all the while maintaining a minimum reserve as per the FCR guidelines.

### Released Energy

Energy is released to the grid once the demand starts to exceed the solar production. The release of energy is higher when there is no solar production to meet the grid demand.

![Energy Production, Storage, and Release](<Screenshot 2024-03-09 at 12.06.56.png>)

(Note: Replace "path/to/image.png" with the actual path to the image in your repository)

## Discussion

Discuss any interesting findings, potential improvements, or real-world implications of your simulation results here.

## Future Work

- A more detailed BESS will be developed 
- A more in depth solar simulation will be carried out 