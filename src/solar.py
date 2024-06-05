import pvlib
from pvlib import location, irradiance, atmosphere, pvsystem, temperature
import pandas as pd

class SolarPanelSimulation:
    def __init__(self, latitude, longitude, altitude, surface_tilt, surface_azimuth):
        """
        Initialize the Solar Panel Simulation.

        Parameters:
        - latitude (float): Latitude of the location in degrees.
        - longitude (float): Longitude of the location in degrees.
        - altitude (float): Altitude of the location in meters.
        - surface_tilt (float): Tilt angle of the solar panel (degrees).
        - surface_azimuth (float): Azimuth angle of the solar panel (degrees).
        """
        self.location = location.Location(latitude, longitude, altitude=altitude)
        self.surface_tilt = surface_tilt
        self.surface_azimuth = surface_azimuth
        self.times = pd.date_range(start='2024-01-01 00:00:00', end='2024-12-31 23:59:59', freq='h', tz='Australia/Perth')

        # Example system parameters for a generic crystalline silicon module
        self.pv_system = pvsystem.retrieve_sam('SandiaMod')['Canadian_Solar_CS5P_220M___2009_']
        self.temp_model_params = temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

    def simulate(self):
        """
        Simulate the PV system's power output over a year.
        """
        # Get solar position for the given times
        solar_position = self.location.get_solarposition(self.times)
        
        # Debugging: Print solar position sample
        print("Solar Position Sample:")
        print(solar_position.head())

        # Get clear sky data
        clearsky = self.location.get_clearsky(self.times)

        # Debugging: Print clear sky irradiance sample
        print("Clear Sky Irradiance Sample:")
        print(clearsky.head())

        # Calculate POA (plane of array) irradiance
        poa_irradiance = irradiance.get_total_irradiance(
            surface_tilt=self.surface_tilt,
            surface_azimuth=self.surface_azimuth,
            dni=clearsky['dni'],
            ghi=clearsky['ghi'],
            dhi=clearsky['dhi'],
            solar_zenith=solar_position['apparent_zenith'],
            solar_azimuth=solar_position['azimuth']
        )

        # Print intermediate POA irradiance values for debugging
        print("POA Irradiance Sample:")
        print(poa_irradiance.head())

        # Calculate cell and module temperature
        temp_cell = temperature.sapm_cell(
            poa_global=poa_irradiance['poa_global'],
            wind_speed=1,  # Assuming 1 m/s wind speed
            temp_air=20,  # Assuming 20 degrees Celsius ambient temperature
            **self.temp_model_params
        )

        # Print intermediate temperature values for debugging
        print("Cell Temperature Sample:")
        print(temp_cell.head())

        # Calculate absolute airmass
        airmass_absolute = pvlib.atmosphere.get_absolute_airmass(solar_position['apparent_zenith'])

        # Calculate the effective irradiance
        effective_irradiance = pvsystem.sapm_effective_irradiance(
            poa_direct=poa_irradiance['poa_direct'],
            poa_diffuse=poa_irradiance['poa_diffuse'],
            airmass_absolute=airmass_absolute,
            aoi=solar_position['apparent_zenith'],
            module=self.pv_system
        )

        # Print intermediate effective irradiance values for debugging
        print("Effective Irradiance Sample:")
        print(effective_irradiance.head())

        # Calculate the DC power output using the SAPM
        power_dc = pvsystem.sapm(effective_irradiance, temp_cell, self.pv_system)

        # Print intermediate power output values for debugging
        print("DC Power Output Sample:")
        print(power_dc['p_mp'].head())

        power_output_df = pd.DataFrame({
            'Timestamp': self.times,
            'Power_Output_kW': power_dc['p_mp']
        }).set_index('Timestamp')

        return power_output_df

# Example usage
simulation = SolarPanelSimulation(
    latitude=-31.9505, 
    longitude=115.8605, 
    altitude=10,  # Assuming a generic altitude
    surface_tilt=15,  # This might be optimized based on specific goals
    surface_azimuth=0  # North-facing in the southern hemisphere
)
power_output_df = simulation.simulate()

# To see output around noon, you can do something like:
print(power_output_df.between_time('10:00', '16:00').head())
