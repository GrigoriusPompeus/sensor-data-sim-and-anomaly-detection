"""
Rule-based anomaly detection with configurable thresholds.
"""

from typing import List, Dict, Callable, Any
from dataclasses import dataclass

from .detector import AnomalyDetector, Alert, AlertSeverity
from ..sensors.base_sensor import SensorReading


@dataclass
class ThresholdRule:
    """Defines a threshold-based rule for anomaly detection."""
    name: str
    sensor_type: str
    condition: Callable[[float], bool]
    threshold: float
    severity: AlertSeverity
    message_template: str
    
    def check(self, reading: SensorReading) -> bool:
        """Check if reading violates this rule."""
        if reading.sensor_type != self.sensor_type:
            return False
        return self.condition(reading.value)
    
    def create_alert(self, reading: SensorReading) -> Alert:
        """Create an alert for this rule violation."""
        sensor_id = reading.sensor_id or "unknown_sensor"
        message = self.message_template.format(
            value=reading.value,
            threshold=self.threshold,
            sensor_id=sensor_id
        )
        
        return Alert(
            timestamp=reading.timestamp,
            sensor_id=sensor_id,
            sensor_type=reading.sensor_type,
            rule_name=self.name,
            severity=self.severity,
            value=reading.value,
            threshold=self.threshold,
            message=message,
            metadata={'rule_type': 'threshold'}
        )


class RuleBasedDetector(AnomalyDetector):
    """Rule-based anomaly detector with configurable thresholds."""
    
    def __init__(self):
        super().__init__("rule_based")
        self.rules: List[ThresholdRule] = []
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default threshold rules for common sensor types."""
        
        # Temperature rules (realistic for Australian environmental conditions)
        self.add_rule(ThresholdRule(
            name="temp_very_low",
            sensor_type="temperature",
            condition=lambda x: x < -5.0,
            threshold=-5.0,
            severity=AlertSeverity.HIGH,
            message_template="Temperature very low: {value:.1f}°C < {threshold:.1f}°C on {sensor_id} - possible frost conditions"
        ))
        
        self.add_rule(ThresholdRule(
            name="temp_very_high",
            sensor_type="temperature",
            condition=lambda x: x > 35.0,
            threshold=35.0,
            severity=AlertSeverity.HIGH,
            message_template="Temperature very high: {value:.1f}°C > {threshold:.1f}°C on {sensor_id} - extreme heat warning"
        ))
        
        self.add_rule(ThresholdRule(
            name="temp_extreme_high",
            sensor_type="temperature",
            condition=lambda x: x > 30.0,
            threshold=30.0,
            severity=AlertSeverity.MEDIUM,
            message_template="High temperature: {value:.1f}°C > {threshold:.1f}°C on {sensor_id} - hot weather conditions"
        ))
        
        # Pressure rules
        self.add_rule(ThresholdRule(
            name="pressure_very_low",
            sensor_type="pressure",
            condition=lambda x: x < 950.0,
            threshold=950.0,
            severity=AlertSeverity.MEDIUM,
            message_template="Atmospheric pressure very low: {value:.1f} hPa < {threshold:.1f} hPa on {sensor_id}"
        ))
        
        self.add_rule(ThresholdRule(
            name="pressure_very_high",
            sensor_type="pressure",
            condition=lambda x: x > 1050.0,
            threshold=1050.0,
            severity=AlertSeverity.MEDIUM,
            message_template="Atmospheric pressure very high: {value:.1f} hPa > {threshold:.1f} hPa on {sensor_id}"
        ))
        
        # Humidity rules
        self.add_rule(ThresholdRule(
            name="humidity_impossible_low",
            sensor_type="humidity",
            condition=lambda x: x < 0.0,
            threshold=0.0,
            severity=AlertSeverity.CRITICAL,
            message_template="Humidity below 0%: {value:.1f}% on {sensor_id} - sensor malfunction"
        ))
        
        self.add_rule(ThresholdRule(
            name="humidity_impossible_high",
            sensor_type="humidity",
            condition=lambda x: x > 100.0,
            threshold=100.0,
            severity=AlertSeverity.CRITICAL,
            message_template="Humidity above 100%: {value:.1f}% on {sensor_id} - sensor malfunction"
        ))
    
    def add_rule(self, rule: ThresholdRule):
        """Add a new threshold rule."""
        self.rules.append(rule)
    
    def remove_rule(self, rule_name: str):
        """Remove a rule by name."""
        self.rules = [r for r in self.rules if r.name != rule_name]
    
    def process_reading(self, reading: SensorReading) -> List[Alert]:
        """Process reading against all applicable rules."""
        alerts = []
        
        for rule in self.rules:
            if rule.check(reading):
                alert = rule.create_alert(reading)
                alerts.append(alert)
        
        return alerts
    
    def get_rules_for_sensor_type(self, sensor_type: str) -> List[ThresholdRule]:
        """Get all rules for a specific sensor type."""
        return [rule for rule in self.rules if rule.sensor_type == sensor_type]
    
    def list_rules(self) -> Dict[str, Any]:
        """List all rules with their configurations."""
        return {
            rule.name: {
                'sensor_type': rule.sensor_type,
                'threshold': rule.threshold,
                'severity': rule.severity.value,
                'message_template': rule.message_template
            }
            for rule in self.rules
        }
