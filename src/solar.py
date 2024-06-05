import pvlib
from pvlib import location, irradiance, atmosphere, pvsystem, temperature
import pandas as pd
import logging
import colorlog

# Configure colorlog
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)s: %(message)s',
    log_colors={
        'DEBUG': 'blue',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
))
logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

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
        self.times = pd.date_range(start='2024-01-01 00:00:00', end='2024-01-01 23:59:59', freq='h', tz='Australia/Perth')

        # Example system parameters for a generic crystalline silicon module
        self.pv_system = pvsystem.retrieve_sam('SandiaMod')['Canadian_Solar_CS5P_220M___2009_']
        self.temp_model_params = temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

    def simulate(self):
        """
        Simulate the PV system's power output over a day.
        """
        # Get solar position for the given times
        solar_position = self.location.get_solarposition(self.times)
        
        # Logging: Solar position sample
        logger.debug("Solar Position Sample:\n%s", solar_position.loc['2024-01-01 10:00:00+08:00':'2024-01-01 14:00:00+08:00'])

        # Get clear sky data
        clearsky = self.location.get_clearsky(self.times)

        # Logging: Clear sky irradiance sample
        logger.debug("Clear Sky Irradiance Sample:\n%s", clearsky.loc['2024-01-01 10:00:00+08:00':'2024-01-01 14:00:00+08:00'])

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

        # Logging: POA irradiance sample
        logger.debug("POA Irradiance Sample:\n%s", poa_irradiance.loc['2024-01-01 10:00:00+08:00':'2024-01-01 14:00:00+08:00'])

        # Calculate cell and module temperature
        temp_cell = temperature.sapm_cell(
            poa_global=poa_irradiance['poa_global'],
            wind_speed=1,  # Assuming 1 m/s wind speed
            temp_air=20,  # Assuming 20 degrees Celsius ambient temperature
            **self.temp_model_params
        )

        # Logging: Cell temperature sample
        logger.debug("Cell Temperature Sample:\n%s", temp_cell.loc['2024-01-01 10:00:00+08:00':'2024-01-01 14:00:00+08:00'])

        # Calculate absolute airmass
        airmass_absolute = pvlib.atmosphere.get_absolute_airmass(solar_position['apparent_zenith'])

        # Calculate the angle of incidence (AOI)
        aoi = irradiance.aoi(
            self.surface_tilt,
            self.surface_azimuth,
            solar_position['apparent_zenith'],
            solar_position['azimuth']
        )

        # Logging: AOI sample
        logger.debug("AOI Sample:\n%s", aoi.loc['2024-01-01 10:00:00+08:00':'2024-01-01 14:00:00+08:00'])

        # Calculate the effective irradiance
        effective_irradiance = pvsystem.sapm_effective_irradiance(
            poa_direct=poa_irradiance['poa_direct'],
            poa_diffuse=poa_irradiance['poa_diffuse'],
            airmass_absolute=airmass_absolute,
            aoi=aoi,
            module=self.pv_system
        )

        # Logging: Effective irradiance sample
        logger.debug("Effective Irradiance Sample:\n%s", effective_irradiance.loc['2024-01-01 10:00:00+08:00':'2024-01-01 14:00:00+08:00'])

        # Calculate the DC power output using the SAPM
        power_dc = pvsystem.sapm(effective_irradiance, temp_cell, self.pv_system)

        # Logging: DC power output sample
        logger.debug("DC Power Output Sample:\n%s", power_dc['p_mp'].loc['2024-01-01 10:00:00+08:00':'2024-01-01 14:00:00+08:00'])

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
logger.info("Power Output Sample:\n%s", power_output_df.between_time('10:00', '16:00').head())
