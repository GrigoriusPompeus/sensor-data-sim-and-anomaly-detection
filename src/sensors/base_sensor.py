"""
Base Sensor Class

Abstract base class for all sensor implementations in the simulation framework.
Defines the common interface and shared functionality for sensor objects.

Author: Grigor Crandon
Date: August 2025
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import uuid
import numpy as np


class SensorReading:
    """
    Represents a single sensor reading with timestamp and metadata.
    """
    
    def __init__(
        self,
        value: Union[float, int],
        timestamp: Optional[datetime] = None,
        sensor_id: Optional[str] = None,
        sensor_type: str = "generic",
        quality: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.value = value
        self.timestamp = timestamp or datetime.now()
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.quality = quality  # Quality factor (0.0 = bad, 1.0 = perfect)
        self.metadata = metadata or {}
    
    def __repr__(self) -> str:
        return f"SensorReading(value={self.value}, timestamp={self.timestamp}, sensor_id={self.sensor_id})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert reading to dictionary format."""
        return {
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'sensor_id': self.sensor_id,
            'sensor_type': self.sensor_type,
            'quality': self.quality,
            'metadata': self.metadata
        }


class BaseSensor(ABC):
    """
    Abstract base class for all sensor implementations.
    
    This class defines the common interface that all sensors must implement,
    including data generation, noise simulation, and calibration functionality.
    """
    
    def __init__(
        self,
        sensor_id: Optional[str] = None,
        sensor_type: str = "generic",
        units: str = "unknown",
        sample_rate: float = 1.0,
        range_min: float = 0.0,
        range_max: float = 100.0,
        accuracy: float = 0.1,
        precision: float = 0.01,
        calibration_date: Optional[datetime] = None,
        **kwargs
    ):
        """
        Initialise base sensor with common parameters.
        
        Args:
            sensor_id: Unique identifier for the sensor
            sensor_type: Type of sensor (e.g., 'temperature', 'pressure')
            units: Measurement units (e.g., '°C', 'Pa', '%')
            sample_rate: Sample rate in Hz
            range_min: Minimum measurable value
            range_max: Maximum measurable value
            accuracy: Sensor accuracy as percentage of full scale
            precision: Sensor precision (smallest detectable change)
            calibration_date: Last calibration date
            **kwargs: Additional sensor-specific parameters
        """
        self.sensor_id = sensor_id or str(uuid.uuid4())
        self.sensor_type = sensor_type
        self.units = units
        self.sample_rate = sample_rate
        self.range_min = range_min
        self.range_max = range_max
        self.accuracy = accuracy
        self.precision = precision
        self.calibration_date = calibration_date or datetime.now()
        
        # Internal state
        self._is_active = False
        self._last_reading = None
        self._reading_count = 0
        self._drift_factor = 0.0
        self._noise_level = 0.01
        self._malfunction_probability = 0.0
        
        # Store additional parameters
        self._parameters = kwargs
    
    @property
    def is_active(self) -> bool:
        """Check if sensor is currently active."""
        return self._is_active
    
    @property
    def last_reading(self) -> Optional[SensorReading]:
        """Get the last sensor reading."""
        return self._last_reading
    
    @property
    def reading_count(self) -> int:
        """Get total number of readings taken."""
        return self._reading_count
    
    def activate(self) -> None:
        """Activate the sensor for data collection."""
        self._is_active = True
    
    def deactivate(self) -> None:
        """Deactivate the sensor."""
        self._is_active = False
    
    def set_noise_level(self, noise_level: float) -> None:
        """Set the noise level for the sensor (0.0 = no noise, 1.0 = high noise)."""
        self._noise_level = max(0.0, min(1.0, noise_level))
    
    def set_drift_factor(self, drift_factor: float) -> None:
        """Set the calibration drift factor."""
        self._drift_factor = drift_factor
    
    def set_malfunction_probability(self, probability: float) -> None:
        """Set probability of sensor malfunction (0.0 = never, 1.0 = always)."""
        self._malfunction_probability = max(0.0, min(1.0, probability))
    
    @abstractmethod
    def _generate_base_value(self, timestamp: datetime) -> float:
        """
        Generate the base (ideal) sensor value for a given timestamp.
        
        This method must be implemented by each sensor type to define
        the underlying physical phenomenon being measured.
        
        Args:
            timestamp: The time for which to generate the value
            
        Returns:
            The ideal sensor value without noise or drift
        """
        pass
    
    def _apply_noise(self, value: float) -> float:
        """
        Apply realistic noise to the sensor reading.
        
        Args:
            value: The clean sensor value
            
        Returns:
            The value with noise applied
        """
        if self._noise_level <= 0:
            return value
        
        # Gaussian noise based on sensor precision and noise level
        noise_std = self.precision * self._noise_level * 10
        noise = np.random.normal(0, noise_std)
        
        return value + noise
    
    def _apply_drift(self, value: float) -> float:
        """
        Apply calibration drift to the sensor reading.
        
        Args:
            value: The sensor value
            
        Returns:
            The value with drift applied
        """
        if self._drift_factor == 0:
            return value
        
        # Calculate drift based on time since calibration
        time_since_calibration = datetime.now() - self.calibration_date
        drift_days = time_since_calibration.total_seconds() / (24 * 3600)
        
        # Apply linear drift
        drift_amount = self._drift_factor * drift_days * (self.range_max - self.range_min) / 100
        
        return value + drift_amount
    
    def _check_malfunction(self) -> bool:
        """
        Check if sensor should malfunction on this reading.
        
        Returns:
            True if sensor should malfunction
        """
        return np.random.random() < self._malfunction_probability
    
    def _clamp_to_range(self, value: float) -> float:
        """
        Clamp value to sensor's measurable range.
        
        Args:
            value: The sensor value
            
        Returns:
            The clamped value
        """
        return max(self.range_min, min(self.range_max, value))
    
    def read(self, timestamp: Optional[datetime] = None) -> SensorReading:
        """
        Take a sensor reading at the specified timestamp.
        
        Args:
            timestamp: The time of the reading (defaults to now)
            
        Returns:
            A SensorReading object with the measured value
        """
        if not self._is_active:
            raise RuntimeError(f"Sensor {self.sensor_id} is not active")
        
        timestamp = timestamp or datetime.now()
        
        # Check for malfunction
        if self._check_malfunction():
            # Return a bad reading
            reading = SensorReading(
                value=float('nan'),
                timestamp=timestamp,
                sensor_id=self.sensor_id,
                sensor_type=self.sensor_type,
                quality=0.0,
                metadata={'malfunction': True}
            )
        else:
            # Generate normal reading
            base_value = self._generate_base_value(timestamp)
            value_with_drift = self._apply_drift(base_value)
            value_with_noise = self._apply_noise(value_with_drift)
            final_value = self._clamp_to_range(value_with_noise)
            
            # Calculate quality based on noise and drift
            quality = max(0.0, 1.0 - self._noise_level - abs(self._drift_factor) / 100)
            
            reading = SensorReading(
                value=final_value,
                timestamp=timestamp,
                sensor_id=self.sensor_id,
                sensor_type=self.sensor_type,
                quality=quality,
                metadata={
                    'base_value': base_value,
                    'drift_applied': value_with_drift - base_value,
                    'noise_level': self._noise_level
                }
            )
        
        self._last_reading = reading
        self._reading_count += 1
        
        return reading
    
    def read_multiple(
        self,
        count: int,
        interval: Optional[timedelta] = None,
        start_time: Optional[datetime] = None
    ) -> List[SensorReading]:
        """
        Take multiple sensor readings over a time period.
        
        Args:
            count: Number of readings to take
            interval: Time interval between readings (defaults to 1/sample_rate)
            start_time: Starting timestamp (defaults to now)
            
        Returns:
            List of SensorReading objects
        """
        if interval is None:
            interval = timedelta(seconds=1.0 / self.sample_rate)
        
        start_time = start_time or datetime.now()
        readings = []
        
        for i in range(count):
            timestamp = start_time + (interval * i)
            reading = self.read(timestamp)
            readings.append(reading)
        
        return readings
    
    def calibrate(self, reference_value: float, actual_value: float) -> None:
        """
        Calibrate the sensor using a known reference.
        
        Args:
            reference_value: The known true value
            actual_value: The value read by the sensor
        """
        # Calculate and apply calibration offset
        calibration_error = actual_value - reference_value
        self._drift_factor = -calibration_error / (self.range_max - self.range_min) * 100
        self.calibration_date = datetime.now()
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get comprehensive sensor information.
        
        Returns:
            Dictionary containing sensor specifications and current state
        """
        return {
            'sensor_id': self.sensor_id,
            'sensor_type': self.sensor_type,
            'units': self.units,
            'sample_rate': self.sample_rate,
            'range': [self.range_min, self.range_max],
            'accuracy': self.accuracy,
            'precision': self.precision,
            'calibration_date': self.calibration_date.isoformat(),
            'is_active': self._is_active,
            'reading_count': self._reading_count,
            'noise_level': self._noise_level,
            'drift_factor': self._drift_factor,
            'malfunction_probability': self._malfunction_probability,
            'parameters': self._parameters
        }
    
    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}(id={self.sensor_id}, "
                f"type={self.sensor_type}, units={self.units}, "
                f"active={self._is_active})")
