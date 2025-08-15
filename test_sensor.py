#!/usr/bin/env python3
"""
Quick test script to verify temperature sensor functionality
"""

from src.sensors.temperature import TemperatureSensor
from datetime import datetime

def test_temperature_sensor():
    """Test basic temperature sensor functionality."""
    print("Testing TemperatureSensor...")
    
    # Create a temperature sensor for Sydney
    sensor = TemperatureSensor(
        location="Sydney",
        base_temperature=20.0,
        daily_range=8.0
    )
    
    print(f"Created sensor: {sensor}")
    print(f"Location: {sensor.location}")
    print(f"Base temperature: {sensor.base_temperature}°C")
    
    # Activate sensor and take a reading
    sensor.activate()
    reading = sensor.read()
    
    print(f"Reading: {reading.value:.2f}°C at {reading.timestamp}")
    print(f"Quality: {reading.quality:.2f}")
    
    # Test weather influence
    sensor.set_weather_conditions("rainy", intensity=1.5)
    reading2 = sensor.read()
    print(f"After rain: {reading2.value:.2f}°C")
    
    print("✅ Temperature sensor test passed!")

if __name__ == "__main__":
    test_temperature_sensor()
