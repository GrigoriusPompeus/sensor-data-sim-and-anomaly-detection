"""
Pressure Sensor Implementation

Realistic atmospheric pressure sensor simulation with weather patterns,
altitude effects, and barometric pressure variations.
"""

import math
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import numpy as np

from .base_sensor import BaseSensor


class PressureSensor(BaseSensor):
    """
    Atmospheric pressure sensor simulation with realistic environmental patterns.
    
    Simulates pressure variations including:
    - Sea level pressure variations (weather systems)
    - Altitude-based pressure calculations
    - Barometric pressure changes
    - Weather front influences
    - Diurnal pressure variations
    """
    
    def __init__(
        self,
        sensor_id: Optional[str] = None,
        altitude: float = 0.0,
        sea_level_pressure: float = 1013.25,
        weather_variability: float = 0.3,
        measurement_type: str = "absolute",  # "absolute", "gauge", "differential"
        **kwargs
    ):
        """
        Initialise pressure sensor with atmospheric parameters.
        
        Args:
            sensor_id: Unique identifier for the sensor
            altitude: Altitude above sea level in metres
            sea_level_pressure: Standard sea level pressure in hPa
            weather_variability: Weather-induced pressure variation factor (0.0-1.0)
            measurement_type: Type of pressure measurement
            **kwargs: Additional sensor parameters
        """
        # Set pressure-specific defaults
        kwargs.setdefault('sensor_type', 'pressure')
        kwargs.setdefault('units', 'hPa')
        kwargs.setdefault('range_min', 800.0)   # Extreme low pressure
        kwargs.setdefault('range_max', 1100.0)  # Extreme high pressure
        kwargs.setdefault('accuracy', 0.1)      # ±0.1 hPa accuracy
        kwargs.setdefault('precision', 0.01)    # 0.01 hPa precision
        kwargs.setdefault('sample_rate', 0.05)  # Sample every 20 seconds
        
        super().__init__(sensor_id=sensor_id, **kwargs)
        
        # Pressure-specific properties
        self.altitude = altitude
        self.sea_level_pressure = sea_level_pressure
        self.weather_variability = max(0.0, min(1.0, weather_variability))
        self.measurement_type = measurement_type
        
        # Calculate base pressure at altitude using barometric formula
        self.base_pressure = self._calculate_pressure_at_altitude(
            self.sea_level_pressure, self.altitude
        )
        
        # Internal state for weather patterns
        self._weather_pressure_offset = 0.0
        self._weather_trend = 0.0  # Rising/falling pressure trend
        self._last_weather_update = datetime.now()
        self._pressure_history = []  # For trend calculation
        
        # Australian city altitude references
        self._city_altitudes = {
            'sydney': 19,
            'melbourne': 31,
            'brisbane': 27,
            'perth': 46,
            'adelaide': 50,
            'darwin': 30,
            'hobart': 51,
            'canberra': 580,
            'alice springs': 545,
            'cairns': 3
        }
    
    def _calculate_pressure_at_altitude(self, sea_level_pressure: float, altitude: float) -> float:
        """
        Calculate atmospheric pressure at given altitude using barometric formula.
        
        Args:
            sea_level_pressure: Pressure at sea level in hPa
            altitude: Altitude in metres
            
        Returns:
            Pressure at altitude in hPa
        """
        # Barometric formula constants
        temp_lapse_rate = 0.0065  # K/m
        gas_constant = 287.05     # J/(kg·K)
        gravity = 9.80665         # m/s²
        sea_level_temp = 288.15   # K (15°C)
        
        # Calculate pressure using barometric formula
        exponent = (gravity * temp_lapse_rate) / (gas_constant * temp_lapse_rate)
        pressure_ratio = (1 - (temp_lapse_rate * altitude) / sea_level_temp) ** (gravity / (gas_constant * temp_lapse_rate))
        
        return sea_level_pressure * pressure_ratio
    
    def _update_weather_patterns(self, timestamp: datetime) -> None:
        """
        Update weather-related pressure patterns.
        
        Simulates the passage of weather systems (high/low pressure systems)
        that cause realistic pressure variations over time.
        """
        time_since_update = timestamp - self._last_weather_update
        
        # Update weather patterns every 1-6 hours
        update_interval = timedelta(hours=np.random.uniform(1, 6))
        
        if time_since_update > update_interval:
            # Generate new weather system influence
            # Weather systems can cause ±30 hPa variations
            weather_base_change = np.random.normal(0, 10) * self.weather_variability
            
            # Add trend component (pressure rising/falling over time)
            trend_change = np.random.normal(0, 2) * self.weather_variability
            self._weather_trend = max(-5, min(5, self._weather_trend + trend_change))
            
            self._weather_pressure_offset = weather_base_change
            self._last_weather_update = timestamp
    
    def _calculate_atmospheric_tide(self, timestamp: datetime) -> float:
        """
        Calculate atmospheric tidal effects using lunar and solar influences.
        
        Atmospheric pressure varies with lunar and solar gravitational effects,
        creating predictable semi-diurnal oscillations.
        """
        hour = timestamp.hour + timestamp.minute / 60.0
        day_of_year = timestamp.timetuple().tm_yday
        
        # Semi-diurnal atmospheric tide (two peaks per day)
        # Primary component: solar heating creates 12-hour cycle
        solar_tide = 0.8 * math.cos(2 * math.pi * hour / 12)
        
        # Secondary component: lunar gravitational effect (24.8-hour cycle)
        lunar_phase = (day_of_year * 24 + hour) / 24.8  # Approximate lunar day
        lunar_tide = 0.2 * math.cos(2 * math.pi * lunar_phase)
        
        return solar_tide + lunar_tide
    
    def _simulate_weather_front(self, timestamp: datetime) -> float:
        """
        Simulate the passage of weather fronts causing rapid pressure changes.
        
        Weather fronts can cause significant pressure drops or rises
        over short periods.
        """
        # Random chance of weather front passage (low probability)
        if np.random.random() < 0.001:  # 0.1% chance per reading
            # Simulate pressure drop/rise from weather front
            front_intensity = np.random.uniform(-15, 10)  # Usually pressure drops
            return front_intensity * self.weather_variability
        
        return 0.0
    
    def _apply_weather_trend(self, timestamp: datetime) -> float:
        """
        Apply gradual weather trend (pressure rising/falling over hours).
        """
        # Trend is applied as a function of time
        hours_since_midnight = timestamp.hour + timestamp.minute / 60.0
        trend_effect = self._weather_trend * (hours_since_midnight / 24.0)
        
        return trend_effect
    
    def _generate_base_value(self, timestamp: datetime) -> float:
        """
        Generate the base pressure value for the given timestamp.
        
        Combines all pressure influences:
        - Base pressure at altitude
        - Weather system influences
        - Diurnal variations
        - Weather front effects
        - Gradual weather trends
        """
        # Update weather patterns
        self._update_weather_patterns(timestamp)
        
        # Start with base pressure at altitude
        pressure = self.base_pressure
        
        # Add weather system influence
        pressure += self._weather_pressure_offset
        
        # Add atmospheric tidal effects
        pressure += self._calculate_atmospheric_tide(timestamp)
        
        # Add weather front effects
        pressure += self._simulate_weather_front(timestamp)
        
        # Add weather trend
        pressure += self._apply_weather_trend(timestamp)
        
        # Store in history for trend analysis
        self._pressure_history.append((timestamp, pressure))
        
        # Keep only recent history (last 24 hours worth)
        cutoff_time = timestamp - timedelta(hours=24)
        self._pressure_history = [
            (t, p) for t, p in self._pressure_history if t > cutoff_time
        ]
        
        return pressure
    
    def set_altitude(self, altitude: float) -> None:
        """
        Change the sensor altitude and recalculate base pressure.
        
        Args:
            altitude: New altitude in metres above sea level
        """
        self.altitude = altitude
        self.base_pressure = self._calculate_pressure_at_altitude(
            self.sea_level_pressure, self.altitude
        )
    
    def set_location_by_city(self, city: str) -> None:
        """
        Set sensor location using predefined Australian city altitudes.
        
        Args:
            city: City name (e.g., 'sydney', 'melbourne', 'canberra')
        """
        city_key = city.lower()
        if city_key in self._city_altitudes:
            self.set_altitude(self._city_altitudes[city_key])
            print(f"Set location to {city.title()}, altitude: {self.altitude}m")
        else:
            available_cities = ', '.join(self._city_altitudes.keys())
            print(f"Unknown city. Available cities: {available_cities}")
    
    def simulate_weather_system(self, system_type: str, intensity: float = 1.0) -> None:
        """
        Manually simulate a specific weather system.
        
        Args:
            system_type: Type of weather system ('high', 'low', 'front_cold', 'front_warm')
            intensity: Intensity of the weather system (0.5-2.0)
        """
        weather_effects = {
            'high': 15.0,          # High pressure system
            'low': -20.0,          # Low pressure system (storm)
            'front_cold': -12.0,   # Cold front passage
            'front_warm': -5.0,    # Warm front passage
            'cyclone': -40.0,      # Cyclone (extreme low pressure)
            'anticyclone': 25.0    # Strong high pressure
        }
        
        base_effect = weather_effects.get(system_type.lower(), 0.0)
        self._weather_pressure_offset = base_effect * intensity * self.weather_variability
        self._last_weather_update = datetime.now()
        
        print(f"Simulated {system_type} weather system with intensity {intensity}")
    
    def get_pressure_trend(self, hours: float = 3.0) -> Dict[str, Any]:
        """
        Calculate pressure trend over the specified time period.
        
        Args:
            hours: Number of hours to look back for trend calculation
            
        Returns:
            Dictionary with trend information
        """
        if len(self._pressure_history) < 2:
            return {'trend': 0.0, 'rate': 0.0, 'classification': 'steady'}
        
        # Get readings from the specified time period
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_readings = [
            (t, p) for t, p in self._pressure_history if t > cutoff_time
        ]
        
        if len(recent_readings) < 2:
            return {'trend': 0.0, 'rate': 0.0, 'classification': 'steady'}
        
        # Calculate linear trend
        times = [(t - recent_readings[0][0]).total_seconds() / 3600 for t, _ in recent_readings]
        pressures = [p for _, p in recent_readings]
        
        # Simple linear regression for trend
        n = len(times)
        sum_t = sum(times)
        sum_p = sum(pressures)
        sum_tp = sum(t * p for t, p in zip(times, pressures))
        sum_t2 = sum(t * t for t in times)
        
        # Calculate slope (hPa/hour)
        if n * sum_t2 - sum_t * sum_t != 0:
            slope = (n * sum_tp - sum_t * sum_p) / (n * sum_t2 - sum_t * sum_t)
        else:
            slope = 0.0
        
        # Classify trend
        if slope > 1.0:
            classification = 'rising rapidly'
        elif slope > 0.3:
            classification = 'rising'
        elif slope > -0.3:
            classification = 'steady'
        elif slope > -1.0:
            classification = 'falling'
        else:
            classification = 'falling rapidly'
        
        total_change = pressures[-1] - pressures[0] if pressures else 0.0
        
        return {
            'trend': total_change,
            'rate': slope,
            'classification': classification,
            'hours': hours
        }
    
    def get_pressure_info(self) -> Dict[str, Any]:
        """
        Get detailed pressure sensor information.
        
        Returns:
            Dictionary with pressure-specific information
        """
        base_info = self.get_info()
        
        pressure_info = {
            'altitude': self.altitude,
            'sea_level_pressure': self.sea_level_pressure,
            'base_pressure': self.base_pressure,
            'weather_variability': self.weather_variability,
            'measurement_type': self.measurement_type,
            'current_weather_offset': self._weather_pressure_offset,
            'weather_trend': self._weather_trend,
            'supported_cities': list(self._city_altitudes.keys()),
            'pressure_trend': self.get_pressure_trend()
        }
        
        # Merge with base sensor info
        base_info.update(pressure_info)
        return base_info
