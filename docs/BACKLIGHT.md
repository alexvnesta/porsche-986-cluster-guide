# Backlight Repair Guide

## Backlight Types

The 986/996 cluster uses different backlight methods depending on generation:

| Era | Cluster Type | Backlight & Indicator Illumination |
|-----|--------------|------------------------------------|
| **MY1997–2000** | Early (`93C56B`, 3×26-pin) | Replaceable twist-lock incandescent bulbs (T5 / B8.5d sockets) |
| **MY2001–2005** | Late (`Kombi 2000`, `93C86`, 3×32-pin) | Mix of surface-mount (PLCC SMD) LEDs and twist-lock bulbs |

## Common Issues

### Symptoms
- Dim cluster or dark LCD windows at night
- Uneven lighting (one gauge or LCD window dark)
- Complete backlight failure
- Flickering illumination

### Causes
1. **Burned out incandescent bulbs** — Most common on early clusters and LCD backlights
2. **Poor socket contacts** — Oxidation on PCB copper traces
3. **Terminal 58d dimmer circuit or ambient photocell fault** — Logs DTC `9150` or `9151` on late clusters

## Bulb Specifications

| Location | Type | Notes |
|----------|------|-------|
| Main gauge backlight | T5 / B8.5d twist-lock | 3000K–4000K warm white for stock look |
| LCD window backlight | T5 / B8.5d twist-lock (1 per LCD window) | If one LCD window appears dead, check its rear bulb first! |
| Warning indicators | T5 wedge / twist-lock (Early) or SMD LED (Late) | Note polarity if converting to LED |

## Dimmer Circuit & Pinout (`Terminal 58d`)

If ALL backlights are dim or not working, test the `Terminal 58d` illumination circuit and built-in ambient light sensor:

### 1. Pin Locations (`Terminal 58d`)
- **Late Cluster (`Kombi 2000`, MY2001–2005, Green Plug A):**
  - **`Plug A Pin 12`:** **Terminal 58d Input** (`0.5 GR/BL`) — Instrument lighting dimmer signal from light switch
  - **`Plug A Pin 13`:** **Terminal 58d Output** (`0.5 GR/BL`) — Regulated PWM illumination output to dash switches (short circuit logs **DTC `9150`**)
- **Early Cluster (MY1997–2000, White Plug II):**
  - **`Plug II Pin 23`:** **Terminal 58d Input** (`0.5 GR/BL`)
  - **`Plug II Pin 19`:** **Terminal 58d Output** (`0.5 GR/RD`)

### 2. Ambient Light Photocell (`DTC 9151`)
The cluster has an internal phototransistor on the gauge face that automatically adjusts LCD and scale brightness based on ambient cabin light.
- On late clusters, you can read the live photocell ADC and dimmer percentage over K-line (`0x64`) via Service **`21 02`**:
  - **Byte 9 (`d9`):** Dimmer rheostat setting (`0..100 %`)
  - **Byte 10 (`d10`):** Ambient light photocell reading (`0x00–0xFF`)
- If the phototransistor fails, the cluster logs **DTC `9151`** (*Fototransistor unplausibel*).

## Testing on the Bench
See [WIRING.md](WIRING.md#4-bench-power-up--diagnostic-harness-guide) for full bench power-up pinouts (`Plug A Pins 1/17` GND, `Pins 2/18` +12V Term 30, `Pin 3` +12V Term 15, and `Pin 12` +12V Term 58d illumination).
