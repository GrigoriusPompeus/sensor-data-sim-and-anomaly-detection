#!/usr/bin/env python3
"""
Test extreme temperature scenarios to trigger threshold rules.

Author: Grigor Crandon
Date: August 2025
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.sensors.temperature import TemperatureSensor
from src.anomaly.rules import RuleBasedDetector

def main():
    print("🌡️ Testing Extreme Temperature Scenarios")
    print("=" * 50)
    
    # Create detector
    detector = RuleBasedDetector()
    
    # Create temperature sensor with extreme settings
    sensor = TemperatureSensor(
        sensor_id="extreme_temp_test",
        base_temperature=45.0,  # Very hot base temperature
        noise_level=0.1,
        malfunction_probability=0.0
    )
    
    # Activate the sensor
    sensor.activate()
    
    print("Testing with extreme hot conditions (45°C base temperature)...")
    print()
    
    alerts_found = []
    
    # Generate several readings to test thresholds
    for i in range(20):
        reading = sensor.read()
        alerts = detector.process_reading(reading)
        
        if alerts:
            alerts_found.extend(alerts)
            print(f"🚨 Reading {i+1}: {reading.value:.1f}°C")
            for alert in alerts:
                print(f"   Alert: {alert.rule_name} - {alert.severity.value.upper()}")
                print(f"   Message: {alert.message}")
            print()
        else:
            print(f"✅ Reading {i+1}: {reading.value:.1f}°C (normal)")
    
    print(f"\nSummary: {len(alerts_found)} alerts triggered")
    
    # Show rule effectiveness
    rule_counts = {}
    for alert in alerts_found:
        rule_counts[alert.rule_name] = rule_counts.get(alert.rule_name, 0) + 1
    
    if rule_counts:
        print("\nRules triggered:")
        for rule, count in rule_counts.items():
            print(f"  • {rule}: {count} times")
    else:
        print("❌ No threshold rules triggered - consider adjusting thresholds or test conditions")

if __name__ == "__main__":
    main()
