
class FCRSystem:
    def __init__(self, min_reserve):
        """
        Initialize the FCR system.

        Parameters:
        - min_reserve: Float. The minimum reserve energy to maintain in kWh.
        """
        self.min_reserve = min_reserve

    def regulate_grid_frequency(self, stored_energy, demand):
        """
        Decide the amount of energy to release to the grid based on stored energy and demand.

        Parameters:
        - stored_energy: Float. The amount of energy available in storage in kWh.
        - demand: Float. The energy demand of the grid in kWh.

        Returns:
        - Energy to release to the grid in kWh.
        """
        if stored_energy > self.min_reserve:
            energy_to_release = min(stored_energy - self.min_reserve, demand)
            return energy_to_release
        return 0
