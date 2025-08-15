"""
Temperature Sensor Implementation

Realistic temperature sensor simulation with daily cycles, seasonal variations,
and environmental factors typical of Australian climate conditions.
"""

import math
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import numpy as np

from .base_sensor import BaseSensor


class TemperatureSensor(BaseSensor):
    """
    Temperature sensor simulation with realistic environmental patterns.
    
    Simulates temperature variations including:
    - Daily temperature cycles (cooler at night, warmer during day)
    - Seasonal variations (summer/winter differences)
    - Weather pattern influences
    - Location-based base temperatures
    - Thermal mass effects (gradual changes)
    """
    
    def __init__(
        self,
        sensor_id: Optional[str] = None,
        location: str = "Sydney",
        base_temperature: float = 20.0,
        daily_range: float = 10.0,
        seasonal_range: float = 15.0,
        thermal_mass: float = 0.1,
        weather_influence: float = 0.3,
        **kwargs
    ):
        """
        Initialise temperature sensor with environmental parameters.
        
        Args:
            sensor_id: Unique identifier for the sensor
            location: Geographic location (affects base temperature)
            base_temperature: Average annual temperature in °C
            daily_range: Daily temperature variation range in °C
            seasonal_range: Seasonal temperature variation range in °C
            thermal_mass: Thermal mass factor (0.0=instant, 1.0=very slow response)
            weather_influence: Weather pattern influence factor (0.0-1.0)
            **kwargs: Additional sensor parameters
        """
        # Set temperature-specific defaults
        kwargs.setdefault('sensor_type', 'temperature')
        kwargs.setdefault('units', '°C')
        kwargs.setdefault('range_min', -40.0)  # Extreme cold
        kwargs.setdefault('range_max', 60.0)   # Extreme heat
        kwargs.setdefault('accuracy', 0.5)     # ±0.5°C accuracy
        kwargs.setdefault('precision', 0.1)    # 0.1°C precision
        kwargs.setdefault('sample_rate', 0.1)  # Sample every 10 seconds
        
        super().__init__(sensor_id=sensor_id, **kwargs)
        
        # Temperature-specific properties
        self.location = location
        self.base_temperature = base_temperature
        self.daily_range = daily_range
        self.seasonal_range = seasonal_range
        self.thermal_mass = max(0.0, min(1.0, thermal_mass))
        self.weather_influence = max(0.0, min(1.0, weather_influence))
        
        # Internal state for thermal mass simulation
        self._previous_temperature = base_temperature
        self._weather_offset = 0.0
        self._weather_change_time = datetime.now()
        
        # Location-based adjustments (Australian cities)
        self._location_adjustments = {
            'sydney': {'base': 20.0, 'daily': 8.0, 'seasonal': 12.0},
            'melbourne': {'base': 16.0, 'daily': 10.0, 'seasonal': 15.0},
            'brisbane': {'base': 24.0, 'daily': 7.0, 'seasonal': 8.0},
            'perth': {'base': 19.0, 'daily': 12.0, 'seasonal': 10.0},
            'adelaide': {'base': 18.0, 'daily': 11.0, 'seasonal': 14.0},
            'darwin': {'base': 28.0, 'daily': 5.0, 'seasonal': 4.0},
            'hobart': {'base': 14.0, 'daily': 8.0, 'seasonal': 10.0},
            'canberra': {'base': 15.0, 'daily': 12.0, 'seasonal': 18.0},
            'alice springs': {'base': 22.0, 'daily': 18.0, 'seasonal': 20.0},
            'cairns': {'base': 26.0, 'daily': 6.0, 'seasonal': 6.0}
        }
        
        # Apply location adjustments if available
        location_key = location.lower()
        if location_key in self._location_adjustments:
            adj = self._location_adjustments[location_key]
            self.base_temperature = adj['base']
            self.daily_range = adj['daily']
            self.seasonal_range = adj['seasonal']
    
    def _get_day_of_year(self, timestamp: datetime) -> int:
        """Get day of year (1-365/366) for seasonal calculations."""
        return timestamp.timetuple().tm_yday
    
    def _get_hour_of_day(self, timestamp: datetime) -> float:
        """Get hour of day as float (0.0-24.0) for daily cycle calculations."""
        return timestamp.hour + timestamp.minute / 60.0 + timestamp.second / 3600.0
    
    def _calculate_seasonal_component(self, timestamp: datetime) -> float:
        """
        Calculate seasonal temperature variation.
        
        Australian seasons:
        - Summer: December, January, February (hot)
        - Autumn: March, April, May (cooling)
        - Winter: June, July, August (cold)
        - Spring: September, October, November (warming)
        """
        day_of_year = self._get_day_of_year(timestamp)
        
        # Peak summer around day 15 (mid-January)
        # Peak winter around day 196 (mid-July)
        seasonal_cycle = math.cos(2 * math.pi * (day_of_year - 15) / 365.25)
        
        return seasonal_cycle * self.seasonal_range / 2
    
    def _calculate_solar_radiation_effect(self, timestamp: datetime) -> float:
        """
        Calculate temperature effect from solar radiation using basic solar geometry.
        
        Uses simplified solar elevation angle calculation and clear sky radiation model.
        """
        hour = self._get_hour_of_day(timestamp)
        day_of_year = self._get_day_of_year(timestamp)
        
        # Solar declination angle (simplified)
        declination = 23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))
        
        # Hour angle (degrees from solar noon)
        hour_angle = 15 * (hour - 12)
        
        # Solar elevation angle (simplified for Australian latitudes ~-35°)
        latitude = -35.0  # Approximate for most Australian cities
        elevation = math.asin(
            math.sin(math.radians(declination)) * math.sin(math.radians(latitude)) +
            math.cos(math.radians(declination)) * math.cos(math.radians(latitude)) * 
            math.cos(math.radians(hour_angle))
        )
        
        # Solar radiation effect (positive during day, negative at night)
        if elevation > 0:
            # Simplified clear sky radiation model
            solar_intensity = max(0, math.sin(elevation)) * self.daily_range
        else:
            # Radiative cooling at night
            solar_intensity = -0.2 * self.daily_range
        
        return solar_intensity
    
    def _update_weather_influence(self, timestamp: datetime) -> None:
        """
        Update weather-related temperature influence.
        
        Simulates weather patterns that can cause temporary temperature changes
        like cloud cover, wind, rain, etc.
        """
        # Update weather pattern every 30-120 minutes
        time_since_change = timestamp - self._weather_change_time
        change_interval = timedelta(minutes=np.random.uniform(30, 120))
        
        if time_since_change > change_interval:
            # Generate new weather influence
            # Can cause ±5°C changes due to weather
            self._weather_offset = np.random.normal(0, 2.0) * self.weather_influence
            self._weather_change_time = timestamp
    
    def _apply_thermal_mass(self, target_temperature: float) -> float:
        """
        Apply thermal mass effect to temperature changes.
        
        Real sensors don't change temperature instantly - there's a delay
        based on the thermal mass of the sensor and surrounding environment.
        """
        if self.thermal_mass == 0:
            return target_temperature
        
        # Exponential approach to target temperature
        # Higher thermal mass = slower response
        response_rate = 1.0 - self.thermal_mass
        
        temperature_change = target_temperature - self._previous_temperature
        actual_change = temperature_change * response_rate
        
        new_temperature = self._previous_temperature + actual_change
        self._previous_temperature = new_temperature
        
        return new_temperature
    
    def _generate_base_value(self, timestamp: datetime) -> float:
        """
        Generate the base temperature value for the given timestamp.
        
        Combines all temperature influences:
        - Base temperature for location
        - Seasonal variations
        - Daily temperature cycles
        - Weather influences
        - Thermal mass effects
        """
        # Update weather influence
        self._update_weather_influence(timestamp)
        
        # Calculate temperature components
        seasonal_temp = self._calculate_seasonal_component(timestamp)
        solar_temp = self._calculate_solar_radiation_effect(timestamp)
        
        # Combine all influences
        ideal_temperature = (
            self.base_temperature +
            seasonal_temp +
            solar_temp +
            self._weather_offset
        )
        
        # Apply thermal mass effect
        actual_temperature = self._apply_thermal_mass(ideal_temperature)
        
        return actual_temperature
    
    def set_location(self, location: str) -> None:
        """
        Change the sensor location and update temperature parameters.
        
        Args:
            location: New location name
        """
        self.location = location
        
        # Apply location adjustments if available
        location_key = location.lower()
        if location_key in self._location_adjustments:
            adj = self._location_adjustments[location_key]
            self.base_temperature = adj['base']
            self.daily_range = adj['daily']
            self.seasonal_range = adj['seasonal']
    
    def set_weather_conditions(self, condition: str, intensity: float = 1.0) -> None:
        """
        Manually set weather conditions affecting temperature.
        
        Args:
            condition: Weather condition ('sunny', 'cloudy', 'rainy', 'windy')
            intensity: Intensity of the weather effect (0.0-2.0)
        """
        weather_effects = {
            'sunny': 3.0,      # Warmer due to direct sunlight
            'cloudy': -1.0,    # Cooler due to reduced sunlight
            'rainy': -2.5,     # Cooler due to evaporation and cloud cover
            'windy': -1.5,     # Cooler due to wind chill
            'stormy': -3.0,    # Significantly cooler
            'clear_night': -2.0  # Cooler due to radiation cooling
        }
        
        base_effect = weather_effects.get(condition.lower(), 0.0)
        self._weather_offset = base_effect * intensity * self.weather_influence
        self._weather_change_time = datetime.now()
    
    def get_temperature_info(self) -> Dict[str, Any]:
        """
        Get detailed temperature sensor information.
        
        Returns:
            Dictionary with temperature-specific information
        """
        base_info = self.get_info()
        
        temperature_info = {
            'location': self.location,
            'base_temperature': self.base_temperature,
            'daily_range': self.daily_range,
            'seasonal_range': self.seasonal_range,
            'thermal_mass': self.thermal_mass,
            'weather_influence': self.weather_influence,
            'current_weather_offset': self._weather_offset,
            'previous_temperature': self._previous_temperature,
            'supported_locations': list(self._location_adjustments.keys())
        }
        
        # Merge with base sensor info
        base_info.update(temperature_info)
        return base_info
    
    def simulate_temperature_profile(
        self,
        duration_hours: float = 24.0,
        start_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate a temperature profile over a specified duration.
        
        Args:
            duration_hours: Duration of simulation in hours
            start_time: Starting time (defaults to now)
            
        Returns:
            Dictionary containing timestamps and temperature readings
        """
        if not self.is_active:
            self.activate()
        
        start_time = start_time or datetime.now()
        readings = []
        timestamps = []
        
        # Generate readings every 10 minutes for the profile
        interval = timedelta(minutes=10)
        total_readings = int(duration_hours * 6)  # 6 readings per hour
        
        for i in range(total_readings):
            timestamp = start_time + (interval * i)
            reading = self.read(timestamp)
            
            readings.append(reading.value)
            timestamps.append(timestamp)
        
        return {
            'timestamps': timestamps,
            'temperatures': readings,
            'location': self.location,
            'duration_hours': duration_hours,
            'base_temperature': self.base_temperature,
            'sensor_id': self.sensor_id
        }
