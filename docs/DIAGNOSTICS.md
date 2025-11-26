# Cluster Diagnostics Guide

## Self-Test Mode

The 986/996 cluster has a built-in self-test function:

### Activation

1. Turn ignition to position 2 (accessories on, engine off)
2. Press and hold the trip odometer reset button
3. Turn ignition to position 3 (run)
4. Continue holding for ~10 seconds

### What Happens

- All gauges sweep from minimum to maximum
- All warning lights illuminate
- LCD shows all segments
- Helps identify stuck gauges or dead lights

## Common Issues & Diagnosis

### Speedometer Not Working

**Symptoms:**
- Speedometer stays at zero
- Odometer not counting

**Possible Causes:**
1. Speed sensor failure
2. Wiring issue
3. Cluster internal fault
4. CAN bus communication error

**Diagnosis:**
- Check for fault codes via OBD-II
- Test speed sensor with multimeter
- Verify CAN bus signals

### Tachometer Erratic

**Symptoms:**
- Jumpy needle
- Incorrect RPM reading
- Needle stuck

**Possible Causes:**
1. Signal wire interference
2. Ground issue
3. Cluster internal fault

### Fuel Gauge Inaccurate

**Symptoms:**
- Always shows full
- Always shows empty
- Erratic readings

**Possible Causes:**
1. Fuel level sender in tank
2. Wiring to sender
3. Cluster internal fault
4. Wrong tank coding (if cluster swapped)

**Diagnosis:**
- Check sender resistance (empty ~250Ω, full ~30Ω approximately)
- Verify wiring continuity
- Check EEPROM tank coding

### Temperature Gauge Issues

**Symptoms:**
- Always cold
- Always hot
- Erratic

**Possible Causes:**
1. Coolant temp sensor
2. Wiring
3. Thermostat stuck (actually runs cold/hot)
4. Cluster fault

### Warning Lights Stay On

**Symptoms:**
- ABS/PSM light stays on
- Check engine light
- Airbag light

**Diagnosis:**
- Read fault codes with proper diagnostic tool
- Usually not a cluster issue - actual fault in system

### Dim or No Backlight

See [BACKLIGHT.md](BACKLIGHT.md)

### LCD Pixel Failure

See [LCD_REPAIR.md](LCD_REPAIR.md)

## Diagnostic Tools

### PIWIS / PST2

Full dealer-level diagnostics:
- Read/clear all fault codes
- Activate individual components
- Program cluster options
- View live data

### Durametric

Popular enthusiast tool:
- Read most fault codes
- View live data
- Some programming capability
- ~$300-400

### Generic OBD-II

Limited functionality:
- Basic engine codes only
- Cannot access cluster directly
- Good for emissions checks

### Multimeter Tests

| Test | Expected Value |
|------|----------------|
| Battery voltage | 12.4-12.8V (engine off) |
| Charging voltage | 13.5-14.5V (engine running) |
| Fuel sender (empty) | ~250Ω |
| Fuel sender (full) | ~30Ω |
| Temp sender (cold) | High resistance |
| Temp sender (hot) | Low resistance |

## Fault Code Reference

### Cluster-Related Codes

Research in progress. Common codes:

| Code | Description |
|------|-------------|
| ? | Cluster communication error |
| ? | Speed signal missing |
| ? | Fuel level signal |

## Gauge Calibration

Some gauges may need calibration after cluster work:
- Usually requires dealer tool
- Speedometer can be slightly off by design (reads high)
- Fuel gauge calibration tied to tank coding

## When to Replace vs Repair

**Repair if:**
- LCD pixel issues only
- Backlight failure
- Single gauge sticking (can sometimes free up)

**Replace if:**
- Complete cluster failure
- Multiple internal faults
- Water damage (corrosion)
- Severe physical damage

## References

- Porsche fault code databases
- Community diagnostic guides
