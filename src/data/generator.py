"""
Data Generator

Simple generator for streaming sensor data without storage overhead.
Provides infinite data streams from multiple coordinated sensors.
"""

from typing import Iterator, Dict, List, Optional, Any
from datetime import datetime, timedelta
import time
from dataclasses import dataclass

from ..sensors import TemperatureSensor, PressureSensor, HumiditySensor, SensorReading


@dataclass
class SensorNetwork:
    """Configuration for a network of coordinated sensors."""
    location: str = "Sydney"
    altitude: float = 19.0  # Sydney altitude
    location_type: str = "coastal"
    
    # Sensor coordination settings
    update_interval: float = 1.0  # seconds between readings
    temperature_coupling: bool = True  # Link humidity to temperature
    weather_sync: bool = True  # Synchronise weather across sensors


class DataGenerator:
    """
    Simple data generator for streaming sensor readings.
    
    Creates infinite streams of coordinated sensor data without storing anything.
    Uses generator pattern for memory efficiency.
    """
    
    def __init__(self, network_config: Optional[SensorNetwork] = None):
        """
        Initialise data generator with sensor network configuration.
        
        Args:
            network_config: Configuration for the sensor network
        """
        self.config = network_config or SensorNetwork()
        
        # Create coordinated sensors
        self.temperature_sensor = TemperatureSensor(
            location=self.config.location,
            sensor_id=f"temp_{self.config.location.lower()}"
        )
        
        self.pressure_sensor = PressureSensor(
            altitude=self.config.altitude,
            sensor_id=f"pressure_{self.config.location.lower()}"
        )
        
        self.humidity_sensor = HumiditySensor(
            location_type=self.config.location_type,
            sensor_id=f"humidity_{self.config.location.lower()}"
        )
        
        # Activate all sensors
        self.temperature_sensor.activate()
        self.pressure_sensor.activate()
        self.humidity_sensor.activate()
        
        # Set location-specific configurations
        self._configure_sensors()
    
    def _configure_sensors(self) -> None:
        """Configure sensors with location-specific settings."""
        # Set pressure sensor location if it's a known Australian city
        try:
            self.pressure_sensor.set_location_by_city(self.config.location)
        except:
            pass  # Use default altitude if city not found
    
    def _synchronise_weather(self, weather_condition: str, intensity: float = 1.0) -> None:
        """
        Apply the same weather condition to all sensors for realism.
        
        Args:
            weather_condition: Weather condition to apply
            intensity: Intensity of the weather effect
        """
        if self.config.weather_sync:
            self.temperature_sensor.set_weather_conditions(weather_condition, intensity)
            
            # Map temperature weather to pressure weather
            pressure_weather_map = {
                'sunny': 'high',
                'cloudy': 'front_warm', 
                'rainy': 'low',
                'stormy': 'cyclone',
                'windy': 'front_cold'
            }
            pressure_condition = pressure_weather_map.get(weather_condition, 'high')
            self.pressure_sensor.simulate_weather_system(pressure_condition, intensity)
            
            self.humidity_sensor.set_weather_condition(weather_condition, intensity)
    
    def stream_readings(
        self, 
        duration_seconds: Optional[float] = None,
        start_time: Optional[datetime] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Generate infinite stream of coordinated sensor readings.
        
        Args:
            duration_seconds: Optional duration limit (infinite if None)
            start_time: Starting timestamp (uses current time if None)
            
        Yields:
            Dictionary with sensor readings: {'temperature': reading, 'pressure': reading, 'humidity': reading}
        """
        current_time = start_time or datetime.now()
        end_time = current_time + timedelta(seconds=duration_seconds) if duration_seconds else None
        
        while True:
            # Check if we've reached the duration limit
            if end_time and current_time >= end_time:
                break
            
            # Generate coordinated readings
            temp_reading = self.temperature_sensor.read(current_time)
            pressure_reading = self.pressure_sensor.read(current_time)
            
            # Couple humidity to temperature for realism
            if self.config.temperature_coupling:
                self.humidity_sensor.set_current_temperature(temp_reading.value)
            
            humidity_reading = self.humidity_sensor.read(current_time)
            
            # Yield the coordinated readings
            yield {
                'timestamp': current_time,
                'temperature': temp_reading,
                'pressure': pressure_reading,
                'humidity': humidity_reading
            }
            
            # Advance time
            current_time += timedelta(seconds=self.config.update_interval)
    
    def stream_single_sensor(
        self, 
        sensor_type: str,
        duration_seconds: Optional[float] = None,
        start_time: Optional[datetime] = None
    ) -> Iterator[SensorReading]:
        """
        Generate infinite stream from a single sensor type.
        
        Args:
            sensor_type: Type of sensor ('temperature', 'pressure', 'humidity')
            duration_seconds: Optional duration limit
            start_time: Starting timestamp
            
        Yields:
            Individual sensor readings
        """
        # Get the requested sensor
        sensor_map = {
            'temperature': self.temperature_sensor,
            'pressure': self.pressure_sensor,
            'humidity': self.humidity_sensor
        }
        
        sensor = sensor_map.get(sensor_type.lower())
        if not sensor:
            raise ValueError(f"Unknown sensor type: {sensor_type}")
        
        current_time = start_time or datetime.now()
        end_time = current_time + timedelta(seconds=duration_seconds) if duration_seconds else None
        
        while True:
            if end_time and current_time >= end_time:
                break
            
            # Special handling for humidity to maintain temperature coupling
            if sensor_type.lower() == 'humidity' and self.config.temperature_coupling:
                temp_reading = self.temperature_sensor.read(current_time)
                self.humidity_sensor.set_current_temperature(temp_reading.value)
            
            reading = sensor.read(current_time)
            yield reading
            
            current_time += timedelta(seconds=self.config.update_interval)
    
    def get_sensor_info(self) -> Dict[str, Any]:
        """
        Get information about all sensors in the network.
        
        Returns:
            Dictionary with sensor information
        """
        return {
            'network_config': {
                'location': self.config.location,
                'altitude': self.config.altitude,
                'location_type': self.config.location_type,
                'update_interval': self.config.update_interval,
                'temperature_coupling': self.config.temperature_coupling,
                'weather_sync': self.config.weather_sync
            },
            'sensors': {
                'temperature': self.temperature_sensor.get_temperature_info(),
                'pressure': self.pressure_sensor.get_pressure_info(),
                'humidity': self.humidity_sensor.get_humidity_info()
            }
        }
    
    def set_weather(self, condition: str, intensity: float = 1.0) -> None:
        """
        Set weather conditions for all sensors.
        
        Args:
            condition: Weather condition ('sunny', 'cloudy', 'rainy', 'stormy', 'windy')
            intensity: Weather intensity (0.5-2.0)
        """
        self._synchronise_weather(condition, intensity)
        print(f"Applied {condition} weather (intensity: {intensity}) to sensor network")
    
    def simulate_time_lapse(
        self,
        hours: float = 24.0,
        time_compression: float = 3600.0  # 1 hour per second
    ) -> Iterator[Dict[str, Any]]:
        """
        Simulate accelerated time for quick data generation.
        
        Args:
            hours: Number of hours to simulate
            time_compression: Time compression factor (seconds of real time per second of simulation)
            
        Yields:
            Sensor readings at compressed time intervals
        """
        start_time = datetime.now()
        duration_seconds = hours * 3600  # Convert hours to seconds
        time_step = time_compression  # Seconds to advance per iteration
        
        current_time = start_time
        end_time = start_time + timedelta(seconds=duration_seconds)
        
        while current_time < end_time:
            # Generate readings for the current simulated time
            temp_reading = self.temperature_sensor.read(current_time)
            pressure_reading = self.pressure_sensor.read(current_time)
            
            if self.config.temperature_coupling:
                self.humidity_sensor.set_current_temperature(temp_reading.value)
            
            humidity_reading = self.humidity_sensor.read(current_time)
            
            yield {
                'timestamp': current_time,
                'temperature': temp_reading,
                'pressure': pressure_reading,
                'humidity': humidity_reading
            }
            
            # Advance simulated time
            current_time += timedelta(seconds=time_step)
