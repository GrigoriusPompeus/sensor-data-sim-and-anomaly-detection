#!/usr/bin/env python3
"""
Quick test to verify imports and VS Code Python interpreter
"""

import sys
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

try:
    import numpy as np
    print(f"✅ NumPy imported successfully: {np.__version__}")
except ImportError as e:
    print(f"❌ NumPy import failed: {e}")

try:
    from src.sensors.base_sensor import BaseSensor, SensorReading
    print("✅ BaseSensor imported successfully")
except ImportError as e:
    print(f"❌ BaseSensor import failed: {e}")

try:
    from src.sensors.temperature import TemperatureSensor
    print("✅ TemperatureSensor imported successfully")
except ImportError as e:
    print(f"❌ TemperatureSensor import failed: {e}")

# Test creating a temperature sensor
try:
    temp_sensor = TemperatureSensor(location="Sydney")
    print(f"✅ TemperatureSensor created: {temp_sensor.sensor_id}")
    print(f"   Location: {temp_sensor.location}")
    print(f"   Base temp: {temp_sensor.base_temperature}°C")
except Exception as e:
    print(f"❌ TemperatureSensor creation failed: {e}")

print("\n🎉 All tests completed!")
