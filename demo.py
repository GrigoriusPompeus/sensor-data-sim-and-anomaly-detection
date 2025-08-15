#!/usr/bin/env python3
"""
Demo script showing the complete sensor simulation and anomaly detection system.

Author: Grigor Crandon
Date: August 2025
"""

import os
import subprocess
import sys

def run_command(cmd, description):
    """Run a command and print its description."""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"Running: {cmd}")
    print("-" * 40)
    
    result = subprocess.run(cmd, shell=True, capture_output=False)
    if result.returncode != 0:
        print(f"❌ Command failed with exit code {result.returncode}")
        return False
    print("✅ Command completed successfully")
    return True

def main():
    """Run the complete demo workflow."""
    print("🚀 SENSOR SIMULATION & ANOMALY DETECTION SYSTEM DEMO")
    print("=" * 60)
    
    # Change to the correct directory
    os.chdir("/Users/grigorcrandon/sensor-sim")
    
    # Clean up any existing files
    if os.path.exists("data/readings.ndjson"):
        os.remove("data/readings.ndjson")
    if os.path.exists("out/alerts.ndjson"):
        os.remove("out/alerts.ndjson")
    if os.path.exists("out/plot.png"):
        os.remove("out/plot.png")
    
    # Step 1: Simulate sensor data
    success = run_command(
        "python cli.py simulate --duration 60 --interval 0.5 --location Brisbane",
        "STEP 1: Simulating 60 seconds of sensor data from Brisbane"
    )
    if not success:
        return 1
    
    # Step 2: Detect anomalies
    success = run_command(
        "python cli.py detect --input data/readings.ndjson --window-size 15 --z-threshold 2.5",
        "STEP 2: Detecting anomalies with z-score threshold 2.5"
    )
    if not success:
        return 1
    
    # Step 3: Generate reports
    success = run_command(
        "python cli.py report --data data/readings.ndjson --alerts out/alerts.ndjson",
        "STEP 3: Generating statistical reports and multi-sensor plots"
    )
    if not success:
        return 1
    
    # Show file sizes
    print(f"\n{'='*60}")
    print("📁 GENERATED FILES")
    print(f"{'='*60}")
    
    for file_path in ["data/readings.ndjson", "out/alerts.ndjson", "out/multi_sensor_plot.png"]:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path:<30} {size:>8} bytes")
        else:
            print(f"❌ {file_path:<30} NOT FOUND")
    
    print(f"\n{'='*60}")
    print("🎉 DEMO COMPLETED SUCCESSFULLY!")
    print(f"{'='*60}")
    print("""
Key Features Demonstrated:
• ✅ Physics-based sensor simulation (temperature, pressure, humidity)
• ✅ Rule-based anomaly detection (threshold violations)  
• ✅ Statistical anomaly detection (rolling z-scores)
• ✅ Comprehensive reporting (statistics, alerts, plots)
• ✅ NDJSON data format for streaming processing
• ✅ Command-line interface for easy integration

Next Steps:
• Open out/multi_sensor_plot.png to view all sensors with alert markers
• Open out/plot.png for single sensor detailed view (if --plot-sensor specified)
• Examine data/readings.ndjson for the raw sensor data
• Review out/alerts.ndjson for detected anomalies
""")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
