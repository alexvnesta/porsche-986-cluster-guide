# LCD Display Repair Guide

## Common LCD Issues

The 986/996 instrument cluster LCD displays are prone to failure, typically showing:
- Missing pixel rows/columns
- Faded or dim segments
- Dark bleeding ("black spot" nematic crystal leakage)
- Complete display failure or intermittent segments

## Root Cause

The three segmented LCD panels are connected to the circuit board via flexible heat-bonded ribbon cables (elastomeric / zebra-strip connectors). Over time:
- Thermal cycling weakens the conductive adhesive bond
- Internal liquid crystal seals degrade under UV/heat exposure
- Connection becomes intermittent

## Repair Options

### Option 1: Re-flow Existing Connection

**Difficulty:** Medium
**Success Rate:** 50-70%
**Cost:** Free (if you have tools)

1. Remove cluster from vehicle
2. Disassemble cluster housing
3. Carefully lift LCD frame from circuit board
4. Clean contacts with isopropyl alcohol
5. Re-heat the ribbon cable connection using a T-bar soldering iron tip with Teflon strip
6. Apply even pressure while cooling
7. Test on bench (`Plug A Pins 1/17` GND, `Pins 2/18/3` +12V on MY01+; or KWP2000 `30 18 00` segment test) before reassembly

### Option 2: Replace LCD Glass & Ribbon Cable (`Minitools SEPDISP87`)

**Difficulty:** Medium-High
**Success Rate:** 90%+
**Cost:** $50-120 per LCD / ribbon kit

1. Source the correct replacement LCD panel (e.g., **Minitools `SEPDISP87`** for MY2001–2004 986 / MY2001–2005 996 3-window clusters)
2. Remove old ribbon cable / glass carefully
3. Clean all PCB gold-plated contacts thoroughly with isopropyl alcohol
4. Position new ribbon cable / LCD glass precisely
5. Heat-bond or seat connector frame
6. Test all segments using the cluster self-test mode or KWP2000 actuator test `30 18 00`

### Option 3: Professional Repair

**Difficulty:** None (send it out)
**Success Rate:** 95%+
**Cost:** $150-350

## Required Tools

- Torx drivers (T10, T20)
- Small Phillips screwdriver
- Soldering iron with T-bar heat-seal tip
- Isopropyl alcohol (90%+)
- Lint-free cloth
- Magnifying glass or loupe

## Disassembly Procedure

### Removing from Vehicle

1. Disconnect battery negative terminal (never turn ignition ON while the cluster is unplugged, or the Airbag ECU `0x15` will latch a fault code!)
2. Pry up the hazard switch trim and microphone/Left bezel cover to access the 2x Torx T20 screws
3. Tilt cluster forward and release the 3 sliding Cam-Lock connector latches (Green Plug A, Blue Plug B, Grey Plug C on MY01+; Blue Plug I, White Plug II, Black Plug III on MY97–00)
4. Remove cluster

### Opening the Cluster

1. Note orientation of all components and take photos before disassembly
2. Unclip the rear white housing cover and remove the Torx screws
3. Separate housing halves and access the PCB and 3 LCD cages

## Replacement LCDs & Contrast Voltage Bias (`0x2C6`)

If the LCD glass itself is cracked, bleeding, or delaminated:
- **Aftermarket Replacement LCD Glass:** **Minitools `SEPDISP87`** (direct replacement for late 3-window segmented clusters).
- **Important Note on 3-Window Segmented LCDs:** Every 986 Boxster cluster (both Early MY97–00 and Late MY01–04 `K21/K24/K26`) uses **three segmented nematic LCD windows**. None of the 986 clusters use a central dot-matrix display (which was only fitted to MY2002+ 996 Carrera facelift clusters `DSN K27+`).
- **LCD Operating Voltage / Contrast Bias (`EEPROM Offset 0x2C6`):**
  - On late `93C86` clusters, EEPROM byte **`0x2C6`** sets the microcontroller's LCD operating voltage (`VLCD`, nominal **`12.7 V – 12.9 V`**).
  - **Factory 986 (`K21` / `K24`) value:** `0x21` (`33`).
  - **Factory 996 (`K23`) value:** `0x20` (`32`).
  - Each `±1` hex step shifts `VLCD` by approximately **`±0.1 V`** (`+1` = darker segments; `-1` = lighter segments / less ghosting in hot cabin temperatures).

## Related Issues

- **Dim Backlight:** See [BACKLIGHT.md](BACKLIGHT.md)
- **Gauge / Coding Issues:** See [DIAGNOSTICS.md](DIAGNOSTICS.md) and [EEPROM_MAP.md](EEPROM_MAP.md)
