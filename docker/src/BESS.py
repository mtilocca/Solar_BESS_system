class BESS:
    def __init__(self, capacity, efficiency=0.9):
        """
        Initialize the BESS.

        Parameters:
        - capacity: Float. The maximum energy storage capacity of the BESS in kWh.
        - efficiency: Float. The efficiency of storing and releasing energy (0-1).
        """
        self.capacity = capacity
        self.efficiency = efficiency
        self.stored_energy = 0

    def store_energy(self, energy):
        """
        Store energy in the BESS, considering efficiency.

        Parameters:
        - energy: Float. The amount of energy to store in kWh.
        """
        effective_energy = energy * self.efficiency
        space_left = self.capacity - self.stored_energy
        energy_to_store = min(space_left, effective_energy)
        self.stored_energy += energy_to_store

    def release_energy(self, energy):
        """
        Release energy from the BESS, considering efficiency.

        Parameters:
        - energy: Float. The amount of energy to release in kWh.
        """
        energy_to_release = min(self.stored_energy, energy / self.efficiency)
        self.stored_energy -= energy_to_release
        return energy_to_release * self.efficiency

    def get_state_of_charge(self):
        """
        Get the current state of charge of the BESS.

        Returns:
        - The state of charge as a percentage of the capacity.
        """
        return (self.stored_energy / self.capacity) * 100
