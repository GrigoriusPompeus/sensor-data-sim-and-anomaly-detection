"""
Plot generation for sensor data visualisation.
"""

from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os

from ..sensors.base_sensor import SensorReading
from ..anomaly.detector import Alert


class PlotGenerator:
    """Generate plots for sensor data and alerts."""
    
    def __init__(self, figsize: tuple = (12, 8)):
        self.figsize = figsize
        plt.style.use('default')  # Use default matplotlib style
    
    def plot_sensor_timeline(
        self,
        readings: List[SensorReading],
        alerts: List[Alert],
        sensor_id: str,
        sensor_type: str,
        output_path: str = "out/plot.png",
        title: Optional[str] = None
    ) -> str:
        """
        Plot sensor readings over time with alert markers.
        
        Args:
            readings: List of sensor readings
            alerts: List of alerts to mark on plot
            sensor_id: ID of sensor to plot
            sensor_type: Type of sensor to plot
            output_path: Path to save plot
            title: Custom title for plot
            
        Returns:
            Path to saved plot file
        """
        # Filter readings for the specified sensor
        sensor_readings = [
            r for r in readings 
            if r.sensor_id == sensor_id and r.sensor_type == sensor_type
        ]
        
        if not sensor_readings:
            raise ValueError(f"No readings found for sensor {sensor_id} of type {sensor_type}")
        
        # Filter alerts for the specified sensor
        sensor_alerts = [
            a for a in alerts 
            if a.sensor_id == sensor_id and a.sensor_type == sensor_type
        ]
        
        # Create plot
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Extract timestamps and values
        timestamps = [r.timestamp for r in sensor_readings]
        values = [r.value for r in sensor_readings]
        
        # Convert timestamps to matplotlib dates for proper plotting
        plot_timestamps = mdates.date2num(timestamps)
        
        # Plot sensor data
        ax.plot(plot_timestamps, values, 'b-', linewidth=1.5, label=f'{sensor_type.title()} Reading')
        
        # Add alert markers
        severity_colors = {
            'low': 'yellow',
            'medium': 'orange', 
            'high': 'red',
            'critical': 'darkred'
        }
        
        alert_severities_plotted = set()
        for alert in sensor_alerts:
            color = severity_colors.get(alert.severity.value, 'gray')
            
            # Only add to legend if we haven't plotted this severity yet
            label = f'{alert.severity.value.title()} Alert' if alert.severity.value not in alert_severities_plotted else ""
            if label:
                alert_severities_plotted.add(alert.severity.value)
            
            # Convert datetime to matplotlib format
            alert_time = mdates.date2num(alert.timestamp)
            ax.axvline(x=float(alert_time), color=color, linestyle='--', alpha=0.7, label=label)
        
        # Format plot
        ax.set_xlabel('Time')
        ax.set_ylabel(f'{sensor_type.title()} ({self._get_units(sensor_type)})')
        
        if title:
            ax.set_title(title)
        else:
            ax.set_title(f'{sensor_type.title()} Sensor Data - {sensor_id}')
        
        # Format x-axis for time
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
        plt.xticks(rotation=45)
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Add legend
        ax.legend()
        
        # Tight layout to prevent label cutoff
        plt.tight_layout()
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save plot
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def plot_multiple_sensors(
        self,
        readings: List[SensorReading],
        alerts: List[Alert],
        output_path: str = "out/multi_sensor_plot.png",
        title: str = "Multi-Sensor Data"
    ) -> str:
        """Plot multiple sensors on subplots."""
        
        # Group readings by sensor
        sensor_groups = {}
        for reading in readings:
            key = f"{reading.sensor_type}_{reading.sensor_id}"
            if key not in sensor_groups:
                sensor_groups[key] = []
            sensor_groups[key].append(reading)
        
        if not sensor_groups:
            raise ValueError("No readings provided")
        
        # Create subplots
        n_sensors = len(sensor_groups)
        fig, axes = plt.subplots(n_sensors, 1, figsize=(12, 3 * n_sensors), sharex=True)
        
        if n_sensors == 1:
            axes = [axes]
        
        # Plot each sensor
        for i, (sensor_key, sensor_readings) in enumerate(sensor_groups.items()):
            ax = axes[i]
            
            # Extract sensor info
            sensor_type = sensor_readings[0].sensor_type
            sensor_id = sensor_readings[0].sensor_id
            
            # Plot data
            timestamps = [r.timestamp for r in sensor_readings]
            values = [r.value for r in sensor_readings]
            
            # Convert timestamps to matplotlib dates
            plot_timestamps = mdates.date2num(timestamps)
            ax.plot(plot_timestamps, values, 'b-', linewidth=1.5)
            
            # Add alerts for this sensor
            sensor_alerts = [
                a for a in alerts 
                if a.sensor_id == sensor_id and a.sensor_type == sensor_type
            ]
            
            severity_colors = {
                'low': 'yellow',
                'medium': 'orange',
                'high': 'red', 
                'critical': 'darkred'
            }
            
            for alert in sensor_alerts:
                color = severity_colors.get(alert.severity.value, 'gray')
                alert_time = mdates.date2num(alert.timestamp)
                ax.axvline(x=float(alert_time), color=color, linestyle='--', alpha=0.7)
            
            # Format subplot
            ax.set_ylabel(f'{sensor_type.title()}\n({self._get_units(sensor_type)})')
            ax.set_title(f'{sensor_id}')
            ax.grid(True, alpha=0.3)
        
        # Format x-axis for bottom plot only
        axes[-1].set_xlabel('Time')
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        axes[-1].xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
        plt.xticks(rotation=45)
        
        # Overall title
        fig.suptitle(title, fontsize=14)
        
        # Tight layout
        plt.tight_layout()
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save plot
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def _get_units(self, sensor_type: str) -> str:
        """Get units for sensor type."""
        units_map = {
            'temperature': '°C',
            'pressure': 'hPa',
            'humidity': '%',
            'battery_voltage': 'V',
            'speed': 'kph'
        }
        return units_map.get(sensor_type, 'units')
