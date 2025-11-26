# Instrument Cluster EEPROM Map

## EEPROM Chip Information

| Cluster Style | Years | Chip | Size | Read Mode |
|---------------|-------|------|------|-----------|
| Old Style | MY2000 and earlier | 93C56B | 256 bytes | 16-bit |
| New Style | MY2001 and later | 93C86 | 2048 bytes | 8-bit |

**Recommended Programmer:** Willem GQ-4X (best compatibility)

## Old Style Cluster (93C56B)

### Memory Layout Overview

```
0x00  ┌────────────────────────────────────────┐
      │  ★ MILEAGE (encrypted)                 │  16 bytes, repeated pattern
0x10  ├────────────────────────────────────────┤
      │  ★ VIN                                 │  Starts here, continues...
0x20  │  VIN continues...                      │
      │  0x26-27: Vehicle Type (09 96/09 86)   │
      │  0x2C: PST2 Mode Byte                  │
      │  0x2F: OBC Enable                      │
0x30  ├────────────────────────────────────────┤
      │  0x30-31: Oil Pressure Gauge           │
      │                                        │
      │  ... (other configuration) ...         │
      │                                        │
0x100 └────────────────────────────────────────┘
```

### Key Locations (93C56B) - DETAILED

| Offset | Length | Value | Description |
|--------|--------|-------|-------------|
| 0x00-0x0F | 16 bytes | (encrypted) | **Mileage** - encrypted, repeated pattern |
| 0x10-0x20 | ~17 bytes | ASCII | **VIN** - starts mid-line 0x10 |
| 0x26-0x27 | 2 bytes | `09 96` or `09 86` | **Vehicle Type** - 996 or 986 |
| 0x2C | 1 byte | `7A` or `78` | **PST2 Mode** - `7A`=986 mode, `78`=996 mode |
| 0x2F | 1 byte | `00` or `1F` | **OBC Enable** - `00`=OFF, `1F`=ON |
| 0x30-0x31 | 2 bytes | `0x??` or `50??` | **Oil Pressure Gauge** - `0x`=Enable, `50`=Disable |

### Vehicle Type (0x26-0x27)

This tells the cluster what car it's installed in:
- `09 96` = 996 Carrera
- `09 86` = 986 Boxster

### PST2 Mode Byte (0x2C)

This "mystery byte" affects how PST2/PIWIS diagnostic tools interact with the cluster:
- `7A` = 986 Boxster mode
- `78` = 996 Carrera mode

If your 996 cluster doesn't behave correctly with PST2 after install in a 986, try changing this byte.

### OBC Enable (0x2F)

The On-Board Computer (trip computer) enable flag:
- `00` = OBC disabled
- `1F` = OBC enabled

This is independent of the DME - it's purely a cluster setting.

### Oil Pressure Gauge (0x30-0x31)

Controls whether the oil pressure gauge is active:
- First nibble `0x` = Enabled
- First nibble `50` = Disabled

### VIN Location Detail

The VIN is stored spanning two lines:
- Starts at the middle of line 0x10
- Ends in the first half of line 0x20
- Plus one character into the second half of line 0x20

### Byte Swapping Note (Important!)

The GQ-4X programmer reads/writes with bytes swapped:
1. When you first read, the VIN will look garbled
2. Click the **A-B swap icon** to read the VIN correctly
3. Make your edits with bytes swapped (VIN readable)
4. **Un-swap** (click A-B again) before writing back to chip
5. The file you write should have the VIN looking garbled again

## New Style Cluster (93C86)

### Memory Layout Overview

```
0x000  ┌────────────────────────────────────────┐
       │  ★ VIN (first line)                    │
0x010  ├────────────────────────────────────────┤
       │  Model code, configuration...          │
       │                                        │
       │         ... (configuration) ...        │
       │                                        │
0x300  ├────────────────────────────────────────┤
       │  ★ MILEAGE (encrypted) - PRIMARY       │  32 bytes
0x320  ├────────────────────────────────────────┤
       │                                        │
       │         ... (other data) ...           │
       │                                        │
0x500  ├────────────────────────────────────────┤
       │  ★ MILEAGE (encrypted) - BACKUP        │  32 bytes
0x520  ├────────────────────────────────────────┤
       │                                        │
0x800  └────────────────────────────────────────┘
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

## Feature Enable Flags Summary

| Feature | Old Style Offset | Old Style Values | New Style |
|---------|------------------|------------------|-----------|
| **OBC (Trip Computer)** | 0x2F | `00`=OFF, `1F`=ON | TBD |
| **Oil Pressure Gauge** | 0x30-0x31 | `0x`=ON, `50`=OFF | TBD |
| **Vehicle Type** | 0x26-0x27 | `09 96`/`09 86` | 0x010+ area |
| **PST2 Mode** | 0x2C | `7A`=986, `78`=996 | TBD |
| **Voltmeter** | TBD | TBD | TBD |
| **Top Operation Warning** | TBD | TBD | TBD |

## Mileage Storage

⚠️ **WARNING: Odometer tampering is illegal in most jurisdictions.**

Legitimate uses for mileage transfer:
- Cluster replacement with correct mileage
- Repair of damaged EEPROM
- Classic vehicle restoration

### Mileage Format

- **Encrypted** in both cluster types
- Cannot be read directly as a number
- Copy entire mileage block when transferring between clusters

### Mileage Locations

| Cluster Type | Primary Location | Backup Location |
|--------------|------------------|-----------------|
| Old Style (93C56B) | 0x00-0x0F | (same block, repeated) |
| New Style (93C86) | 0x300-0x31F | 0x500-0x51F |

### Transfer Procedure

To transfer mileage from one cluster to another:

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

## VIN Transfer

### Why Transfer VIN?

- MY2001+ cars: Audio system checks VIN against ECU
- Mismatched VIN = radio won't work

### VIN Transfer Procedure

**Old Style:**
1. Copy second half of line 0x10 from source
2. Copy first half of line 0x20 from source
3. Copy first character of second half of line 0x20

**New Style:**
1. Copy bytes 0x000-0x00F (entire first line)

## Model Code

The model identifier tells the cluster which vehicle it's in:

| Code | Model |
|------|-------|
| `09 96` | 996 Carrera |
| `09 86` | 986 Boxster |

**Old Style:** Located at 0x26-0x27
**New Style:** Located in 0x010-0x02F area

This affects:
- PIWIS/PST2 menu access
- Some gauge behaviors
- Possibly fuel tank calibration

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

## Sample Dumps

The `dumps/` folder contains:
- 93C86 dump at 74,336 miles
- 93C86 dump at 206,913 miles (same VIN, different mileage)
- Reference images showing offset annotations

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
