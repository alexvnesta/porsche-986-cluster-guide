# Instrument Cluster EEPROM Map

## EEPROM Chip Information

| Cluster Style | Years | Chip | Size | Read Mode |
|---------------|-------|------|------|-----------|
| Old Style | MY2000 and earlier | 93C56B | 256 bytes | 16-bit |
| New Style | MY2001 and later | 93C86 | 2048 bytes | 8-bit |

**Recommended Programmer:** Willem GQ-4X (best compatibility)

---

## Old Style Cluster (93C56B) - 256 bytes

### Memory Layout Overview

```
         00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
        ┌───────────────────────────────────────────────┐
0x00    │ ★ MILEAGE (encrypted)                         │
        ├───────────────────────────────────────────────┤
0x10    │                         │ ★ VIN starts ────── │
        ├─────────────────────────┼─────────────────────┤
0x20    │ ── VIN continues ────── │                     │
        ├───────────────────────────────────────────────┤
0x30    │          │09 86│       │PST2│               │ │
        │          │or   │       │mode│               │ │
        │          │09 96│       │    │               │ │
        ├───────────────────────────────────────────────┤
0x40    │                   │OIL │                      │
        │                   │PRES│                      │
        ├───────────────────────────────────────────────┤
0x50    │             │VOLT│                            │
        │             │ MTR│                            │
        ├───────────────────────────────────────────────┤
        │              ... (other config) ...           │
        ├───────────────────────────────────────────────┤
0xE0    │    │ DIAL CALIBRATION DATA │                  │
        │    │ (cols 02-0D)          │                  │
        └───────────────────────────────────────────────┘
```

### Key Locations (93C56B) - DETAILED

| Row | Column | Offset | Value | Description |
|-----|--------|--------|-------|-------------|
| 0x00 | 00-0F | 0x00-0x0F | (encrypted) | **Mileage** - 16 bytes, encrypted |
| 0x10 | 08-0F | 0x18-0x1F | ASCII | **VIN** (first part) |
| 0x20 | 00-08 | 0x20-0x28 | ASCII | **VIN** (second part) |
| 0x30 | 05-06 | 0x35-0x36 | `09 86` / `09 96` | **Vehicle Type** |
| 0x30 | 0B | 0x3B | `06` / `08` | **PST2 Mode** - `06`=986, `08`=996 |
| 0x40 | 07 | 0x47 | `00` / `1F` | **OBC (On-Board Computer)** - `00`=OFF, `1F`=ON |
| 0x40 | 09 | 0x49 | `3C` / `50` | **Oil Pressure Gauge** - `3C`=ON, `50`=OFF |
| 0x50 | 06 | 0x56 | `01` / `00` | **Voltmeter** - `01`=ON, `00`=OFF |
| 0xE0 | 02-0D | 0xE2-0xED | varies | **Dial Calibration** data |

### Mileage (0x00-0x0F)

- 16 bytes of encrypted mileage data
- Algorithm not publicly documented
- To transfer: copy entire block from source to destination cluster

### VIN Location

The 17-character VIN spans two rows:
- **Row 0x10, columns 08-0F** (8 bytes) - First part of VIN
- **Row 0x20, columns 00-08** (9 bytes) - Second part of VIN

Total: 17 characters

### Vehicle Type (0x35-0x36)

Tells the cluster which car it's installed in:

| Value | Model |
|-------|-------|
| `09 86` | 986 Boxster |
| `09 96` | 996 Carrera |

### PST2 Mode Byte (0x3B)

This "mystery byte" affects how PST2/PIWIS diagnostic tools interact with the cluster:

| Value | Mode |
|-------|------|
| `06` | 986 Boxster mode |
| `08` | 996 Carrera mode |

If your 996 cluster doesn't behave correctly with PST2 after install in a 986, change this byte.

### OBC - On-Board Computer (0x47)

The trip computer / on-board computer enable flag:

| Value | Status |
|-------|--------|
| `00` | DISABLED |
| `1F` | ENABLED |

This controls whether the OBC functions (average fuel consumption, range, etc.) are available.

### Oil Pressure Gauge (0x49)

| Value | Status |
|-------|--------|
| `3C` | ENABLED |
| `50` | DISABLED |

### Voltmeter (0x56)

| Value | Status |
|-------|--------|
| `01` | ENABLED |
| `00` | DISABLED |

### Dial Calibration (0xE2-0xED)

This 12-byte area contains calibration data for the four gauge needles:
- **Speedometer** (MPH or KM/H scaling)
- **Tachometer** (RPM)
- **Coolant temperature**
- **Fuel level**

The exact byte mapping for each gauge is still being researched. When doing a 996→986 conversion, you may need to copy fuel gauge calibration from your original 986 cluster for accurate readings.

### Byte Swapping Note (Important!)

The GQ-4X programmer reads/writes with bytes swapped:
1. When you first read, the VIN will look garbled
2. Click the **A-B swap icon** to read the VIN correctly
3. Make your edits with bytes swapped (VIN readable)
4. **Un-swap** (click A-B again) before writing back to chip
5. The file you write should have the VIN looking garbled again

---

## New Style Cluster (93C86) - 2048 bytes

### Memory Layout Overview

```
         00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
        ┌───────────────────────────────────────────────┐
0x000   │ ★ VIN (first line)                            │
        ├───────────────────────────────────────────────┤
0x010   │ Model code, configuration...                  │
        │                                               │
        │           ... (configuration) ...             │
        │                                               │
        ├───────────────────────────────────────────────┤
0x300   │ ★ MILEAGE (encrypted) - PRIMARY               │
0x310   │ (32 bytes total)                              │
        ├───────────────────────────────────────────────┤
        │           ... (other data) ...                │
        ├───────────────────────────────────────────────┤
0x500   │ ★ MILEAGE (encrypted) - BACKUP                │
0x510   │ (32 bytes total)                              │
        └───────────────────────────────────────────────┘
```

### Key Locations (93C86)

| Offset | Length | Description |
|--------|--------|-------------|
| 0x000-0x00F | 16 bytes | **VIN** (first line, plain text) |
| 0x010-0x02F | varies | Model code, configuration |
| 0x300-0x31F | 32 bytes | **Mileage** (encrypted) - PRIMARY |
| 0x500-0x51F | 32 bytes | **Mileage** (encrypted) - BACKUP |

**Important:** Both mileage locations (0x300 and 0x500) must be updated together!

### Crystal Shorting (Required for New Style)

The new style clusters run on lower power. The programmer provides enough power to start the processor, which interferes with reading.

**Solution:** Short the crystal legs before reading/writing:
1. Locate the crystal on the circuit board (near processor)
2. Use a wire or paperclip to short the two legs together
3. This safely stops the processor without damage
4. Now you can read/write the EEPROM normally

### No Byte Swapping

Unlike old-style clusters, new-style code is NOT byte-swapped when read.

---

## Feature Enable Summary

### Old Style (93C56B)

| Feature | Offset | Enable | Disable |
|---------|--------|--------|---------|
| **OBC (Trip Computer)** | 0x47 | `1F` | `00` |
| **Oil Pressure Gauge** | 0x49 | `3C` | `50` |
| **Voltmeter** | 0x56 | `01` | `00` |
| **Vehicle Type** | 0x35-0x36 | `09 86`=986 | `09 96`=996 |
| **PST2 Mode** | 0x3B | `06`=986 | `08`=996 |

### New Style (93C86)

| Feature | Offset | Enable | Disable |
|---------|--------|--------|---------|
| **OBC** | TBD | TBD | TBD |
| **Voltmeter** | TBD | TBD | TBD |
| **Oil Pressure Gauge** | TBD | TBD | TBD |

---

## Market Configuration (UK vs US)

Based on comparison of UK (KM/Celsius) vs US (Miles/Fahrenheit) dumps:

### Potential Market/Unit Offsets (Old Style)

The following bytes differ between UK and US market clusters:

| Offset | UK (KM/C) | US (Miles/F) | Possible Function |
|--------|-----------|--------------|-------------------|
| 0x40 | `34` | `18` | Market config? |
| 0x41 | `5D` | `60` | Market config? |
| 0x44 | `99` | `66` | Market config? |
| 0x46 | `16` | `26` | Market config? |
| 0x4B | `BC` | `61` | Market config? |
| 0xEB-0xED | `E4 52 94` | `E9 66 83` | **Speedometer calibration (KM vs Miles?)** |

### Dial Calibration (0xE2-0xED)

This 12-byte area contains calibration data for four gauges:
- **Speedometer** (MPH or KM/H)
- **Tachometer** (RPM)
- **Coolant temperature**
- **Fuel level**

```
Offset    UK (KM)         US (MPH/C)      Notes
0xE2-E3   1B 12           18 10           Related to voltmeter?
0xE4-EA   00 00 AF 00 EC 09 E4            Common (unchanged)
0xEB-ED   E4 52 94        E9 66 83        SPEEDOMETER SCALING
```

**Hypothesis:** Bytes 0xEB-0xED contain the speedometer scaling factor:
- `E4 52 94` = KM/H calibration
- `E9 66 83` = MPH calibration

**Note:** When converting a 996 cluster to 986, you may need to copy fuel gauge calibration bytes from your original 986 cluster for accurate fuel level readings.

### Row 0x40 Configuration Block

This area (0x40-0x4F) differs significantly between UK and US clusters:

```
UK (KM/C):   34 5D 00 FB 99 F6 16 1F 0B 3C 78 BC FF FF FF FF
US (Mi/F):   18 60 02 FC 66 F6 26 1F 0B 3C 78 61 FF FF FF FF
                                          ^^
                                          Oil Pressure confirmed at 0x49
```

---

## Research Needed

The following items need further investigation:

### Units Configuration
- [ ] **KM vs Miles** - Likely in 0xEB-0xED (speedometer scaling) and 0x40-0x4B area
- [ ] **Celsius vs Fahrenheit** - Location still unknown (note: MPH clusters can still use Celsius)
- [ ] **12hr vs 24hr time** - Location unknown
- [ ] **Odometer display units** - May be separate from speedometer

### Other Unknown Locations
- [x] **OBC Enable** for old-style - **FOUND: 0x47** (`00`=OFF, `1F`=ON)
- [ ] **Soft Top Warning Light** enable/disable (for convertible models)
- [ ] **Fuel Tank Size** calibration
- [ ] **Complete dial calibration** interpretation (0xE2-0xED)
- [ ] **New-style feature flags** - OBC, voltmeter, oil pressure locations

If you discover any of these, please contribute!

---

## Mileage Storage

⚠️ **WARNING: Odometer tampering is illegal in most jurisdictions.**

Legitimate uses for mileage transfer:
- Cluster replacement with correct mileage
- Repair of damaged EEPROM
- Classic vehicle restoration

### Mileage Locations

| Cluster Type | Primary Location | Backup Location |
|--------------|------------------|-----------------|
| Old Style (93C56B) | 0x00-0x0F | (single copy) |
| New Style (93C86) | 0x300-0x31F | 0x500-0x51F |

### Transfer Procedure

**Old Style:**
1. Read source cluster, save to file
2. Read destination cluster, save to file
3. Copy bytes 0x00-0x0F from source to destination file
4. Write modified file to destination cluster

**New Style:**
1. Read source cluster, save to file
2. Read destination cluster, save to file
3. Copy bytes 0x300-0x31F AND 0x500-0x51F from source to destination
4. Write modified file to destination cluster

---

## VIN Transfer

### Why Transfer VIN?

- MY2001+ cars: Audio system checks VIN against ECU
- Mismatched VIN = radio won't work

### VIN Transfer Procedure

**Old Style:**
- Copy bytes 0x18-0x1F (row 0x10, cols 08-0F)
- Copy bytes 0x20-0x28 (row 0x20, cols 00-08)

**New Style:**
- Copy bytes 0x000-0x010 (entire first line)

---

## Disassembly for EEPROM Access

### Old Style Cluster

1. Two green sliding connectors on back - slide outward
2. Black clip at bottom (beneath tachometer) - pry up
3. Separate gauges from circuit board
4. EEPROM is on front of board, above center LCD, slightly right of upper-left corner

### New Style Cluster

1. Remove Torx fasteners on back of circuit board
2. Short the crystal legs (prevents processor from starting)
3. EEPROM is above the dot-matrix display, slightly left of center

### EEPROM Chip Identification

Both chips are 8-pin SOIC packages. Pin 1 is marked with a dot or notch.

---

## SOIC Clip Connection

```
Chip Pin 1 (top right when reading markings)
    ↓
    ┌─────┐
    │  •  │ ← Pin 1 indicator
    │     │
    └─────┘

SOIC clip orientation:
- Pin 1 on chip = Pin 1 on clip
- Clip's Pin 1 should align with programmer's Pin 1
```

---

## Software Tools

### Hex Editor

**HxD Hex Editor** (free) - recommended for editing dump files

### Programmer Software

- GQ-4X: GQUSBPrg
- CH341A: AsProgrammer

### Chip Selection in Software

**Old Style:**
- Device menu → ALL → 93C56B (16 BIT)

**New Style:**
- Device menu → ALL → 93C86

### Cluster Analyzer Tool

See `tools/cluster_analyzer.py` for automated dump analysis:

```bash
# Analyze a single dump
python3 tools/cluster_analyzer.py dump.bin

# Compare two dumps (e.g., before/after mileage change)
python3 tools/cluster_analyzer.py dump1.bin --compare dump2.bin
```

---

## Sample Dumps

The `dumps/` folder contains:

### Old Style (93C56B) - 256 bytes

#### Dump Comparison

| Feature | avn_orig (your 986) | rennlist (986 conversion) | illustrated (PDF guide) |
|---------|---------------------|---------------------------|-------------------------|
| **VIN** | WP0CA2986XU624175 | WP0ZZZ98ZYU600985 | WP0AA2995YS623225 |
| **Vehicle Type** | 996 (0996) | **986** (0986) | 996 (0996) |
| **PST2 Mode** | 996 (0x08) | **986** (0x06) | 996 (0x08) |
| **OBC** | ENABLED | ENABLED | ENABLED |
| **Oil Pressure** | ENABLED | ENABLED | ENABLED |
| **Voltmeter** | **DISABLED** | ENABLED | ENABLED |
| **0xE2-E3** | 18 10 | 1B 12 | 1B 12 |
| **0xEB-ED** | E9 66 83 (MPH) | E4 52 94 (KM) | E9 66 83 (MPH) |
| **Speed** | MPH | KM | MPH |
| **Temp** | Celsius | Celsius | ? |
| **Time** | 12hr | ? | ? |

#### Key Observations

1. **986 conversion (rennlist)** - The only one configured as a 986 Boxster:
   - Vehicle type = 0986, PST2 mode = 0x06
   - Speedometer calibration = KM (E4 52 94)

2. **Your original (avn_orig)** - Only dump with voltmeter disabled:
   - Voltmeter = 0x00, 0xE2-E3 = 18 10

3. **0xE2-E3 correlation** - These bytes (`18 10` vs `1B 12`) may correlate with voltmeter state

#### Dump Files

| File | Description |
|------|-------------|
| `eeprom_dump_996_ref_986_rennlist_guide.bin` | 996→986 conversion (UK, KM/Celsius) |
| `eeprom_dump_986_cluster_1999_avn_orig.bin` | Original 986 (MPH/Celsius, 12hr) |
| `eeprom_dump_working_with_eeprom_illustrated.bin` | From Rennlist PDF guide (996) |

### New Style (93C86) - 2048 bytes
| File | Description | Mileage |
|------|-------------|---------|
| `Porsche 911...74336 original dump.bin` | Original 996 | 74,336 mi |
| `Porsche 911...206913 original dump.bin` | Modified mileage | 206,913 mi |

### Reference Images
- `93c56-old-style-hex-dump.jpg` - Raw hex view
- `93c56-old-style-annotated-offsets.jpg` - Annotated offset map

---

## Quick Reference Card (Old Style 93C56B)

```
OFFSET  VALUE           FUNCTION
────────────────────────────────────────────────────
0x00-0F (encrypted)     Mileage (16 bytes)
0x18-1F ASCII           VIN part 1 (8 chars)
0x20-28 ASCII           VIN part 2 (9 chars)
0x35-36 09 86/09 96     Vehicle Type (986/996)
0x3B    06/08           PST2 Mode (986/996)
0x40-4B varies          Market config (UK vs US)
0x47    00/1F           OBC Trip Computer (OFF/ON)
0x49    3C/50           Oil Pressure (ON/OFF)
0x56    01/00           Voltmeter (ON/OFF)
0xE2-E3 1B12/1810       Calibration (voltmeter related?)
0xEB-ED E45294/E96683   Speedometer scaling (KM/MPH?)
```

### 996→986 Conversion Checklist

When converting a 996 cluster to work in a 986:

```
1. Copy mileage:        0x00-0x0F from 986 → 996 cluster
2. Copy VIN:            0x18-0x28 from 986 → 996 cluster
3. Set vehicle type:    0x35-0x36 = 09 86
4. Set PST2 mode:       0x3B = 06
5. Enable OBC:          0x47 = 1F (if desired)
6. Enable oil pressure: 0x49 = 3C
7. Enable voltmeter:    0x56 = 01
```

---

## Acknowledgments

This documentation is based on research by:
- **Gavin Yuill** - Original EEPROM research
- **Shaun Merriman** - New style cluster testing
- **freserf** - OBC enable discovery (BoXa.net, May 2023)
- **KevinH2000** - Rennlist PDF documentation
- **Alex Nesta** - Old style offset mapping & reference images
- **MHH Auto Forum** - Sample dumps

## References

- [Rennlist PDF: Working with the EPROM on Porsche Boxster](https://rennlist.com/forums/attachments/boxster-and-boxster-s-986-forum/1278842d1523504323-programming-a-996-cluster-to-work-in-a-986-working-with-the-eprom-on-porsche-boxster-illustrated-old-and-new-style-clusters-minimum.pdf)
- [BoXa.net Forum - 986 to 996 Gauge Cluster Thread](https://www.boxa.net/)
- [MHH Auto Forum](https://mhhauto.com/)
