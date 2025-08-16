# Quick Reference Guide

**Sensor Simulation & Anomaly Detection System**  
*Author: Grigor Crandon - August 2025*

## 🚀 Installation & Setup

```bash
# Clone from GitHub
git clone git@github.com:GrigoriusPompeus/sensor-data-sim-and-anomaly-detection.git
cd sensor-data-sim-and-anomaly-detection

# Setup environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Verify installation
python test_imports.py
```

## ⚡ Quick Commands

```bash
# Complete demo
python demo.py

# Smart workflow (recommended) - auto-generates fresh alerts
python cli.py simulate --duration 60 --location Brisbane --output data/brisbane.ndjson
python cli.py report --data data/brisbane.ndjson --plot-sensor temp_brisbane

# Legacy workflow - manual alert generation
python cli.py simulate --duration 60 --location Brisbane
python cli.py detect --z-threshold 2.5 --window-size 15  
python cli.py report --alerts out/alerts.ndjson
```

## 📝 Command Reference

### Simulate
```bash
python cli.py simulate [options]
  --duration SECONDS     # Duration in seconds (default: 60)
  --interval SECONDS     # Sample interval (default: 1.0)
  --location CITY        # Australian city (default: Sydney)
  --output FILE          # Output file (default: data/readings.ndjson)
```

### Detect
```bash
python cli.py detect [options]
  --input FILE           # Input NDJSON (default: data/readings.ndjson)
  --output FILE          # Output alerts (default: out/alerts.ndjson)
  --window-size N        # Z-score window (default: 10)
  --z-threshold FLOAT    # Z-score threshold (default: 3.0)
```

### Report
```bash
python cli.py report [options]
  --data FILE            # Sensor data (default: data/readings.ndjson)
  --alerts FILE          # Alerts file (default: auto-generated from data)
  --plot-sensor ID       # Single sensor plot (optional)

# New smart features:
# - Auto-detects location from data metadata
# - Auto-generates fresh alerts if none specified  
# - Color-coded terminal output with severity legend
# - PNG plots include comprehensive alert severity legend
```

## 🧪 Testing

```bash
python test_imports.py        # Verify installation
python test_all_sensors.py    # Test sensor physics
python test_data_generator.py # Test data generation
python examples_practical.py  # Real-world examples
```

## 🌏 Available Locations

Sydney | Melbourne | Brisbane | Perth | Adelaide | Darwin | Hobart | Canberra

## 📊 Output Files

- `data/readings.ndjson` - Raw sensor data (~86KB for 60s)
- `out/alerts.ndjson` - Detected anomalies (~5KB)
- `out/multi_sensor_plot.png` - All sensors plot (~430KB)
- `out/plot.png` - Single sensor plot (if specified)

## 🚨 Default Anomaly Rules

- High temp > 30°C (MEDIUM), > 35°C (HIGH)
- Low temp < -5°C (HIGH - frost)
- Pressure < 950 or > 1050 hPa (MEDIUM)
- Humidity < 0% or > 100% (CRITICAL)
- Z-score > threshold (LOW→CRITICAL based on magnitude)

## 🎨 Alert Color Coding

The system uses color-coded severity levels in reports:

- **🟡 LOW (Yellow)** - Minor anomalies, statistical outliers
- **🟠 MEDIUM (Orange)** - Moderate anomalies, environmental alerts  
- **🔴 HIGH (Red)** - Significant anomalies, dangerous conditions
- **🟣 CRITICAL (Magenta)** - Severe anomalies, system failures

Colors appear in:
- Alert summary tables
- Severity breakdowns  
- Recent alerts listings

---
*Professional sensor simulation for IoT testing, algorithm development, and education*
