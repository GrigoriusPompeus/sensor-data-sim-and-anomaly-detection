"""Tests for sensor calibration behaviour."""

from datetime import datetime, timedelta

from src.sensors.base_sensor import BaseSensor


class DummySensor(BaseSensor):
    """Simple sensor returning a constant base value for testing."""

    def _generate_base_value(self, timestamp: datetime) -> float:  # pragma: no cover - behaviour trivial
        return 50.0


def test_calibration_corrects_reading_and_preserves_drift():
    sensor = DummySensor(range_min=0, range_max=100)
    sensor.set_noise_level(0)
    sensor.set_drift_factor(0.5)  # 0.5% of range per day -> 0.5 units/day
    sensor.activate()

    # Simulate passage of time to accumulate drift
    sensor.calibration_date = datetime.now() - timedelta(days=10)
    reading = sensor.read(datetime.now())
    assert abs(reading.value - 55.0) < 1e-6  # base 50 + 5 units drift

    # Calibrate using a known reference value
    sensor.calibrate(reference_value=50.0, actual_value=reading.value)

    # Immediate reading should match the reference value
    corrected = sensor.read(datetime.now())
    assert abs(corrected.value - 50.0) < 1e-6

    # Future reading shows normal drift rate from calibration time
    future = sensor.read(datetime.now() + timedelta(days=2))
    assert abs(future.value - 51.0) < 1e-6

