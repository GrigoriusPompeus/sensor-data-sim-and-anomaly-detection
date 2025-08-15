#!/usr/bin/env python3
"""
Test all implemented sensors to verify functionality
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.sensors import TemperatureSensor, PressureSensor, HumiditySensor
from datetime import datetime

def test_temperature_sensor():
    print("🌡️  Testing Temperature Sensor")
    print("-" * 40)
    
    temp_sensor = TemperatureSensor(location="Sydney")
    temp_sensor.activate()
    
    print(f"Sensor ID: {temp_sensor.sensor_id}")
    print(f"Location: {temp_sensor.location}")
    print(f"Base Temperature: {temp_sensor.base_temperature}°C")
    
    # Take a few readings
    for i in range(3):
        reading = temp_sensor.read()
        print(f"Reading {i+1}: {reading.value:.1f}°C (Quality: {reading.quality:.2f})")
    
    # Test weather conditions
    temp_sensor.set_weather_conditions("rainy", intensity=1.5)
    reading = temp_sensor.read()
    print(f"After rain: {reading.value:.1f}°C")
    
    print()

def test_pressure_sensor():
    print("🌪️  Testing Pressure Sensor") 
    print("-" * 40)
    
    pressure_sensor = PressureSensor(altitude=50)  # Adelaide altitude
    pressure_sensor.activate()
    
    print(f"Sensor ID: {pressure_sensor.sensor_id}")
    print(f"Altitude: {pressure_sensor.altitude}m")
    print(f"Base Pressure: {pressure_sensor.base_pressure:.1f} hPa")
    
    # Take a few readings
    for i in range(3):
        reading = pressure_sensor.read()
        print(f"Reading {i+1}: {reading.value:.1f} hPa (Quality: {reading.quality:.2f})")
    
    # Test weather system
    pressure_sensor.simulate_weather_system("low", intensity=1.2)
    reading = pressure_sensor.read()
    print(f"After low pressure system: {reading.value:.1f} hPa")
    
    # Test pressure trend
    trend = pressure_sensor.get_pressure_trend()
    print(f"Pressure trend: {trend['classification']}")
    
    print()

def test_humidity_sensor():
    print("💧 Testing Humidity Sensor")
    print("-" * 40)
    
    humidity_sensor = HumiditySensor(location_type="coastal")
    humidity_sensor.activate()
    humidity_sensor.set_current_temperature(25.0)
    
    print(f"Sensor ID: {humidity_sensor.sensor_id}")
    print(f"Location Type: {humidity_sensor.location_type}")
    print(f"Base Humidity: {humidity_sensor.base_humidity}%")
    
    # Take a few readings
    for i in range(3):
        reading = humidity_sensor.read()
        print(f"Reading {i+1}: {reading.value:.1f}%RH (Quality: {reading.quality:.2f})")
    
    # Test weather conditions
    humidity_sensor.set_weather_condition("rainy", intensity=1.8)
    reading = humidity_sensor.read()
    print(f"After rain: {reading.value:.1f}%RH")
    
    # Test humidity analysis
    analysis = humidity_sensor.get_humidity_analysis(25.0)
    print(f"Dew Point: {analysis['dew_point']}°C")
    print(f"Absolute Humidity: {analysis['absolute_humidity']} g/m³")
    print(f"Comfort: {analysis['comfort_assessment']}")
    
    print()

def test_sensor_integration():
    print("🔗 Testing Sensor Integration")
    print("-" * 40)
    
    # Create all sensors for the same location
    temp_sensor = TemperatureSensor(location="Melbourne")
    pressure_sensor = PressureSensor()
    pressure_sensor.set_location_by_city("Melbourne")
    humidity_sensor = HumiditySensor(location_type="urban")
    
    # Activate all sensors
    for sensor in [temp_sensor, pressure_sensor, humidity_sensor]:
        sensor.activate()
    
    print("Environmental Station - Melbourne")
    
    # Take coordinated readings
    temp_reading = temp_sensor.read()
    pressure_reading = pressure_sensor.read()
    
    # Set humidity sensor temperature based on temperature sensor
    humidity_sensor.set_current_temperature(temp_reading.value)
    humidity_reading = humidity_sensor.read()
    
    print(f"Temperature: {temp_reading.value:.1f}°C")
    print(f"Pressure: {pressure_reading.value:.1f} hPa")
    print(f"Humidity: {humidity_reading.value:.1f}%RH")
    
    # Calculate dew point with actual readings
    dew_point = humidity_sensor.calculate_dew_point(
        humidity_reading.value, temp_reading.value
    )
    print(f"Dew Point: {dew_point:.1f}°C")
    
    print()

if __name__ == "__main__":
    print("🧪 Sensor Simulation Test Suite")
    print("=" * 50)
    print()
    
    try:
        test_temperature_sensor()
        test_pressure_sensor()
        test_humidity_sensor()
        test_sensor_integration()
        
        print("✅ All sensor tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
