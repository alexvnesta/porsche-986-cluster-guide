# Instrument Cluster Wiring & Connectors

## Cluster Connector Pinout

The 986/996 instrument cluster uses a large multi-pin connector on the back.

### Main Connector (32-pin)

Research in progress. Known signals:

| Pin | Signal | Description |
|-----|--------|-------------|
| ? | CAN-H | CAN bus high |
| ? | CAN-L | CAN bus low |
| ? | IGN | Ignition switched +12V |
| ? | GND | Ground |
| ? | ILL+ | Illumination +12V |
| ? | ILL- | Illumination dimmer |
| ? | FUEL | Fuel level sender |
| ? | TEMP | Coolant temp sender |
| ? | OIL-P | Oil pressure sender |
| ? | OIL-T | Oil temp sender |
| ? | SPEED | Speed signal input |
| ? | TACH | Tachometer signal |

## CAN Bus Communication

The cluster communicates with other modules via CAN bus:
- **Speed:** 500 kbps
- **Protocol:** ISO 15765 / UDS

### CAN Messages (Research Needed)

| CAN ID | Description |
|--------|-------------|
| ? | Engine RPM |
| ? | Vehicle speed |
| ? | Coolant temperature |
| ? | Warning lights |

## 986 vs 996 Cluster Differences

When swapping a 996 cluster into a 986:

| Feature | 986 | 996 |
|---------|-----|-----|
| Tachometer range | 8000 RPM | 8000 RPM |
| Speedometer | mph/kph | mph/kph |
| OBC standard | No | Some models |
| Oil pressure gauge | Some | Some |
| Fuel tank coding | 64L | 64L (Carrera) |

### Compatibility Notes

- Physical dimensions are identical
- Connector pinout is compatible
- EEPROM may need adjustment for:
  - OBC enable/disable
  - Fuel tank size
  - Gauge configuration

## Power Supply

| Supply | Voltage | Notes |
|--------|---------|-------|
| Battery | 12V | Permanent for memory |
| Ignition | 12V | Switched with key |
| Illumination | 0-12V | Dimmer controlled |

## Ground Points

The cluster grounds through the main connector. Poor grounds cause:
- Flickering displays
- Inaccurate gauges
- Intermittent operation

## Diagnostic Connector

The cluster can be diagnosed via OBD-II port using:
- PIWIS/PST2
- Durametric
- Generic OBD-II (limited)

### Cluster Self-Test

Some clusters support a self-test mode:
1. Turn ignition to position 2
2. Press and hold trip reset button
3. Watch gauges sweep through range
4. Warning lights illuminate in sequence

## References

- Porsche Workshop Manual
- Community wiring diagrams
