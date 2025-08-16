"""
Statistical reporting for sensor data.
"""

from typing import List, Dict, Any
from collections import defaultdict
import statistics

from ..sensors.base_sensor import SensorReading
from ..anomaly.detector import Alert


class SensorStats:
    """Statistical summary for a single sensor."""
    
    def __init__(self, sensor_id: str, sensor_type: str):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.values: List[float] = []
        self.count = 0
        self.mean = 0.0
        self.min_val = float('inf')
        self.max_val = float('-inf')
        self.stdev = 0.0
    
    def add_reading(self, reading: SensorReading):
        """Add a reading to the statistics."""
        if not (reading.value == reading.value):  # Skip NaN values
            return
        
        self.values.append(reading.value)
        self.count += 1
        self.min_val = min(self.min_val, reading.value)
        self.max_val = max(self.max_val, reading.value)
    
    def calculate(self):
        """Calculate final statistics."""
        if not self.values:
            return
        
        self.mean = statistics.mean(self.values)
        if len(self.values) > 1:
            self.stdev = statistics.stdev(self.values)
        
        # Handle edge case where no values were added
        if self.min_val == float('inf'):
            self.min_val = 0.0
        if self.max_val == float('-inf'):
            self.max_val = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            'sensor_id': self.sensor_id,
            'sensor_type': self.sensor_type,
            'count': self.count,
            'mean': round(self.mean, 3) if self.count > 0 else 0.0,
            'min': round(self.min_val, 3) if self.count > 0 else 0.0,
            'max': round(self.max_val, 3) if self.count > 0 else 0.0,
            'stdev': round(self.stdev, 3) if self.count > 1 else 0.0
        }


class StatsReporter:
    """Generate statistical reports for sensor data."""
    
    def __init__(self):
        self.sensor_stats: Dict[str, SensorStats] = {}
        self.readings_processed = 0
    
    def _get_sensor_key(self, reading: SensorReading) -> str:
        """Get unique key for sensor."""
        return f"{reading.sensor_type}_{reading.sensor_id}"
    
    def add_reading(self, reading: SensorReading):
        """Add a reading to the statistics."""
        sensor_key = self._get_sensor_key(reading)
        
        if sensor_key not in self.sensor_stats:
            self.sensor_stats[sensor_key] = SensorStats(
                reading.sensor_id or "unknown",
                reading.sensor_type
            )
        
        self.sensor_stats[sensor_key].add_reading(reading)
        self.readings_processed += 1
    
    def add_readings(self, readings: List[SensorReading]):
        """Add multiple readings."""
        for reading in readings:
            self.add_reading(reading)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive statistics report."""
        # Calculate final statistics for all sensors
        for stats in self.sensor_stats.values():
            stats.calculate()
        
        # Group by sensor type
        by_type = defaultdict(list)
        for stats in self.sensor_stats.values():
            by_type[stats.sensor_type].append(stats.to_dict())
        
        return {
            'summary': {
                'total_readings': self.readings_processed,
                'unique_sensors': len(self.sensor_stats),
                'sensor_types': list(by_type.keys())
            },
            'by_sensor_type': dict(by_type),
            'all_sensors': [stats.to_dict() for stats in self.sensor_stats.values()]
        }
    
    def print_report(self, location: str = "Unknown"):
        """Print formatted statistics report to console."""
        report = self.generate_report()
        
        print("\n" + "="*60)
        print("SENSOR STATISTICS REPORT")
        print("="*60)
        print(f"Location: {location}")
        
        summary = report['summary']
        print(f"Total Readings: {summary['total_readings']:,}")
        print(f"Unique Sensors: {summary['unique_sensors']}")
        print(f"Sensor Types: {', '.join(summary['sensor_types'])}")
        
        print("\nDetailed Statistics by Sensor:")
        print("-" * 80)
        print(f"{'Sensor ID':<15} {'Type':<12} {'Count':<8} {'Mean':<10} {'Min':<10} {'Max':<10} {'StdDev':<8}")
        print("-" * 80)
        
        for sensor_data in report['all_sensors']:
            print(f"{sensor_data['sensor_id']:<15} "
                  f"{sensor_data['sensor_type']:<12} "
                  f"{sensor_data['count']:<8} "
                  f"{sensor_data['mean']:<10.2f} "
                  f"{sensor_data['min']:<10.2f} "
                  f"{sensor_data['max']:<10.2f} "
                  f"{sensor_data['stdev']:<8.2f}")
        
        print("-" * 80)
    
    def get_sensor_summary(self, sensor_type: str) -> Dict[str, Any]:
        """Get summary for a specific sensor type."""
        report = self.generate_report()
        return report['by_sensor_type'].get(sensor_type, [])
    
    def reset(self):
        """Reset all statistics."""
        self.sensor_stats.clear()
        self.readings_processed = 0
