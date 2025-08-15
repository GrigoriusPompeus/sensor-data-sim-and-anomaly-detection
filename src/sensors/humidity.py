"""
Humidity Sensor Implementation

Realistic humidity sensor simulation with temperature correlation,
weather influences, and environmental factors.
"""

import math
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import numpy as np

from .base_sensor import BaseSensor


class HumiditySensor(BaseSensor):
    """
    Relative humidity sensor simulation with realistic environmental patterns.
    
    Simulates humidity variations including:
    - Temperature-dependent humidity relationships
    - Weather pattern influences (rain, clouds, etc.)
    - Diurnal humidity cycles
    - Seasonal humidity patterns
    - Saturation limits and dew point calculations
    """
    
    def __init__(
        self,
        sensor_id: Optional[str] = None,
        base_humidity: float = 60.0,
        temperature_coupling: float = 0.7,
        weather_sensitivity: float = 0.5,
        location_type: str = "urban",  # "urban", "coastal", "inland", "tropical"
        **kwargs
    ):
        """
        Initialise humidity sensor with environmental parameters.
        
        Args:
            sensor_id: Unique identifier for the sensor
            base_humidity: Base relative humidity percentage
            temperature_coupling: How much temperature affects humidity (0.0-1.0)
            weather_sensitivity: Sensitivity to weather conditions (0.0-1.0)
            location_type: Type of location affecting humidity patterns
            **kwargs: Additional sensor parameters
        """
        # Set humidity-specific defaults
        kwargs.setdefault('sensor_type', 'humidity')
        kwargs.setdefault('units', '%RH')
        kwargs.setdefault('range_min', 0.0)     # 0% RH
        kwargs.setdefault('range_max', 100.0)   # 100% RH
        kwargs.setdefault('accuracy', 2.0)      # ±2% RH accuracy
        kwargs.setdefault('precision', 0.1)     # 0.1% RH precision
        kwargs.setdefault('sample_rate', 0.1)   # Sample every 10 seconds
        
        super().__init__(sensor_id=sensor_id, **kwargs)
        
        # Humidity-specific properties
        self.base_humidity = max(0.0, min(100.0, base_humidity))
        self.temperature_coupling = max(0.0, min(1.0, temperature_coupling))
        self.weather_sensitivity = max(0.0, min(1.0, weather_sensitivity))
        self.location_type = location_type
        
        # Internal state
        self._current_temperature = 20.0  # Assumed temperature for calculations
        self._weather_humidity_offset = 0.0
        self._last_weather_update = datetime.now()
        
        # Location-specific humidity characteristics
        self._location_characteristics = {
            'coastal': {
                'base_humidity': 70.0,
                'seasonal_range': 15.0,
                'daily_range': 20.0,
                'rain_sensitivity': 1.2
            },
            'inland': {
                'base_humidity': 50.0,
                'seasonal_range': 25.0,
                'daily_range': 30.0,
                'rain_sensitivity': 1.5
            },
            'urban': {
                'base_humidity': 60.0,
                'seasonal_range': 20.0,
                'daily_range': 25.0,
                'rain_sensitivity': 1.0
            },
            'tropical': {
                'base_humidity': 80.0,
                'seasonal_range': 10.0,
                'daily_range': 15.0,
                'rain_sensitivity': 0.8
            },
            'arid': {
                'base_humidity': 30.0,
                'seasonal_range': 20.0,
                'daily_range': 35.0,
                'rain_sensitivity': 2.0
            }
        }
        
        # Apply location characteristics
        if location_type in self._location_characteristics:
            char = self._location_characteristics[location_type]
            self.base_humidity = char['base_humidity']
    
    def _calculate_saturation_humidity(self, temperature: float) -> float:
        """
        Calculate saturation humidity at given temperature using Magnus formula.
        
        Args:
            temperature: Temperature in Celsius
            
        Returns:
            Saturation humidity in %RH (always 100% at saturation)
        """
        # Magnus formula for saturation vapour pressure
        # At saturation, RH = 100%
        return 100.0
    
    def _calculate_psychrometric_humidity(self, temperature: float, timestamp: datetime) -> float:
        """
        Calculate humidity using psychrometric relationships and saturation vapour pressure.
        
        Uses the Magnus formula and considers temperature-humidity coupling
        based on actual atmospheric physics.
        """
        # Magnus formula constants
        a = 17.27
        b = 237.7
        
        # Calculate saturation vapour pressure at current temperature
        sat_vapour_pressure = 6.112 * math.exp((a * temperature) / (b + temperature))
        
        # Base saturation vapour pressure at reference temperature (20°C)
        ref_temp = 20.0
        ref_sat_pressure = 6.112 * math.exp((a * ref_temp) / (b + ref_temp))
        
        # Temperature effect on relative humidity
        # When temperature increases, RH decreases if absolute humidity stays constant
        temp_ratio = ref_sat_pressure / sat_vapour_pressure if sat_vapour_pressure > 0 else 1.0
        
        # Apply psychrometric relationship
        psychrometric_adjustment = (temp_ratio - 1.0) * 100 * self.temperature_coupling
        
        return psychrometric_adjustment
    
    def _calculate_seasonal_humidity(self, timestamp: datetime) -> float:
        """
        Calculate seasonal humidity variations.
        
        In Australia:
        - Summer (Dec-Feb): Generally lower humidity inland, higher coastal
        - Winter (Jun-Aug): Higher humidity inland, variable coastal
        """
        day_of_year = timestamp.timetuple().tm_yday
        location_char = self._location_characteristics.get(
            self.location_type, self._location_characteristics['urban']
        )
        
        # Seasonal cycle (summer = low for most areas except tropical/coastal)
        seasonal_cycle = math.cos(2 * math.pi * (day_of_year - 15) / 365.25)
        
        # Adjust based on location type
        if self.location_type in ['tropical', 'coastal']:
            # Tropical/coastal areas have less seasonal variation
            seasonal_effect = seasonal_cycle * location_char['seasonal_range'] / 4
        else:
            # Inland areas have more seasonal variation
            seasonal_effect = seasonal_cycle * location_char['seasonal_range'] / 2
        
        return seasonal_effect
    
    def _calculate_daily_humidity_cycle(self, timestamp: datetime) -> float:
        """
        Calculate daily humidity variations.
        
        Typically:
        - Highest humidity early morning (around 6 AM)
        - Lowest humidity mid-afternoon (around 2-4 PM)
        """
        hour = timestamp.hour + timestamp.minute / 60.0
        location_char = self._location_characteristics.get(
            self.location_type, self._location_characteristics['urban']
        )
        
        # Daily cycle - minimum around 15:00 (3 PM), maximum around 6:00 AM
        daily_cycle = math.cos(2 * math.pi * (hour - 6) / 24)
        
        # Scale by location-specific daily range
        daily_effect = daily_cycle * location_char['daily_range'] / 2
        
        return daily_effect
    
    def _update_weather_influence(self, timestamp: datetime) -> None:
        """
        Update weather-related humidity influences.
        
        Weather events like rain, clouds, wind affect humidity levels.
        """
        time_since_update = timestamp - self._last_weather_update
        update_interval = timedelta(minutes=np.random.uniform(30, 180))
        
        if time_since_update > update_interval:
            # Generate weather influence
            location_char = self._location_characteristics.get(
                self.location_type, self._location_characteristics['urban']
            )
            
            # Random weather effect with location sensitivity
            base_change = np.random.normal(0, 10) * self.weather_sensitivity
            rain_modifier = location_char['rain_sensitivity']
            
            # Chance of rain/high humidity event
            if np.random.random() < 0.1:  # 10% chance of high humidity event
                base_change += np.random.uniform(15, 30) * rain_modifier
            
            self._weather_humidity_offset = base_change
            self._last_weather_update = timestamp
    
    def set_current_temperature(self, temperature: float) -> None:
        """
        Set the current ambient temperature for humidity calculations.
        
        Args:
            temperature: Current temperature in Celsius
        """
        self._current_temperature = temperature
    
    def set_weather_condition(self, condition: str, intensity: float = 1.0) -> None:
        """
        Manually set weather conditions affecting humidity.
        
        Args:
            condition: Weather condition ('sunny', 'cloudy', 'rainy', 'stormy')
            intensity: Intensity of the weather effect (0.0-2.0)
        """
        location_char = self._location_characteristics.get(
            self.location_type, self._location_characteristics['urban']
        )
        
        weather_effects = {
            'sunny': -15.0,        # Lower humidity due to evaporation
            'cloudy': 5.0,         # Slightly higher humidity
            'rainy': 25.0,         # Much higher humidity
            'stormy': 30.0,        # Very high humidity
            'foggy': 35.0,         # Near saturation
            'windy': -10.0,        # Lower humidity due to air movement
            'dry': -20.0,          # Very low humidity
            'humid': 20.0          # High humidity conditions
        }
        
        base_effect = weather_effects.get(condition.lower(), 0.0)
        rain_sensitivity = location_char['rain_sensitivity']
        
        self._weather_humidity_offset = (
            base_effect * intensity * self.weather_sensitivity * rain_sensitivity
        )
        self._last_weather_update = datetime.now()
        
        print(f"Set weather condition: {condition} (intensity: {intensity})")
    
    def _generate_base_value(self, timestamp: datetime) -> float:
        """
        Generate the base humidity value for the given timestamp.
        
        Combines all humidity influences:
        - Base humidity for location type
        - Temperature effects
        - Seasonal variations
        - Daily humidity cycles
        - Weather influences
        """
        # Update weather influence
        self._update_weather_influence(timestamp)
        
        # Start with base humidity
        humidity = self.base_humidity
        
        # Add psychrometric temperature effect
        humidity += self._calculate_psychrometric_humidity(self._current_temperature, timestamp)
        
        # Add seasonal variation
        humidity += self._calculate_seasonal_humidity(timestamp)
        
        # Add daily cycle
        humidity += self._calculate_daily_humidity_cycle(timestamp)
        
        # Add weather influence
        humidity += self._weather_humidity_offset
        
        # Ensure humidity stays within physical limits (0-100%)
        humidity = max(0.0, min(100.0, humidity))
        
        return humidity
    
    def calculate_dew_point(self, humidity: float, temperature: float) -> float:
        """
        Calculate dew point temperature given humidity and temperature.
        
        Args:
            humidity: Relative humidity in %RH
            temperature: Temperature in Celsius
            
        Returns:
            Dew point temperature in Celsius
        """
        # Magnus formula for dew point calculation
        a = 17.27
        b = 237.7
        
        alpha = ((a * temperature) / (b + temperature)) + math.log(humidity / 100.0)
        dew_point = (b * alpha) / (a - alpha)
        
        return dew_point
    
    def calculate_absolute_humidity(self, humidity: float, temperature: float) -> float:
        """
        Calculate absolute humidity given relative humidity and temperature.
        
        Args:
            humidity: Relative humidity in %RH
            temperature: Temperature in Celsius
            
        Returns:
            Absolute humidity in g/m³
        """
        # Magnus formula for saturation vapour pressure
        a = 17.27
        b = 237.7
        
        saturation_pressure = 6.112 * math.exp((a * temperature) / (b + temperature))
        actual_pressure = saturation_pressure * (humidity / 100.0)
        
        # Convert to absolute humidity using ideal gas law
        # AH = (vapour_pressure * molar_mass) / (gas_constant * temperature_kelvin)
        temp_kelvin = temperature + 273.15
        absolute_humidity = (actual_pressure * 18.016) / (0.08314 * temp_kelvin * 100)
        
        return absolute_humidity
    
    def get_humidity_analysis(self, temperature: Optional[float] = None) -> Dict[str, Any]:
        """
        Get comprehensive humidity analysis including derived values.
        
        Args:
            temperature: Current temperature for calculations (uses stored if None)
            
        Returns:
            Dictionary with humidity analysis
        """
        if temperature is None:
            temperature = self._current_temperature
        
        # Get current humidity reading
        current_reading = self.read() if self.is_active else None
        humidity = current_reading.value if current_reading else self.base_humidity
        
        # Calculate derived values
        dew_point = self.calculate_dew_point(humidity, temperature)
        absolute_humidity = self.calculate_absolute_humidity(humidity, temperature)
        
        # Comfort analysis
        if humidity < 30:
            comfort = "Too dry - may cause discomfort"
        elif humidity > 70:
            comfort = "Too humid - may feel uncomfortable"
        else:
            comfort = "Comfortable humidity range"
        
        return {
            'relative_humidity': humidity,
            'temperature': temperature,
            'dew_point': round(dew_point, 1),
            'absolute_humidity': round(absolute_humidity, 2),
            'comfort_assessment': comfort,
            'location_type': self.location_type,
            'weather_offset': self._weather_humidity_offset
        }
    
    def get_humidity_info(self) -> Dict[str, Any]:
        """
        Get detailed humidity sensor information.
        
        Returns:
            Dictionary with humidity-specific information
        """
        base_info = self.get_info()
        
        humidity_info = {
            'base_humidity': self.base_humidity,
            'temperature_coupling': self.temperature_coupling,
            'weather_sensitivity': self.weather_sensitivity,
            'location_type': self.location_type,
            'current_temperature': self._current_temperature,
            'weather_humidity_offset': self._weather_humidity_offset,
            'supported_locations': list(self._location_characteristics.keys()),
            'humidity_analysis': self.get_humidity_analysis()
        }
        
        # Merge with base sensor info
        base_info.update(humidity_info)
        return base_info
