"""
Command Line Interface for sensor simulation and analysis.

Author: Grigor Crandon
Date: August 2025
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.data.generator import DataGenerator, SensorNetwork
from src.anomaly.detector import AlertManager
from src.anomaly.rules import RuleBasedDetector
from src.anomaly.statistics import ZScoreDetector
from src.reporting.stats import StatsReporter
from src.reporting.alerts import AlertSummary
from src.reporting.plots import PlotGenerator
from src.sensors.base_sensor import SensorReading
from src.anomaly.detector import Alert


def simulate_command(args):
    """Simulate sensor data and write to NDJSON file."""
    print(f"Simulating {args.duration} seconds of sensor data...")
    
    # Create sensor network
    network = SensorNetwork(
        location=args.location,
        update_interval=args.interval,
        temperature_coupling=True,
        weather_sync=True
    )
    
    # Create data generator
    generator = DataGenerator(network)
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Generate and write data
    readings_count = 0
    with open(args.output, 'w') as f:
        for reading_group in generator.stream_readings():
            # Extract individual sensor readings from the group
            timestamp = reading_group['timestamp']
            
            # Write each sensor reading as a separate NDJSON line
            for sensor_type, reading in reading_group.items():
                if sensor_type != 'timestamp':  # Skip timestamp key
                    # Create NDJSON line for this sensor reading
                    ndjson_data = reading.to_dict()
                    f.write(json.dumps(ndjson_data) + '\n')
                    readings_count += 1
            
            # Check if we've generated enough data
            if readings_count >= args.duration / args.interval * 3:  # 3 sensors per interval
                break
    
    print(f"Generated {readings_count} readings and saved to {args.output}")


def detect_command(args):
    """Read sensor data and detect anomalies, writing alerts to NDJSON."""
    print(f"Detecting anomalies in {args.input}...")
    
    # Setup anomaly detection
    alert_manager = AlertManager()
    
    # Add rule-based detector
    rule_detector = RuleBasedDetector()
    alert_manager.add_detector(rule_detector)
    
    # Add z-score detector
    zscore_detector = ZScoreDetector(
        window_size=args.window_size,
        z_threshold=args.z_threshold
    )
    alert_manager.add_detector(zscore_detector)
    
    # Process readings from NDJSON file
    readings_count = 0
    alerts_count = 0
    
    # Ensure output directory exists
    os.makedirs('out', exist_ok=True)
    
    with open(args.input, 'r') as infile, open(args.output, 'w') as outfile:
        for line in infile:
            try:
                # Parse NDJSON line
                data = json.loads(line.strip())
                
                # Create SensorReading object
                reading = SensorReading(
                    value=data['value'],
                    timestamp=datetime.fromisoformat(data['timestamp']),
                    sensor_id=data.get('sensor_id'),
                    sensor_type=data.get('sensor_type', 'generic'),
                    quality=data.get('quality', 1.0),
                    metadata=data.get('metadata', {})
                )
                
                # Process through detectors
                new_alerts = alert_manager.process_reading(reading)
                
                # Write alerts as NDJSON
                for alert in new_alerts:
                    outfile.write(json.dumps(alert.to_dict()) + '\n')
                    alerts_count += 1
                
                readings_count += 1
                
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Warning: Skipping invalid line: {e}")
                continue
    
    print(f"Processed {readings_count} readings and found {alerts_count} alerts")
    print(f"Alerts saved to {args.output}")


def report_command(args):
    """Generate reports from sensor data and alerts."""
    print(f"Generating reports for {args.data_file}...")
    
    # Load sensor data
    readings = []
    with open(args.data_file, 'r') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                reading = SensorReading(
                    value=data['value'],
                    timestamp=datetime.fromisoformat(data['timestamp']),
                    sensor_id=data.get('sensor_id'),
                    sensor_type=data.get('sensor_type', 'generic'),
                    quality=data.get('quality', 1.0),
                    metadata=data.get('metadata', {})
                )
                readings.append(reading)
            except (json.JSONDecodeError, KeyError, ValueError):
                continue
    
    # Load alerts if available
    alerts = []
    if os.path.exists(args.alerts_file):
        with open(args.alerts_file, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    alert = Alert.from_dict(data)
                    alerts.append(alert)
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
    
    # Generate statistics report
    stats_reporter = StatsReporter()
    stats_reporter.add_readings(readings)
    stats_reporter.print_report()
    
    # Generate alerts summary
    if alerts:
        alert_summary = AlertSummary()
        alert_summary.add_alerts(alerts)
        alert_summary.print_summary()
    else:
        print("\nNo alerts found.")
    
    # Generate plot
    if readings:
        try:
            os.makedirs('out', exist_ok=True)
            plot_generator = PlotGenerator()
            
            if args.plot_sensor:
                # Plot single sensor
                sensor_found = False
                sensor_type = None
                for reading in readings:
                    if reading.sensor_id == args.plot_sensor:
                        sensor_type = reading.sensor_type
                        sensor_found = True
                        break
                
                if sensor_found and sensor_type:
                    plot_path = plot_generator.plot_sensor_timeline(
                        readings=readings,
                        alerts=alerts,
                        sensor_id=args.plot_sensor,
                        sensor_type=sensor_type,
                        output_path='out/plot.png'
                    )
                    print(f"\nSingle sensor plot saved to {plot_path}")
                else:
                    print(f"\nWarning: Sensor '{args.plot_sensor}' not found in data")
            
            # Always generate multi-sensor plot as well
            multi_plot_path = plot_generator.plot_multiple_sensors(
                readings=readings,
                alerts=alerts,
                output_path='out/multi_sensor_plot.png',
                title='All Sensors Timeline with Anomaly Detection'
            )
            print(f"Multi-sensor plot saved to {multi_plot_path}")
                
        except Exception as e:
            print(f"\nWarning: Could not generate plot: {e}")
    else:
        print("\nNo sensor data found for plotting.")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Sensor simulation and anomaly detection toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simulate 60 seconds of data
  python cli.py simulate --duration 60 --output data/readings.ndjson
  
  # Detect anomalies
  python cli.py detect --input data/readings.ndjson --output out/alerts.ndjson
  
  # Generate reports
  python cli.py report --data data/readings.ndjson --alerts out/alerts.ndjson --plot-sensor temp_sydney
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Simulate command
    sim_parser = subparsers.add_parser('simulate', help='Generate sensor data')
    sim_parser.add_argument('--duration', type=int, default=60,
                           help='Simulation duration in seconds (default: 60)')
    sim_parser.add_argument('--interval', type=float, default=1.0,
                           help='Sample interval in seconds (default: 1.0)')
    sim_parser.add_argument('--location', type=str, default='Sydney',
                           help='Simulation location (default: Sydney)')
    sim_parser.add_argument('--output', type=str, default='data/readings.ndjson',
                           help='Output file path (default: data/readings.ndjson)')
    
    # Detect command
    detect_parser = subparsers.add_parser('detect', help='Detect anomalies in sensor data')
    detect_parser.add_argument('--input', type=str, default='data/readings.ndjson',
                              help='Input NDJSON file (default: data/readings.ndjson)')
    detect_parser.add_argument('--output', type=str, default='out/alerts.ndjson',
                              help='Output alerts file (default: out/alerts.ndjson)')
    detect_parser.add_argument('--window-size', type=int, default=10,
                              help='Z-score window size (default: 10)')
    detect_parser.add_argument('--z-threshold', type=float, default=3.0,
                              help='Z-score threshold (default: 3.0)')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate reports and plots')
    report_parser.add_argument('--data', dest='data_file', type=str, default='data/readings.ndjson',
                              help='Input sensor data file (default: data/readings.ndjson)')
    report_parser.add_argument('--alerts', dest='alerts_file', type=str, default='out/alerts.ndjson',
                              help='Input alerts file (default: out/alerts.ndjson)')
    report_parser.add_argument('--plot-sensor', type=str,
                              help='Sensor ID for single sensor plot (optional, multi-sensor plot always generated)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'simulate':
            simulate_command(args)
        elif args.command == 'detect':
            detect_command(args)
        elif args.command == 'report':
            report_command(args)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
