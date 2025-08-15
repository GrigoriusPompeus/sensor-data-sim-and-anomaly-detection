# Sensor Calculations and Thresholds Reference

**Made by Grigor Crandon**

## Overview
This document describes how our sensor simulation calculates realistic values and what thresholds trigger anomaly alerts.

---

## Temperature Sensor Calculations

### Base Physics Model
The temperature sensor combines multiple environmental factors:

1. **Base Temperature by Location:**
   - Sydney: 20°C base, 12°C daily range, 15°C seasonal range
   - Melbourne: 16°C base, 10°C daily range, 18°C seasonal range  
   - Brisbane: 22°C base, 8°C daily range, 12°C seasonal range
   - Perth: 19°C base, 14°C daily range, 16°C seasonal range
   - Adelaide: 18°C base, 13°C daily range, 17°C seasonal range
   - **Darwin: 28°C base, 5°C daily range, 4°C seasonal range**
   - Hobart: 14°C base, 8°C daily range, 14°C seasonal range
   - Canberra: 16°C base, 16°C daily range, 20°C seasonal range
   - **Alice Springs: 22°C base, 18°C daily range, 20°C seasonal range**
   - Cairns: 25°C base, 6°C daily range, 8°C seasonal range

2. **Seasonal Component:**
   - Peak summer around mid-January (day 15)
   - Peak winter around mid-July (day 196)
   - Uses cosine function: `cos(2π × (day_of_year - 15) / 365.25)`

3. **Daily Solar Radiation:**
   - Solar elevation angle calculation using latitude (-35°)
   - Hour angle: 15° × (hour - 12)
   - Positive effect during day, negative at night
   - Maximum effect at solar noon

4. **Weather Influences:**
   - Random weather offset with thermal mass damping
   - Gradual changes to simulate realistic weather patterns

5. **Final Calculation:**
   ```
   Temperature = Base + Seasonal + Solar_Radiation + Weather_Offset
   ```

### Temperature Anomaly Thresholds
- **Frost Warning (HIGH):** < -5.0°C
- **Hot Weather (MEDIUM):** > 30.0°C  
- **Extreme Heat (HIGH):** > 35.0°C

---

## Humidity Sensor Calculations

### Base Physics Model
The humidity sensor simulates relative humidity with environmental coupling:

1. **Location Type Characteristics:**
   - **Coastal:** 70% base, 15% seasonal range, 20% daily range
   - **Inland:** 50% base, 25% seasonal range, 30% daily range
   - **Urban:** 60% base, 20% seasonal range, 25% daily range
   - **Tropical:** 80% base, 10% seasonal range, 15% daily range
   - **Arid:** 30% base, 20% seasonal range, 35% daily range

2. **Temperature Coupling:**
   - Inverse relationship: higher temperature → lower humidity
   - Coupling strength configurable (0.0-1.0)

3. **Daily Cycle:**
   - Higher humidity at night (dew formation)
   - Lower humidity during day (evaporation)
   - Peak humidity around 6 AM, minimum around 2 PM

4. **Weather Sensitivity:**
   - Rain events increase humidity significantly
   - Different rain sensitivity by location type

5. **Final Calculation:**
   ```
   Humidity = Base + Seasonal + Daily_Cycle + Temperature_Effect + Weather_Effect
   ```

### Humidity Anomaly Thresholds
- **Sensor Malfunction (CRITICAL):** < 0.0% or > 100.0%

---

## Pressure Sensor Calculations

### Base Physics Model
The atmospheric pressure sensor uses barometric altitude correction:

1. **Altitude Adjustment:**
   Uses barometric formula to calculate pressure at altitude:
   ```
   P = P₀ × exp(-g × M × h / (R × T))
   ```
   Where:
   - P₀ = sea level pressure (1013.25 hPa default)
   - h = altitude in meters
   - Standard atmospheric conditions applied

2. **City Altitudes:**
   - Sydney: 19m, Melbourne: 31m, Brisbane: 27m
   - Perth: 46m, Adelaide: 50m, Darwin: 30m
   - Hobart: 51m, **Canberra: 580m**, **Alice Springs: 545m**
   - Cairns: 3m

3. **Weather Patterns:**
   - High/low pressure systems simulation
   - Pressure trends (rising/falling)
   - Weather variability factor (0.0-1.0)

4. **Diurnal Variation:**
   - Small daily pressure oscillations (~1-3 hPa)
   - Semi-diurnal atmospheric tides

5. **Final Calculation:**
   ```
   Pressure = Base_Altitude_Adjusted + Weather_Pattern + Diurnal_Variation
   ```

### Pressure Anomaly Thresholds
- **Very Low Pressure (MEDIUM):** < 950.0 hPa
- **Very High Pressure (MEDIUM):** > 1050.0 hPa

---

## Statistical Anomaly Detection (Z-Score)

In addition to threshold rules, we use statistical analysis:

### Z-Score Calculation
- **Rolling Window:** 10 readings per sensor
- **Threshold:** Z-score > 3.0 (statistical outlier)
- **Severity Grading:**
  - 3.0-4.0: MEDIUM severity
  - 4.0-5.0: HIGH severity  
  - >5.0: CRITICAL severity

### Z-Score Formula
```
z = (value - window_mean) / window_stdev
```

---

## Current Simulation Ranges

Based on Australian environmental conditions and physics models:

### Typical Value Ranges
- **Temperature:** 13-35°C (varies by location and season)
- **Humidity:** 20-90% RH (varies by location type)
- **Pressure:** 980-1030 hPa (varies by altitude and weather)

### Alert Frequency
- **Rule-based alerts:** Triggered by extreme values
- **Statistical alerts:** Triggered by sudden changes or outliers
- **Combined approach:** Catches both extreme values and unusual patterns

---

## Testing the System

### Generate Test Data
```bash
# Hot location, longer duration for more variation
python cli.py simulate --duration 60 --location "Alice Springs" --interval 0.5

# Detect anomalies
python cli.py detect

# Generate report with visualisation
python cli.py report
```

### View Active Rules
```bash
python test_active_rules.py
```

This shows all 7 active anomaly detection rules currently configured in the system.
