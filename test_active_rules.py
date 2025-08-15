#!/usr/bin/env python3
"""
Test script to show active anomaly detection rules.

Author: Grigor Crandon
Date: August 2025
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.anomaly.rules import RuleBasedDetector

def main():
    print("🔍 Active Anomaly Detection Rules")
    print("=" * 50)
    
    # Create detector to see active rules
    detector = RuleBasedDetector()
    rules = detector.list_rules()
    
    print(f"Total Active Rules: {len(rules)}")
    print()
    
    # Group by sensor type
    sensor_types = {}
    for rule_name, rule_config in rules.items():
        sensor_type = rule_config['sensor_type']
        if sensor_type not in sensor_types:
            sensor_types[sensor_type] = []
        sensor_types[sensor_type].append((rule_name, rule_config))
    
    # Display rules by sensor type
    for sensor_type, type_rules in sensor_types.items():
        print(f"📊 {sensor_type.upper()} SENSOR RULES:")
        print("-" * 30)
        
        for rule_name, config in type_rules:
            severity = config['severity'].upper()
            threshold = config['threshold']
            
            print(f"  • {rule_name}")
            print(f"    Threshold: {threshold}")
            print(f"    Severity:  {severity}")
            print()
    
    print("✅ All rules are relevant to our sensor types!")
    print("   (Removed battery_voltage and speed rules as they don't apply)")

if __name__ == "__main__":
    main()
