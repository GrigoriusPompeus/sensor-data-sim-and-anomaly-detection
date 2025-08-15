"""
Statistical anomaly detection using rolling z-scores.
"""

from typing import List, Dict, Deque
from collections import deque
import statistics
import math

from .detector import AnomalyDetector, Alert, AlertSeverity
from ..sensors.base_sensor import SensorReading


class SensorWindow:
    """Rolling window for sensor readings with statistical calculations."""
    
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.values: Deque[float] = deque(maxlen=window_size)
        self.timestamps: Deque = deque(maxlen=window_size)
    
    def add_reading(self, reading: SensorReading):
        """Add a new reading to the window."""
        self.values.append(reading.value)
        self.timestamps.append(reading.timestamp)
    
    def get_z_score(self, value: float) -> float:
        """Calculate z-score for a value based on current window."""
        if len(self.values) < 2:
            return 0.0
        
        try:
            mean = statistics.mean(self.values)
            stdev = statistics.stdev(self.values)
            
            if stdev == 0:
                return 0.0
            
            return abs(value - mean) / stdev
        except statistics.StatisticsError:
            return 0.0
    
    def get_statistics(self) -> Dict[str, float]:
        """Get current window statistics."""
        if not self.values:
            return {'count': 0, 'mean': 0.0, 'stdev': 0.0, 'min': 0.0, 'max': 0.0}
        
        return {
            'count': len(self.values),
            'mean': statistics.mean(self.values),
            'stdev': statistics.stdev(self.values) if len(self.values) > 1 else 0.0,
            'min': min(self.values),
            'max': max(self.values)
        }
    
    def is_full(self) -> bool:
        """Check if window is full."""
        return len(self.values) >= self.window_size


class ZScoreDetector(AnomalyDetector):
    """Rolling z-score anomaly detector with configurable thresholds."""
    
    def __init__(self, window_size: int = 10, z_threshold: float = 3.0):
        super().__init__("z_score")
        self.window_size = window_size
        self.z_threshold = z_threshold
        self.sensor_windows: Dict[str, SensorWindow] = {}
    
    def _get_sensor_key(self, reading: SensorReading) -> str:
        """Get unique key for sensor."""
        return f"{reading.sensor_type}_{reading.sensor_id}"
    
    def _get_severity_from_z_score(self, z_score: float) -> AlertSeverity:
        """Determine alert severity based on z-score magnitude."""
        if z_score >= 5.0:
            return AlertSeverity.CRITICAL
        elif z_score >= 4.0:
            return AlertSeverity.HIGH
        elif z_score >= 3.0:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW
    
    def process_reading(self, reading: SensorReading) -> List[Alert]:
        """Process reading and detect z-score anomalies."""
        alerts = []
        sensor_key = self._get_sensor_key(reading)
        
        # Get or create window for this sensor
        if sensor_key not in self.sensor_windows:
            self.sensor_windows[sensor_key] = SensorWindow(self.window_size)
        
        window = self.sensor_windows[sensor_key]
        
        # Calculate z-score before adding new reading
        if window.is_full():
            z_score = window.get_z_score(reading.value)
            
            if z_score >= self.z_threshold:
                severity = self._get_severity_from_z_score(z_score)
                stats = window.get_statistics()
                
                message = (
                    f"Statistical anomaly detected: {reading.sensor_type} value {reading.value:.2f} "
                    f"has z-score {z_score:.2f} (threshold: {self.z_threshold:.1f}) on {reading.sensor_id}. "
                    f"Window mean: {stats['mean']:.2f}, stdev: {stats['stdev']:.2f}"
                )
                
                alert = Alert(
                    timestamp=reading.timestamp,
                    sensor_id=reading.sensor_id or "unknown",
                    sensor_type=reading.sensor_type,
                    rule_name=f"z_score_{self.z_threshold}",
                    severity=severity,
                    value=reading.value,
                    threshold=self.z_threshold,
                    message=message,
                    metadata={
                        'rule_type': 'z_score',
                        'z_score': z_score,
                        'window_size': self.window_size,
                        'window_stats': stats
                    }
                )
                alerts.append(alert)
        
        # Add reading to window
        window.add_reading(reading)
        
        return alerts
    
    def get_sensor_statistics(self, sensor_type: str, sensor_id: str) -> Dict[str, float]:
        """Get current statistics for a specific sensor."""
        sensor_key = f"{sensor_type}_{sensor_id}"
        if sensor_key in self.sensor_windows:
            return self.sensor_windows[sensor_key].get_statistics()
        return {}
    
    def reset(self):
        """Reset all sensor windows and alerts."""
        super().reset()
        self.sensor_windows.clear()
    
    def list_monitored_sensors(self) -> List[str]:
        """List all sensors currently being monitored."""
        return list(self.sensor_windows.keys())
