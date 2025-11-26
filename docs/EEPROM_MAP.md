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
Line 0x00  ┌────────────────────────────────────────┐
           │  MILEAGE (encrypted, repeated values)  │
Line 0x10  ├────────────────────────────────────────┤
           │  VIN starts mid-line ──────────────────│
Line 0x20  │──────────── VIN ends + padding         │
Line 0x30  ├────────────────────────────────────────┤
           │  Configuration / Feature Flags         │
           │                                        │
           │  Position 0x2F (47): OBC Enable        │
           │     00 = OFF                           │
           │     1F = ON                            │
           │                                        │
           └────────────────────────────────────────┘
```

### Key Locations (93C56B)

| Offset | Length | Description |
|--------|--------|-------------|
| 0x00 | 16 bytes | Mileage (encrypted, repeated values) |
| 0x10-0x20 | ~17 bytes | VIN (starts mid-line 0x10, ends early line 0x20) |
| 0x2F | 1 byte | OBC Enable: `00`=OFF, `1F`=ON |

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
Line 0x000 ┌────────────────────────────────────────┐
           │  VIN (stored in first line)            │
Line 0x010 ├────────────────────────────────────────┤
           │  Model code: "09 96" or "09 86"        │
Line 0x020 │  (plain text, affects PIWIS access)    │
           │                                        │
           │         ... (configuration) ...        │
           │                                        │
Line 0x300 ├────────────────────────────────────────┤
           │  MILEAGE (encrypted) - copy 1          │
Line 0x310 │  (continued)                           │
           │                                        │
           │         ... (other data) ...           │
           │                                        │
Line 0x500 ├────────────────────────────────────────┤
           │  MILEAGE (encrypted) - copy 2          │
Line 0x510 │  (continued)                           │
           └────────────────────────────────────────┘
```

### Key Locations (93C86)

| Offset | Description |
|--------|-------------|
| 0x000 | VIN (first line) |
| 0x010-0x020 | Model code "09 96" or "09 86" |
| 0x300-0x310 | Mileage (encrypted) - PRIMARY |
| 0x500-0x510 | Mileage (encrypted) - BACKUP |

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

## Feature Enable Flags

### OBC (On-Board Computer)

| Cluster | Location | OFF | ON |
|---------|----------|-----|-----|
| Old Style (93C56B) | Position 0x2F | `00` | `1F` |
| New Style (93C86) | TBD | TBD | TBD |

The OBC provides trip computer functions and is a cluster-only setting (not DME dependent).

### Additional Feature Flags (Research Needed)

| Feature | Old Style | New Style | Status |
|---------|-----------|-----------|--------|
| Oil Pressure Gauge | ? | ? | Needs research |
| Voltmeter | ? | ? | Needs research |
| Top Operation Warning | ? | ? | Needs research |

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

### Transfer Procedure

To transfer mileage from one cluster to another:

**Old Style:**
1. Read source cluster, save to file
2. Read destination cluster, save to file
3. Copy line 0x00 (mileage) from source to destination file
4. Write modified file to destination cluster

**New Style:**
1. Read source cluster, save to file
2. Read destination cluster, save to file
3. Copy lines 0x300-0x310 AND 0x500-0x510 from source to destination
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
1. Copy entire first line (0x000)

## Model Code (New Style Only)

The model identifier is stored as plain text:
- `09 96` = 996 Carrera
- `09 86` = 986 Boxster

This affects PIWIS/PST2 menu access. If using a 996 cluster in a 986, you may need to select 996 in the PIWIS menu system to access instrument commands.

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

## Acknowledgments

This documentation is based on research by:
- **Gavin Yuill** - Original EEPROM research
- **Shaun Merriman** - New style cluster testing
- **freserf** - OBC enable discovery (BoXa.net, May 2023)
- **KevinH2000** - Rennlist PDF documentation

## References

- [Rennlist PDF: Working with the EPROM on Porsche Boxster](https://rennlist.com/forums/attachments/boxster-and-boxster-s-986-forum/1278842d1523504323-programming-a-996-cluster-to-work-in-a-986-working-with-the-eprom-on-porsche-boxster-illustrated-old-and-new-style-clusters-minimum.pdf)
- [BoXa.net Forum - 986 to 996 Gauge Cluster Thread](https://www.boxa.net/)
