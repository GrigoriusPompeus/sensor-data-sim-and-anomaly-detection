"""
Alert reporting and summarisation.
"""

from typing import List, Dict, Any
from collections import defaultdict, Counter

from ..anomaly.detector import Alert, AlertSeverity


class AlertSummary:
    """Generate summaries and reports for alerts."""
    
    def __init__(self):
        self.alerts: List[Alert] = []
    
    def add_alert(self, alert: Alert):
        """Add an alert to the summary."""
        self.alerts.append(alert)
    
    def add_alerts(self, alerts: List[Alert]):
        """Add multiple alerts."""
        self.alerts.extend(alerts)
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive alert summary."""
        if not self.alerts:
            return {
                'total_alerts': 0,
                'by_severity': {},
                'by_rule': {},
                'by_sensor_type': {},
                'by_sensor_id': {},
                'timeline': []
            }
        
        # Count by severity
        severity_counts = Counter(alert.severity.value for alert in self.alerts)
        
        # Count by rule
        rule_counts = Counter(alert.rule_name for alert in self.alerts)
        
        # Count by sensor type
        sensor_type_counts = Counter(alert.sensor_type for alert in self.alerts)
        
        # Count by sensor ID
        sensor_id_counts = Counter(alert.sensor_id for alert in self.alerts)
        
        # Timeline (sorted by timestamp)
        timeline = sorted(self.alerts, key=lambda a: a.timestamp)
        
        return {
            'total_alerts': len(self.alerts),
            'by_severity': dict(severity_counts),
            'by_rule': dict(rule_counts),
            'by_sensor_type': dict(sensor_type_counts),
            'by_sensor_id': dict(sensor_id_counts),
            'timeline': [
                {
                    'timestamp': alert.timestamp.isoformat(),
                    'sensor_id': alert.sensor_id,
                    'sensor_type': alert.sensor_type,
                    'rule_name': alert.rule_name,
                    'severity': alert.severity.value,
                    'value': alert.value,
                    'message': alert.message
                }
                for alert in timeline
            ]
        }
    
    def print_summary(self):
        """Print formatted alert summary to console with color coding."""
        summary = self.generate_summary()
        
        # ANSI color codes
        COLORS = {
            'low': '\033[93m',      # Yellow
            'medium': '\033[38;5;208m',  # Orange  
            'high': '\033[91m',     # Red
            'critical': '\033[95m', # Magenta
            'reset': '\033[0m'      # Reset
        }
        
        def colorize_severity(severity: str) -> str:
            """Add color to severity text."""
            color = COLORS.get(severity.lower(), COLORS['reset'])
            return f"{color}{severity.upper()}{COLORS['reset']}"
        
        print("\n" + "="*60)
        print("ALERT SUMMARY REPORT")
        print("="*60)
        
        print(f"Total Alerts: {summary['total_alerts']}")
        
        if summary['total_alerts'] == 0:
            print("No alerts generated.")
            return
        
        # Severity breakdown with colors and legend
        print("\nAlerts by Severity:")
        print("-" * 30)
        print(f"  {COLORS['reset']}Legend: {COLORS['low']}●{COLORS['reset']} Low (Yellow)  "
              f"{COLORS['medium']}●{COLORS['reset']} Medium (Orange)  "
              f"{COLORS['high']}●{COLORS['reset']} High (Red)  "
              f"{COLORS['critical']}●{COLORS['reset']} Critical (Magenta)")
        print("-" * 30)
        for severity, count in summary['by_severity'].items():
            colored_severity = colorize_severity(severity)
            print(f"  {colored_severity:<20}: {count:>3}")
        
        # Rule breakdown
        print("\nAlerts by Rule:")
        print("-" * 40)
        for rule, count in summary['by_rule'].items():
            print(f"  {rule:<25}: {count:>3}")
        
        # Sensor type breakdown
        print("\nAlerts by Sensor Type:")
        print("-" * 35)
        for sensor_type, count in summary['by_sensor_type'].items():
            print(f"  {sensor_type:<20}: {count:>3}")
        
        # Recent alerts (last 10) with color coding
        if summary['timeline']:
            print("\nRecent Alerts (last 10):")
            print("-" * 80)
            print(f"{'Time':<20} {'Sensor':<15} {'Rule':<20} {'Severity':<20} {'Value':<10}")
            print("-" * 80)
            
            for alert in summary['timeline'][-10:]:
                timestamp = alert['timestamp'].split('T')[1][:8]  # Just time part
                colored_severity = colorize_severity(alert['severity'])
                print(f"{timestamp:<20} "
                      f"{alert['sensor_id']:<15} "
                      f"{alert['rule_name']:<20} "
                      f"{colored_severity:<30} "  # Extra space for color codes
                      f"{alert['value']:<10.2f}")
            
            print("-" * 80)
    
    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """Get all alerts of a specific severity."""
        return [alert for alert in self.alerts if alert.severity == severity]
    
    def get_alerts_by_rule(self, rule_name: str) -> List[Alert]:
        """Get all alerts for a specific rule."""
        return [alert for alert in self.alerts if alert.rule_name == rule_name]
    
    def get_alerts_by_sensor(self, sensor_id: str) -> List[Alert]:
        """Get all alerts for a specific sensor."""
        return [alert for alert in self.alerts if alert.sensor_id == sensor_id]
    
    def get_critical_alerts(self) -> List[Alert]:
        """Get all critical alerts."""
        return self.get_alerts_by_severity(AlertSeverity.CRITICAL)
    
    def reset(self):
        """Reset all alerts."""
        self.alerts.clear()
