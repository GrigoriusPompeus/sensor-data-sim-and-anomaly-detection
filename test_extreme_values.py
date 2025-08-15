#!/usr/bin/env python3
"""
Test extreme sensor values to trigger threshold-based anomaly detection.

Author: Grigor Crandon
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime
from src.sensors.base_sensor import SensorReading
from src.anomaly.detector import AlertManager
from src.anomaly.rules import RuleBasedDetector
from src.anomaly.statistics import ZScoreDetector

def test_extreme_values():
    """Test with extreme sensor values to trigger threshold alerts."""
    
    print("🧪 Testing Extreme Values for Threshold Alerts")
    print("=" * 60)
    
    # Setup detectors
    alert_manager = AlertManager()
    rule_detector = RuleBasedDetector()
    zscore_detector = ZScoreDetector(window_size=5, z_threshold=2.0)
    
    alert_manager.add_detector(rule_detector)
    alert_manager.add_detector(zscore_detector)
    
    # Test cases with extreme values
    test_cases = [
        # Normal values first (to build z-score baseline)
        SensorReading(23.0, datetime.now(), "test_temp", "temperature", 0.99),
        SensorReading(1013.0, datetime.now(), "test_pressure", "pressure", 0.99),
        SensorReading(65.0, datetime.now(), "test_humidity", "humidity", 0.99),
        SensorReading(24.0, datetime.now(), "test_temp", "temperature", 0.99),
        SensorReading(1012.0, datetime.now(), "test_pressure", "pressure", 0.99),
        
        # Threshold violations
        SensorReading(115.0, datetime.now(), "test_temp", "temperature", 0.99),  # Very high temp
        SensorReading(-45.0, datetime.now(), "test_temp", "temperature", 0.99),  # Temp very low
        SensorReading(65.0, datetime.now(), "test_temp", "temperature", 0.99),   # Temp very high
        SensorReading(940.0, datetime.now(), "test_pressure", "pressure", 0.99), # Pressure very low
        SensorReading(1060.0, datetime.now(), "test_pressure", "pressure", 0.99), # Pressure very high
        SensorReading(-5.0, datetime.now(), "test_humidity", "humidity", 0.99),   # Humidity impossible low
        SensorReading(105.0, datetime.now(), "test_humidity", "humidity", 0.99),  # Humidity impossible high
    ]
    
    print("Processing readings and detecting anomalies...\n")
    
    for i, reading in enumerate(test_cases):
        alerts = alert_manager.process_reading(reading)
        
        if alerts:
            print(f"Reading {i+1:2d}: {reading.sensor_type:12} = {reading.value:6.1f}")
            for alert in alerts:
                severity_icon = {
                    'low': '🟡', 'medium': '🟠', 'high': '🔴', 'critical': '🚨'
                }
                icon = severity_icon.get(alert.severity.value, '⚪')
                print(f"    {icon} {alert.severity.value.upper():8} | {alert.rule_name:15} | {alert.message}")
        else:
            print(f"Reading {i+1:2d}: {reading.sensor_type:12} = {reading.value:6.1f} ✅ Normal")
    
    # Summary
    all_alerts = alert_manager.get_all_alerts()
    print(f"\n📊 Summary:")
    print(f"   Total readings processed: {len(test_cases)}")
    print(f"   Total alerts generated: {len(all_alerts)}")
    
    # Count by severity
    severity_counts = {}
    for alert in all_alerts:
        severity = alert.severity.value
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    print("   Alerts by severity:")
    for severity, count in severity_counts.items():
        print(f"     {severity.capitalize():8}: {count}")

if __name__ == "__main__":
    test_extreme_values()
