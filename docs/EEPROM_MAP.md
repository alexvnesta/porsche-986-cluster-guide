# Instrument Cluster EEPROM Map (`93C56B` & `93C86`)

Complete memory map, bit-level coding reference, gauge calibration tables, and dump comparison for Porsche 986 Boxster and 996 911 instrument clusters (`Kombiinstrument`).

---

## 1. EEPROM Chip Overview

| Cluster Generation | Model Years | DSN Range | EEPROM Chip | Size | Native Organization | OBD K-Line Read (`0x23`) |
|---|---|---|---|---|---|---|
| **Old Style (Early)** | MY1997–2000 (986)<br>MY1998–2000 (996) | `K02`–`K17` | **Microchip 93C56B** (SOIC-8) | **256 bytes** (`0x00–0xFF`) | 16-bit (`128 × 16`) — requires byte-swap in GQ-4X | Not supported (SOIC-8 clip or desolder required) |
| **New Style (`Kombi 2000`)** | MY2001–2004 (986)<br>MY2001–2005 (996) | `K20`–`K50` | **Microchip 93C86** (SOIC-8) | **2048 bytes** (`0x000–0x7FF`) | 8-bit linear (`2048 × 8`) — native byte order | **Supported** via KWP2000 `23 08 xx xx 10` at `0x080000–0x0807FF` (RAM shadow; see [Section 3.12](#312-mileage-storage--dynamic-ram-shadow-caveats-0x300--0x500)) |

**Recommended Hardware Programmer:** Willem GQ-4X or CH341A (with 3.3V/5V adapter and SOIC-8 test clip) for offline chip access, or a standard **FTDI FT232RL KKL interface (OBD-II Pin 3)** for non-invasive KWP2000 reading and coding on MY2001+ clusters.

---

## 2. Old Style Cluster (`93C56B`) — 256 Bytes (MY1997–2000)

### 2.1 Memory Layout Overview

```text
         00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
        ┌───────────────────────────────────────────────┐
0x00    │ ★ MILEAGE (encrypted, 16 bytes)               │
        ├───────────────────────────────────────────────┤
0x10    │                         │ ★ VIN starts ────── │
        ├─────────────────────────┼─────────────────────┤
0x20    │ ── VIN continues ────── │                     │
        ├───────────────────────────────────────────────┤
0x30    │          │09 86│       │PST2│               │ │
        │          │or   │       │mode│               │ │
        │          │09 96│       │    │               │ │
        ├───────────────────────────────────────────────┤
0x40    │                   │OBC │ │OIL │               │
        │                   │0x47│ │PRES│               │
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

### 2.2 Key Locations (`93C56B`) — Detailed

| Row | Column | Offset | Value | Description |
|-----|--------|--------|-------|-------------|
| `0x00` | `00–0F` | `0x00–0x0F` | (encrypted) | **Mileage** — 16 bytes, encrypted |
| `0x10` | `08–0F` | `0x18–0x1F` | ASCII | **VIN** (first part, 8 characters) |
| `0x20` | `00–08` | `0x20–0x28` | ASCII | **VIN** (second part, 9 characters) |
| `0x30` | `05–06` | `0x35–0x36` | `09 86` / `09 96` | **Vehicle Type** (`09 86` = 986 Boxster, `09 96` = 996 Carrera) |
| `0x30` | `0B` | `0x3B` | `06` / `08` | **PST2 Diagnostic Mode** (`06` = 986 mode, `08` = 996 mode) |
| `0x40` | `07` | `0x47` | `00` / `1F` | **OBC (On-Board Computer)** (`00` = OFF, `1F` = ON) |
| `0x40` | `09` | `0x49` | `3C` / `50` | **Oil Pressure Gauge** (`3C` = ON, `50` = OFF) |
| `0x50` | `06` | `0x56` | `01` / `00` | **Voltmeter** (`01` = ON, `00` = OFF) |
| `0xE0` | `02–0D` | `0xE2–0xED` | varies | **Dial Calibration** data (12 bytes) |

### 2.3 Field Descriptions (`93C56B`)

#### Mileage (`0x00–0x0F`)
- 16 bytes of encrypted mileage data.
- To transfer mileage when swapping an early cluster: copy the entire 16-byte block `0x00–0x0F` from the source cluster to the destination cluster.

#### VIN Location (`0x18–0x28`)
The 17-character ASCII VIN spans two rows:
- **Row `0x10`, columns `08–0F` (`0x18–0x1F`):** First 8 characters of VIN.
- **Row `0x20`, columns `00–08` (`0x20–0x28`):** Remaining 9 characters of VIN.

#### Vehicle Type (`0x35–0x36`) & PST2 Mode Byte (`0x3B`)

| Offset | 986 Boxster | 996 Carrera | Purpose |
|---|---|---|---|
| `0x35–0x36` | `09 86` | `09 96` | Tells the cluster which vehicle platform it is installed in |
| `0x3B` | `06` | `08` | Configures how PST2/PIWIS diagnostic tools identify the cluster |

If a 996 cluster retrofitted into a 986 does not behave properly with dealer diagnostic tools or fuel tank curves, verify that `0x35–0x36 = 09 86` and `0x3B = 06`.

#### Feature Enable Flags (`0x47`, `0x49`, `0x56`)

| Feature | Offset | Enable | Disable | Notes |
|---|---|---|---|---|
| **OBC (Trip Computer)** | `0x47` | `1F` | `00` | Enables average speed, average consumption, range, and outside temperature |
| **Oil Pressure Gauge** | `0x49` | `3C` | `50` | Enables the 5-bar oil pressure gauge on 5-pod 996 clusters |
| **Voltmeter** | `0x56` | `01` | `00` | Enables the battery voltmeter gauge on 5-pod 996 clusters |

#### Market Configuration & Dial Calibration (`0x40–0x4F` & `0xE2–0xED`)

Comparison of UK (km/°C) vs. US (Miles/°F) 93C56B dumps:

```text
UK (KM/C):   34 5D 00 FB 99 F6 16 1F 0B 3C 78 BC FF FF FF FF
US (Mi/F):   18 60 02 FC 66 F6 26 1F 0B 3C 78 61 FF FF FF FF
                                  ^^    ^^
                             OBC (0x47) Oil Pressure (0x49)
```

| Offset | UK (`KM/°C`) | US (`Miles/°F`) | Notes |
|---|---|---|---|
| `0x40–0x41` | `34 5D` | `18 60` | Market / unit configuration |
| `0x44` | `99` | `66` | Market configuration |
| `0x46` | `16` | `26` | Market configuration |
| `0x4B` | `BC` | `61` | Market configuration |
| `0xE2–0xE3` | `1B 12` | `18 10` | Correlates with voltmeter state (`1B 12` when voltmeter enabled, `18 10` when disabled) |
| `0xE4–0xEA` | `00 00 AF 00 EC 09 E4` | `00 00 AF 00 EC 09 E4` | Common gauge calibration bytes |
| `0xEB–0xED` | `E4 52 94` | `E9 66 83` | Speedometer scaling (`E4 52 94` = km/h, `E9 66 83` = mph) |

#### Byte Swapping Note (`93C56B` 16-bit Mode)
When reading a 93C56B in 16-bit mode on a Willem GQ-4X programmer:
1. On initial read, adjacent bytes in each 16-bit word appear swapped (the VIN looks garbled, e.g., `PWZ0ZZ...`).
2. Click the **A-B swap** icon in the programmer software to view and edit the VIN and offsets in natural order.
3. Click **A-B swap** again before writing back to the physical chip if your programmer expects word-swapped 16-bit buffers.

---

## 3. New Style Cluster (`93C86` — "Kombi 2000") — 2048 Bytes (MY2001–2005)

On MY2001+ clusters (`DSN K20` and newer), VDO migrated to a **2048-byte (`0x000–0x7FF`) 93C86 EEPROM** organized in **native 8-bit linear byte order**.

> **Byte Order Note (`8-bit` vs. `16-bit` Programmer Reads):**
> When read over the vehicle's K-line diagnostic port (`Service 0x23` at `0x080000`) or with an EEPROM programmer set to **8-bit mode**, the 93C86 is in native linear byte order (`0x000` starts with `W P 0 ...`). If a 93C86 is read with an external programmer accidentally set to **16-bit mode**, every pair of bytes is swapped (`0x000` starts with `P W Z 0 ...`). Always work in native 8-bit order; [`tools/cluster_analyzer.py`](../tools/cluster_analyzer.py) automatically detects and unswaps 16-bit dumps.

### 3.1 Complete 93C86 Memory Map (`0x000–0x7FF`)

```text
Offset          Size    KWP2000 Read / Write           Description
──────────────────────────────────────────────────────────────────────────────────────────────────────
0x000–0x010     17 B    Read: 1A 90 / Write: 3B 90     VIN (Vehicle Identification Number, ASCII)
0x011–0x01C     12 B    Read: 1A 80 / 1A 92            VDO Hardware & Blank Number Metadata
0x01D–0x022      6 B    Read: 1A 9E                    Porsche Part Number (6-byte BCD, e.g. 09 86 64 12 17 00)
0x023            1 B    Read: 1A 9F                    DSN (Datensatznummer: 0x15=K21, 0x17=K23, 0x18=K24, 0x1A=K26)
0x024–0x031     14 B    Read: 1A 9F / internal         Dataset Sub-version & Checksum Constants
0x032–0x039      8 B    Read: 30 01 01 / Write: 30 01 08  Parameterkodierung (Equipment, OBC, Chimes, Tell-Tales)
0x03A–0x041      8 B    Read: 30 01 02 / Write: 30 01 09  Menükonfiguration (Default & Knob-Twist Display Units)
0x042–0x045      4 B    Internal                       Display / Trip Computer Range Mask (18 3F 06 3F on 986)
0x050            1 B    Read: 21 73 / Write: 3B 73     Spoiler Retract Speed Threshold (km/h, default 0x50 = 80 km/h)
0x051            1 B    Read: 21 72 / Write: 3B 72     Spoiler Extend Speed Threshold (km/h, default 0x78 = 120 km/h)
0x052–0x053      2 B    Read: 21 70 / Write: 3B 70     K-Zahl (Pulses/km, uint16 LE: FA 5C = 23,802 Imp./km)
0x054–0x055      2 B    Read: 21 71 / Write: 3B 71     Factory Threshold Constants (78 64 = [120, 100])
0x056            1 B    Read: 21 74 / Write: 3B 74     Fuel Tank Calibration Offset (Tankabgleichwert, 0x4E; reset=0x00)
0x0D4–0x0DF     12 B    Read: 1A 95 / 1A 99            VDO Factory Production / Flash Timestamps #1 & #2 (BCD)
0x0E5–0x0E7      3 B    Read: 1A 93                    Software / Diagnostic Version Index (e.g. 22 05 01 / 35 48 01)
0x0F0–0x0F5      6 B    Read: 1A 9A                    VDO Factory Production / Test Timestamp #3 (BCD)
0x168–0x17F     24 B    Read: 21 77                    12-Point Analog Sensor Linearization Curve (12 × uint16 LE)
0x184–0x18D     10 B    Read: 21 78 01                 Secondary Speedometer Stepper Curve (5 × uint16 LE)
0x192–0x19B     10 B    Read: 21 78 00 / Write: 3B 78 00  Primary Speedometer Stepper Calibration Curve (5 × uint16 LE)
0x19C–0x1FF    100 B    Internal                       Tachometer, Coolant Temp & Oil Pressure Stepper Curves
0x202–0x20D     12 B    Read: 21 7C / Write: 3B 7C     Fuel Tank Calibration Curve Z (6 × uint16 LE)
0x21A–0x225     12 B    Read: 21 75 / Write: 3B 75     Fuel Tank Sender Resistance Curve X (6 × uint16 LE, 0.1 Ω)
0x226–0x235     16 B    Read: 21 7B / Write: 3B 7B     Fuel Tank Volume Curve Y (16 bytes, Liters)
0x2C6            1 B    Internal                       LCD Operating Voltage / Contrast Bias (0x21 on 986, 0x20 on 996)
0x300–0x31F     32 B    Read: 21 10 (decoded km)       Primary Encrypted Odometer Block (32 bytes)
0x380–0x3AD     46 B    Read: 21 76 00..07 / 3B 76 ..  Oil Level Sensor Characteristic Curve (8 sub-blocks, 46 bytes)
0x40A–0x40D      4 B    Internal                       Active Key Menu Configuration Shadow (mirrors 0x03E–0x041)
0x500–0x51F     32 B    Internal                       Backup Encrypted Odometer Block (32 bytes)
0x600–0x643     68 B    Read: 18 FF FF 01 / 02         Fault Memory (DTC) Storage Records & Freeze Frames
0x644–0x65B     24 B    Read: 21 31 00..0B             Event Memory Odometer History (12 × 2-byte records)
0x6F4–0x6F5      2 B    Read: 21 30 / Clear: 31 30     Event Memory Active Warning Bitmask (12 flags)
```

---

### 3.2 Identification Fields (`0x000–0x02F`, `0x0D4–0x0F5`)

| Offset | Length | K21 Dump (`986.641.217.00`) | K24 Dump (`986.641.237.00`) | K23 Dump (`996.641.227.00`) | Decoding Rule |
|---|---|---|---|---|---|
| `0x000–0x010` | 17 B | `WP0ZZZ98Z1S6XXXXX` | `WP0ZZZ98Z2U6XXXXX` | `WP0ZZZ99Z2S603304` | 17-character ASCII VIN (`1A 90` / `3B 90`) |
| `0x01D–0x022` | 6 B | `09 86 64 12 17 00` | `09 86 64 12 37 00` | `09 96 64 12 27 00` | Packed BCD Porsche part number (`1A 9E`): `0986.641.217.00` |
| `0x023` | 1 B | `0x15` (**K21**) | `0x18` (**K24**) | `0x17` (**K23**) | `DSN = "K" + str(byte_0x23)` (`1A 9F`): `0x15`=21, `0x17`=23, `0x18`=24, `0x1A`=26 |
| `0x0D4–0x0D9` | 6 B | `05 02 01 07 27 48` | `14 01 02 18 10 42` | `02 12 01 15 32 46` | VDO BCD Timestamp #1 (`DD MM YY HH MM SS`): `2001-02-05 07:27:48` (K21) |
| `0x0DA–0x0DF` | 6 B | `07 02 01 13 30 54` | `29 01 02 11 03 54` | `06 12 01 11 56 50` | VDO BCD Timestamp #2 (`1A 99`): Factory assembly / test timestamp |
| `0x0E5–0x0E7` | 3 B | `22 05 01` | `35 48 01` | `18 48 01` | Firmware / Dataset revision index (`1A 93`) |
| `0x0F0–0x0F5` | 6 B | `05 02 01 19 50 23` | `17 01 02 14 51 19` | `05 12 01 06 10 06` | VDO BCD Timestamp #3 (`1A 9A`): Final end-of-line calibration timestamp |

---

### 3.3 `Parameterkodierung` — Equipment & Warning Drivers (`0x032–0x039`)

- **EEPROM Offset:** `0x032–0x039` (8 bytes: Byte 0 .. Byte 7)
- **KWP2000 Read:** `30 01 01` → returns `70 01 01 <8 bytes>`
- **KWP2000 Write:** `30 01 08 <8 bytes>` → returns `70 01 08 <8 bytes>`
- **Verified Factory Baselines:**
  - **986 Boxster / Boxster S (`K21` / `K24` / `K26`, Manual, OBC, Non-PSM, UK/RDW):** `84 02 1F 00 B5 07 00 00`
  - **996 Carrera 2 (`K23`, Manual, OBC, Non-PSM, UK):** `84 03 1F 10 B5 02 00 00`

#### Complete Bit-Level Decoding Table (`0x032–0x039`)

| Byte | EEPROM Offset | Bit(s) | Hex Mask | Meaning & Values | Factory 986 (`K21/K24`) | Factory 996 (`K23`) |
|---|---|---|---|---|---|---|
| **Byte 0** | `0x032` | Bit 0 | `0x01` | Reserved (`0`) | `0` | `0` |
| | | **Bits 1, 3, 4** | **`0x1A`** (`0x02\|0x08\|0x10`) | **PSM / Brake System Type:**<br>`0x00` = **Without PSM (Bosch ABS 5.3)** — uses discrete mechanical handbrake switch on `Plug B Pin 22`<br>`0x1A` (or `0x10`) = **With PSM (Bosch PSM 5.7)** — expects brake/PSM status over CAN Antrieb | `0` (Non-PSM) | `0` (Non-PSM) |
| | | **Bit 2** | **`0x04`** | **Factory VDO Base Config Bit A** *(Must remain `1`)* | `1` (`0x04`) | `1` (`0x04`) |
| | | Bits 5–6 | `0x60` | Tank / Chassis variant (`00b` = standard 64L tank) | `00b` | `00b` |
| | | **Bit 7** | **`0x80`** | **Factory VDO Base Config Bit B** *(Must remain `1`)* | `1` (`0x80`) | `1` (`0x80`) |
| **Byte 1** | `0x033` | **Bit 0** | **`0x01`** | **Model Platform / 5-Gauge Pod Enable:**<br>`0` = 986 Boxster (3-dial cluster)<br>`1` = 996 Carrera / Turbo (5-dial cluster with Oil Pressure & Voltmeter) | `0` (`0x02`) | `1` (`0x03`) |
| | | **Bit 1** | **`0x02`** | **Factory Powertrain / Manual Baseline Bit** *(1 on factory 986 & 996 dumps)* | `1` (`0x02`) | `1` (`0x02`) |
| | | **Bit 2** | **`0x04`** | **PCM / CDR23 / MOST Bus Installed:** `0` = No MOST/PCM, `1` = Installed | `0` | `0` |
| | | **Bit 5** | **`0x20`** | **Cruise Control (`Tempostat`) Indicator:** `0` = Disabled, `1` = Enabled (green lamp in tach) | `0` | `0` |
| **Byte 2** | `0x034` | **Bit 0** | **`0x01`** | **On-Board Computer (OBC) Master Enable:** `1` = Active, `0` = Inactive | `1` | `1` |
| | | **Bit 1** | **`0x02`** | **OBC Menu — Outside Temperature:** `1` = Active | `1` | `1` |
| | | **Bit 2** | **`0x04`** | **OBC Menu — Average Speed (`Ø km/h` / `Ø mph`):** `1` = Active | `1` | `1` |
| | | **Bit 3** | **`0x08`** | **OBC Menu — Average Consumption (`Ø MPG` / `Ø l/100km`):** `1` = Active | `1` | `1` |
| | | **Bit 4** | **`0x10`** | **OBC Menu — Remaining Range (`Reichweite`):** `1` = Active *(Full 986/996 Carrera OBC = `0x1F`)* | `1` (`0x1F`) | `1` (`0x1F`) |
| | | **Bit 5** | **`0x20`** | **OBC Menu — Turbo Boost Pressure (`Ladedruck`):** `1` = Active *(996 Turbo / GT2 `K22` only; `0` on NA cars)* | `0` | `0` |
| | | **Bits 6–7** | **`0xC0`** | **OBC Master Inhibit (Inverted):** `00b` when OBC enabled (`0x1F`); `11b` (`0xC0`) when OBC disabled | `00b` | `00b` |
| **Byte 3** | `0x035` | Bit 0 | `0x01` | Audio / Radio station display menu in center LCD (`1` = Active) | `0` | `0` |
| | | Bit 1 | `0x02` | Telephone display menu in center LCD (`1` = Active) | `0` | `0` |
| | | Bit 2 | `0x04` | Navigation display menu in center LCD (`1` = Active) | `0` | `0` |
| | | Bit 3 | `0x08` | Voice control (`Sprachbedienung`) menu (`1` = Active) | `0` | `0` |
| | | Bit 4 | `0x10` | 996 Oil Level / Carrera menu flag (`1` on 996 K23, `0` on 986) | `0` (`0x00`) | `1` (`0x10`) |
| **Byte 4** | `0x036` | **Bit 0** | **`0x01`** | **Tell-Tale Driver Baseline Bit 0** *(Factory = `1`)* | `1` | `1` |
| | | **Bit 1** | **`0x02`** | **Acoustic Seatbelt Chime (USA / Canada):** `0` = Off (RDW/UK), `1` = On (USA) | `0` | `0` |
| | | **Bit 2** | **`0x04`** | **Tell-Tale Driver Baseline Bit 2** *(Factory = `1`)* | `1` | `1` |
| | | **Bit 3** | **`0x08`** | **Ignition Key-in-Lock Acoustic Chime (USA):** `0` = Off (RDW/UK), `1` = On | `0` | `0` |
| | | **Bits 4–5** | **`0x30`** | **Airbag / SRS & Seatbelt Tell-Tale Driver Enable** *(Factory = `11b` = `0x30`)* | `11b` | `11b` |
| | | **Bit 6** | **`0x40`** | **120 km/h Speed Warning Chime (Gulf / Saudi States):** `0` = Off, `1` = On | `0` | `0` |
| | | **Bit 7** | **`0x80`** | **Lights-On Warning Buzzer & Driver Master Enable** *(Factory = `1`; full RDW/UK byte = `0xB5`)* | `1` (`0xB5`) | `1` (`0xB5`) |
| **Byte 5** | `0x037` | **Bit 0** | **`0x01`** | **Rear Spoiler Warning Logic Active:** `1` = Active (`0x07` on 986), `0` = Off on 996 (`0x02`) | `1` (`0x07`) | `0` (`0x02`) |
| | | **Bits 1–2** | **`0x06`** | **Body / Roof / Spoiler Profile Bits:** `11b` (`0x06`) on 986 Boxster, `01b` (`0x02`) on 996 Coupe | `11b` | `01b` |
| | | **Bit 4** | **`0x10`** | **Euro NCAP Seatbelt Acoustic Warning (`DSN K26+`):** `0` = Off, `1` = On | `0` | `0` |
| **Bytes 6–7** | `0x038–0x039` | All | `0xFF` | Reserved (`00 00` on all verified 986/996 dumps) | `00 00` | `00 00` |

---

### 3.4 Warning Lamp Drivers, PSM Handbrake Logic & How Bad Coding Breaks Tell-Tales

A critical architectural detail of the 93C86 `Parameterkodierung` (`0x032–0x039`) is that **user-configurable option bits share the same 8 bytes as VDO's internal hardware driver configuration bits** (`0x84` in Byte 0, `0x02`/`0x03` in Byte 1, `0xB5` in Byte 4, and `0x07`/`0x02` in Byte 5).

This does **not** fail during normal vehicle operation. However, two common custom-software mistakes will corrupt this block and cause baffling hardware symptoms:

1. **Building a coding payload from `00 00 00 00 00 00 00 00` instead of Read-Modify-Write:**
   - If a custom coding script only populates the bits it knows about (such as OBC `0x034 = 0x1F`) and leaves the "undocumented" baseline bits at `0x00`, or if a tool sends `30 01 08` without a data payload (which causes the cluster firmware to write stale K-line receive-buffer bytes into EEPROM — see [DIAGNOSTICS.md](DIAGNOSTICS.md)), the factory baseline bits in `0x032` and `0x036` get overwritten.
2. **Symptom 1 — Zeroing Byte 4 (`0x036 = 0x00` instead of `0xB5`): Dead Airbag & Seatbelt Key-On Bulb Check:**
   - Byte `0x036` (`0xB5 = 1011 0101b`) enables the cluster microcontroller's internal solid-state low-side lamp drivers and acoustic chime triggers.
   - When `0x036` is overwritten with `0x00`, the **Airbag (`SRS`) warning lamp remains completely dark at ignition key-on (no 4-second bulb-check sweep)**, the seatbelt tell-tale stops working, and the headlights-left-on door chime goes silent — even though the LEDs/bulbs, wiring, and Airbag ECU are physically fine.
   - Restoring `0x036` to `0xB5` (and `0x032` to `0x84`) immediately restores the key-on Airbag bulb-check and chimes.
3. **Symptom 2 — Setting PSM Bit (`0x032 = 0x10`) on a Non-PSM Car: Dead Handbrake Warning Light & DTC `5555`:**
   - On a non-PSM car (Bosch ABS 5.3), the red **(!) Brake / Handbrake warning lamp** is triggered directly by the mechanical handbrake lever switch grounding `Plug B Pin 22`.
   - If Bit 4 of `0x032` (`0x10`) is accidentally set, the cluster switches to PSM mode (`Bosch PSM 5.7`), ignores the physical handbrake switch input on `B22`, and waits for a CAN message from a PSM controller that does not exist — disabling the handbrake warning light and logging DTC `5555` (*CAN timeout ABS*).

> **Safety Rule on Airbag Verification:**
> Restoring `0x036 = 0xB5` so that the Airbag lamp performs its key-on bulb-check only proves that the **cluster's internal lamp driver** is working again. Complete verification requires confirming that:
> 1. The Airbag lamp illuminates at ignition ON and extinguishes after ~4 seconds, **and**
> 2. The **Airbag control unit (`POSIP / Bosch AB6.2`, K-line target address `0x15` on OBD Pin 3, powered via Ignition Switch Terminal 86S / Fuse E1)** responds to diagnostics and reports zero stored fault codes.

---

### 3.5 `Menükonfiguration` — Display Units & Right-Knob Toggle (`0x03A–0x041`)

- **EEPROM Offset:** `0x03A–0x041` (8 bytes: two 4-byte halves)
  - **Bytes `0..3` (`0x03A–0x03D`):** **Primary / Default Display State** (active at ignition on).
  - **Bytes `4..7` (`0x03E–0x041`):** **Secondary Display State** (active when the user twists the right-hand cluster knob to toggle units, e.g., between `MPH` and `km/h`; also mirrored in active key shadow `0x40A–0x40D`).
- **KWP2000 Read:** `30 01 02` → returns `70 01 02 <8 bytes>`
- **KWP2000 Write:** `30 01 09 <8 bytes>` → returns `70 01 09 <8 bytes>`

#### Bit-Level Decoding Table (`0x03A–0x041`)

| Byte in Half | EEPROM Offset (Half 1 / Half 2) | Bit(s) | Hex Mask | Parameter & Values |
|---|---|---|---|---|
| **Byte 0** | `0x03A` / `0x03E` | **Bits 0–2** | `0x07` | **OBC Display Language:**<br>`0` = German (`Deutsch`)<br>`1` = English<br>`2` = French (`Français`)<br>`3` = Italian (`Italiano`)<br>`4` = Spanish (`Español`)<br>`5` = Japanese |
| | | **Bits 3–4** | `0x18` | **Fuel Consumption Unit (`Consumption << 3`):**<br>`0` (`0x00`) = **`l/100km`** (Europe / RDW)<br>`1` (`0x08`) = **`km/l`** (Japan)<br>`2` (`0x10`) = **`MPG (US)`** (USA)<br>`3` (`0x18`) = **`MPG (UK Imperial)`** (UK)<br>*(Example: English `0x01` + UK MPG `0x18` = **`0x19`**)* |
| | | Bits 5–7 | `0xE0` | Tire Pressure Monitoring (`RDK`) display flags (`0` on 986/996) |
| **Byte 1** | `0x03B` / `0x03F` | Bit 0 | `0x01` | Market unit profile flag (`0x01` on factory UK dumps, `0x00` on RDW dumps) |
| **Byte 2** | `0x03C` / `0x040` | **Bit 0** | **`0x01`** | **Distance (Odometer/Trip) & Digital Speedometer Unit:**<br>`0` = **Miles (`mi`) & `MPH`**<br>`1` = **Kilometers (`km`) & `km/h`** |
| | | Bit 1 | `0x02` | Voice control status (`0` = Off) |
| | | **Bit 2** | **`0x04`** | **Outside Temperature Unit:**<br>`0` = **Fahrenheit (`°F`)**<br>`1` = **Celsius (`°C`)** |
| | | **Bit 3** | **`0x08`** | **Digital Clock Format:**<br>`0` = **12-hour (`AM/PM`)**<br>`1` = **24-hour (`24h`)** |
| | | Bit 5 | `0x20` | Telephone info display (`0` = Off) |
| **Byte 3** | `0x03D` / `0x041` | All | `0xFF` | Reserved (`0x00`) |

#### Verified `Menükonfiguration` Presets (`0x03A–0x041`)

| Market / Profile | 8-Byte Hex (`0x03A–0x041`) | Default Display (Half 1) | Right-Knob Twist (Half 2) |
|---|---|---|---|
| **UK Ideal (24h Clock + MPH/km/h Knob Toggle)** | `19 01 0C 00 19 01 0D 00` | English, **MPH / Miles**, UK MPG, °C, **24h clock** (`0x0C`) | Twisting right knob toggles digital speedo to **km/h** (`0x0D`) for European driving |
| **Factory UK Baseline (12h Clock, Locked MPH)** | `19 01 04 00 19 01 04 00` | English, **MPH / Miles**, UK MPG, °C, **12h clock** (`0x04`) | Remains in **MPH** (`0x04`) when knob is twisted |
| **Factory Continental Europe (RDW)** | `00 00 0C 00 00 00 0D 00` | German, **MPH/km/h** toggle, `l/100km`, °C, 24h clock | Toggles between `0x0C` (MPH) and `0x0D` (km/h) |
| **USA / North America (`Miles / °F / US MPG / 12h`)** | `11 01 00 00 11 01 01 00` | English, **MPH / Miles**, US MPG (`0x11`), **°F**, 12h clock (`0x00`) | Twisting right knob toggles digital speedo to **km/h** (`0x01`) |

---

### 3.6 Speedometer Pulse Constant (`K-Zahl`, `0x052–0x053`) & Spoiler Speeds (`0x050–0x051`)

| EEPROM Offset | Size | KWP2000 Read / Write | Factory 986 (`K21/K24`) | Factory 996 (`K23`) | Decoding & Notes |
|---|---|---|---|---|---|
| `0x050` | 1 B | `21 73` / `3B 73 <1B>` | `0x50` (**80 km/h**) | `0x3C` (**60 km/h**) | **Rear Spoiler Retract Speed (`Einfahrgeschwindigkeit`):** Direct unsigned byte in `km/h` (`80 km/h` on 986, `60 km/h` on 996) |
| `0x051` | 1 B | `21 72` / `3B 72 <1B>` | `0x78` (**120 km/h**) | `0x78` (**120 km/h**) | **Rear Spoiler Extend Speed (`Ausfahrgeschwindigkeit`):** Direct unsigned byte in `km/h` (`120 km/h`) |
| `0x052–0x053` | 2 B | `21 70` / `3B 70 <2B>` | `FA 5C` (**23,802**) | `FA 5C` (**23,802**) | **`K-Zahl` (Road Speed Pulses per Kilometer):** `uint16 LE` (`0x5CFA = 23802 Imp./km`).<br>• 986 (`K21/K24/K26`) & 996 Turbo (`K22`) & UK 996 (`K23`): `23,802` (`FA 5C`)<br>• 996 Carrera RDW (`K20/K25`): `23,400` (`68 5B`)<br>• USA (`K20–K26`): `24,060` (`FC 5D`)<br>*(Note: If PCM1 nav is fitted, `Kombi K-Zahl = 6 × PCM K-Zahl`, e.g., `23802 = 6 × 3967`)* |
| `0x054–0x055` | 2 B | `21 71` / `3B 71 <2B>` | `78 64` (`[120, 100]`) | `78 64` (`[120, 100]`) | Factory threshold constants |
| `0x056` | 1 B | `21 74` / `3B 74 <1B>` | `0x4E` (K21) / `0x00` (K24) | `0x4E` (`78`) | **Fuel Tank Calibration Offset (`Tankabgleichwert`):** Reset via `3B 74 00` |

---

### 3.7 Speedometer Stepper Calibration Curves (`0x192–0x19B` & `0x184–0x18D`)

The analog speedometer needle is driven by a high-resolution stepper motor controlled by a **10-byte piecewise-linear lookup table** (`5 × uint16 LE` words `[w0, w1, w2, w3, w4]`):
- **Primary Speedometer Curve (`0x192–0x19B`):** Read via `21 78 00` (`61 78 00 <10B>`), written via `3B 78 00 <10B>`.
  - `0x192–0x193` = `w0` (`00 00` origin).
  - `0x194–0x19B` = `w1, w2, w3, w4` (8 active curve bytes).
- **Secondary Speedometer Curve (`0x184–0x18D`):** Read via `21 78 01` (`61 78 01 <10B>`).
  - `0x184–0x185` = `w0` (`00 00`), `0x186–0x18D` = `1B 05 C7 2D F6 6E BC 98` (`[0, 1307, 11719, 28406, 39100]`).

#### Mathematical Model (`[w0, w1, w2, w3, w4]`)

| Word | EEPROM Offset | Role | Units & Physical Meaning |
|---|---|---|---|
| `w0` | `0x192–0x193` | Origin `(X0, Y0)` | Always `0` (`00 00`) — needle rest stop at `0 km/h` |
| `w1` | `0x194–0x195` | **Input Speed Breakpoint `X1`** | Vehicle speed in **`0.01 km/h`** where needle reaches the first calibrated dial mark (e.g., `1225 = 12.25 km/h = 7.61 mph` for the **10 mph** mark on a UK dial) |
| `w2` | `0x196–0x197` | **Stepper Position `Y1`** | Fixed physical stepper motor microstep angle (`11639` on 986, `11650` on 996) corresponding to the printed **10 mph / 10 km/h** tick mark on the gauge face |
| `w3` | `0x198–0x199` | **Input Speed Breakpoint `X2`** | Vehicle speed in **`0.01 km/h`** where needle reaches the full-scale dial mark (e.g., `28300 = 283.00 km/h = 175.85 mph` for the **180 mph** mark on a UK Boxster S dial) |
| `w4` | `0x19A–0x19B` | **Stepper Position `Y2`** | Fixed physical stepper motor microstep angle (`38944–39221`) corresponding to the printed full-scale mark (**250 km/h, 280 km/h, 300 km/h, or 180 mph**) |

For any true road speed $v$ (in `0.01 km/h` units) between $w_1$ and $w_3$, the cluster interpolates the needle stepper position $Y(v)$ linearly:
$$Y(v) = w_2 + \frac{v - w_1}{w_3 - w_1} \cdot (w_4 - w_2)$$

> **CRITICAL CALIBRATION RULE — Never Modify `w2` (`0x196`) or `w4` (`0x19A`):**
> `w2` and `w4` are the **physical angular coordinates of the ink marks printed on the gauge face**. Scaling `w2` or `w4` shifts where the needle points relative to the dial face and creates a severe fixed offset error across the entire sweep. To change speedometer calibration (or remove factory over-read), **only adjust the input speed breakpoints `w1` and `w3`**!

#### Verified Primary Speedometer Curves (`0x192–0x19B`)

| Dial Face & Application | 10-Byte Hex (`0x192–0x19B`) | Decoded `uint16 LE` `[w0, w1, w2, w3, w4]` | Behavior at True 50.0 mph (`80.47 km/h`) |
|---|---|---|---|
| **Factory UK 986 Boxster S (180 mph dial)** | `00 00 C9 04 77 2D 8C 6E 8A 98` | `[0, 1225, 11639, 28300, 39050]` | Reads **~52.2 mph** (`+4.4%` factory EU ECE-R39 safety margin) |
| **Factory UK 996 Carrera (`K23`, 180/200 mph dial)** | `00 00 D5 04 82 2D 70 7B 35 99` | `[0, 1237, 11650, 31600, 39221]` | Factory UK 996 Carrera curve |
| **Factory RDW 986 Boxster 2.7L (250 km/h dial)** | `00 00 7F 02 77 2D 37 63 51 98` | `[0, 639, 11639, 25399, 38993]` | Reads `~83 km/h` on a 250 km/h dial.<br>⚠️ **WARNING:** If loaded onto a UK 180 mph / 280 km/h Boxster S dial, `w3=25399` compresses the full sweep to 157.8 mph, causing a massive **`+15.3%` (`+7.6 mph` at 50 mph) over-read!** |
| **Factory RDW 986 Boxster S 3.2L (280 km/h dial)** | `00 00 7F 02 77 2D 5B 72 20 98` | `[0, 639, 11639, 29275, 38944]` | Factory 280 km/h Boxster S curve |
| **Factory RDW 996 Carrera / Turbo (300 km/h dial)** | `00 00 00 03 82 2D 70 7B 35 99` | `[0, 768, 11650, 31600, 39221]` | Factory 300 km/h 996 curve |
| **Calibrated UK 180 mph — True 1:1 GPS (`0.0 mph` error)** | `00 00 49 06 77 2D 28 71 8A 98` | `[0, 1609, 11639, 28968, 39050]` | Reads **exact 50.0 mph** at 50.0 mph GPS (`16.09 km/h = 10.0 mph`, `289.68 km/h = 180.0 mph`) |
| **Calibrated UK 180 mph — `+3.0%` Legal Cushion** | `00 00 1A 06 77 2D DC 6D 8A 98` | `[0, 1562, 11639, 28124, 39050]` | Reads **51.5 mph** at 50.0 mph GPS (`+1.5 mph` safety margin) |

*(Note: The digital speedometer in the center LCD and the odometer are driven directly by the `K-Zahl` pulse constant at `0x052–0x053` and are completely independent of the analog stepper curve at `0x192–0x19B`.)*

---

### 3.8 Fuel Tank Calibration Curves (`0x202–0x235`)

The fuel gauge and OBC remaining-range (`Reichweite`) calculation use three tables in EEPROM:

| EEPROM Offset | Length | KWP2000 Read / Write | Factory 986 (`K21 / K24`, 64L Tank) | Factory 996 (`K23`, 64L Tank) | Description |
|---|---|---|---|---|---|
| `0x202–0x20D` | 12 B | `21 7C` / `3B 7C <12B>` | **K21:** `AB 03 70 03 2D 03 8F 02 B9 01 67 00`<br>**K24:** `A4 03 77 03 26 03 88 02 B2 01 6A 00` | `A3 03 68 03 25 03 87 02 B1 01 6A 00` | **Tank Curve Z (`6 × uint16 LE`, `0.1 Ω`):** Secondary sender resistance table (`[93.9, 88.0, 81.3, 65.5, 44.1, 10.3] Ω` on K21) |
| `0x21A–0x225` | 12 B | `21 75` / `3B 75 <12B>` | `AE 03 5D 03 33 03 97 02 C6 01 88 00` | `FE 03 FD 03 A6 03 2D 03 30 02 6A 00` | **Tank Sender Resistance Curve X (`6 × uint16 LE`, `0.1 Ω`):**<br>• **986 (`K21/K24`):** `[94.2, 86.1, 81.9, 66.3, 45.4, 13.6] Ω` (Empty → Full)<br>• **996 (`K23`):** `[102.2, 102.1, 93.4, 81.3, 56.0, 10.6] Ω` |
| `0x226–0x235` | 16 B | `21 7B` / `3B 7B <16B>` | `00 00 00 06 80 0A 00 0F 80 16 B3 1C 2E 00 03 01` *(K24 byte 12 = `39`)* | `00 00 00 05 80 0A 00 0F 80 16 B3 1C 30 00 03 01` | **Tank Volume Curve Y (`16 bytes`):** Volume breakpoints and damping thresholds |

---

### 3.9 Oil Level Sensor Characteristic Curve (`0x380–0x3AD`)

The electronic engine oil level measurement (`Ölstandsmessung`) uses a **46-byte (`0x2E`) temperature-compensated calibration table** at `0x380–0x3AD`, accessed via KWP2000 `21 76 00..07` (Read) and `3B 76 00..07` (Write) across 8 sub-blocks:

| Sub-Block | EEPROM Offset | Length | KWP2000 Read / Write | Factory MY2001 (`K21` 986) | Factory MY2002 (`K24` 986 & `K23` 996) |
|---|---|---|---|---|---|
| Block `00` | `0x380–0x389` | 10 B | `21 76 00` / `3B 76 00` | `3D 01 6A 01 96 01 C3 01 F0 01` | `3D 01 6A 01 96 01 C3 01 F0 01` |
| Block `01` | `0x38A–0x393` | 10 B | `21 76 01` / `3B 76 01` | `18 00 28 00 38 00 48 00 58 00` | `12 00 22 00 32 00 42 00 52 00` |
| Block `02` | `0x394–0x398` | 5 B | `21 76 02` / `3B 76 02` | `53 48 38 23 00` | `2A 32 38 38 1C` |
| Block `03` | `0x399–0x39D` | 5 B | `21 76 03` / `3B 76 03` | `87 78 69 52 27` | `5A 5F 68 65 51` |
| Block `04` | `0x39E–0x3A2` | 5 B | `21 76 04` / `3B 76 04` | `B8 A7 97 7F 59` | `86 8C 94 94 86` |
| Block `05` | `0x3A3–0x3A7` | 5 B | `21 76 05` / `3B 76 05` | `E8 D5 C3 AE 8C` | `B3 B9 BE C4 BC` |
| Block `06` | `0x3A8–0x3AC` | 5 B | `21 76 06` / `3B 76 06` | `FF FF F1 E0 C6` | `E3 E8 EE F9 FC` |
| Block `07` | `0x3AD` | 1 B | `21 76 07` / `3B 76 07` | `FF` | `FF` |

> **996 ↔ 986 Cluster Swap Note:** Because the dry-sump/integrated-wet-sump oil pan geometry differs slightly between the mid-engine 986 (`M96.2x`) and rear-engine 996 (`M96.0x`), copying `0x380–0x3AD` (or writing sub-blocks `3B 76 00..07`) from a 986 dump into a 996 cluster retrofitted to a Boxster ensures accurate electronic oil level bar-graph readings and countdown timers.

---

### 3.10 LCD Contrast / Operating Voltage Bias (`0x2C6`)

- **EEPROM Offset:** `0x2C6` (1 byte)
- **Verified Values:**
  - **986 Boxster (`K21` & `K24`):** `0x21` (`33`)
  - **996 Carrera (`K23`):** `0x20` (`32`)
- **Hardware Function:** Configures the VDO microcontroller's LCD operating voltage (`VLCD`) bias generator for the three segmented nematic LCD panels (matching the Minitools `SEPDISP87` replacement LCD engineering specification):
  - Nominal target LCD operating voltage: **`12.7 V – 12.9 V`** at room temperature.
  - Incrementing `0x2C6` by `+1` hex step (`0x21 → 0x22`) increases `VLCD` by approximately **`+0.1 V`** (darkening segments if a replacement LCD appears faint).
  - Decrementing `0x2C6` by `-1` hex step (`0x21 → 0x20`) lowers `VLCD` by approximately **`-0.1 V`** (reducing ghosting/bleeding if unlit segments appear faintly visible in hot weather).

---

### 3.11 Event Memory (`Ereignisspeicher`, `0x644–0x65B` & `0x6F4–0x6F5`)

In addition to standard KWP2000 fault codes (`0x600–0x643`), the 93C86 cluster maintains a 12-channel **Event Memory** that records the last odometer reading at which any critical warning lamp was triggered:
- **`0x6F4–0x6F5` (2 bytes, read via `21 30`, cleared via `31 30`):** 12-bit active warning mask:
  - **Byte `0x6F4` (`bits 0..7`):** Bit 0 = Brake fluid level, Bit 1 = Brake pad wear, Bit 2 = Coolant level, Bit 3 = Coolant over-temperature, Bit 4 = Oil pressure, Bit 5 = Oil level, Bit 6 = Roll-over bar (`Überrollbügel`), Bit 7 = Airbag warning.
  - **Byte `0x6F5` (`bits 0..3`):** Bit 0 = Check Engine (`MIL`), Bit 1 = ABD / TC / PSM intervention, Bit 2 = Brake booster (`Bremskraftverstärker`), Bit 3 = Engine compartment blower (`Motorraumgebläse`).
- **`0x644–0x65B` (24 bytes, read via `21 31 00` through `21 31 0B`):** 12 × 2-byte odometer snapshots corresponding to each of the 12 warning events above.

---

### 3.12 Mileage Storage & Dynamic RAM Shadow Caveats (`0x300` & `0x500`)

⚠️ **WARNING: Odometer tampering is illegal in most jurisdictions.** The information below is provided strictly for legitimate cluster repair, EEPROM corruption recovery, and matching replacement clusters to a vehicle's true mileage.

| Cluster Generation | Primary Odometer Block | Backup Odometer Block | Live K-Line Read (`km`) |
|---|---|---|---|
| **Old Style (`93C56B`)** | `0x000–0x00F` (16 bytes) | *(Single copy only)* | `21 22` (4 bytes) |
| **New Style (`93C86`)** | `0x300–0x31F` (32 bytes) | `0x500–0x51F` (32 bytes) | `21 10` (3 bytes, 24-bit unsigned integer in `km`) |

#### Mathematical Structure of `0x300` and `0x500` (Dual-Buffer Interleaving & Parity)
The VDO 93C86 cluster stores the total odometer across two 32-byte blocks: Primary (`0x300–0x31F`) and Backup (`0x500–0x51F`). Each 32-byte block consists of:
- **First 16 Bytes (`h1`):** 8 circular words stored Little-Endian (`Low, High`), generated from base ceiling word $w_0 = \text{0xFFFF} - (\text{km} \mathbin{//} 32) - 1$ via circular left 1-bit rotations (`rol16(w, 1)`).
- **Second 16 Bytes (`h2`):** 8 differential words stored Big-Endian (`High, Low`), implementing an 8-stage Johnson/Möbius Vernier ring counter stepping in discrete **2 km quanta** (16 states per 32 km cycle).

1. **Why Byte 25 Differs on Odd-Kilometer Vehicles (The Ping-Pong Interleaving):**
   - Because a single 32-byte buffer only resolves distance in discrete 2 km increments, the VDO firmware achieves **exact 1 km resolution** by **interleaving the Primary (`0x300`) and Backup (`0x500`) buffers**:
     $$\text{Total Odometer} = \frac{\text{Buffer}_{0x300} + \text{Buffer}_{0x500}}{2}$$
   - **Even Kilometers ($\text{km} \pmod 2 = 0$):** Both `0x300` and `0x500` hold the exact same state (100% byte identical).
   - **Odd Kilometers ($\text{km} \pmod 2 = 1$):** `0x300` holds the even step below, while `0x500` holds the even step above. In the binary representation, this manifests as a 1-word difference at byte offset `+0x19` (byte 25 in the block: `0x319` vs `0x519`, typically `0x2E` vs `0x3E`).
   - **Conclusion:** A 1-word difference at byte 25 is **normal factory behavior on odd-mileage vehicles**, NOT EEPROM corruption.

2. **Offline Desoldered / Clip Programming Rule:**
   - If flashing a physical 93C86 chip offline with a hardware programmer (GQ-4X / CH341A), ensure both `0x300` and `0x500` are paired validly (or identical for even km). If the two blocks disagree beyond the allowed 1-step rolling window at cold power-on, the cluster will display `999999` or illuminate the `!` parity fault indicator.

3. **Never Overwrite Your Cluster's Odometer or VIN with Another Car's Dump:**
   - If your cluster suffers coding corruption, **never** flash another car's complete `.bin` image onto your cluster. Doing so overwrites your VIN (`0x000`), part number (`0x01D`), DSN (`0x023`), and odometer (`0x300`/`0x500`). Instead, restore only the specific configuration fields (`0x032–0x041`, `0x192–0x19B`, etc.) over K-line using services `30 01 08`, `30 01 09`, and `3B xx`.

---

## 4. Included Sample Dumps (`dumps/`)

### 4.1 New Style (`93C86`, 2048 Bytes) — Side-by-Side Comparison

| Field / Offset | `eeprom_dump_986_boxster_s_2001_k21_uk_93c86.bin` | `eeprom_dump_986_boxster_s_2002_k24_uk_93c86.bin` | `eeprom_dump_996_c2_2002_k23_uk_74336mi_native8_93c86.bin` | `eeprom_dump_996_c2_2002_k23_uk_206913mi_native8_93c86.bin` |
|---|---|---|---|---|
| **Vehicle** | MY2001 986 Boxster S 3.2L Manual (UK) | MY2002 986 Boxster S 3.2L Manual (UK) | MY2002 996 Carrera 2 Manual (UK, 74,336 mi) | MY2002 996 Carrera 2 Manual (UK, 206,913 mi) |
| **Read Method** | OBD K-Line (`Service 0x23` at `0x080000`) | Bench K-Line (`Service 0x23` at `0x080000`) | Hardware programmer (converted to native 8-bit) | Hardware programmer (converted to native 8-bit) |
| **VIN (`0x000–0x010`)** | `WP0ZZZ98Z1S6XXXXX` *(masked)* | `WP0ZZZ98Z2U6XXXXX` *(masked)* | `WP0ZZZ99Z2S603304` | `WP0ZZZ99Z2S603304` |
| **Part No (`0x01D–0x022`)** | `986.641.217.00` (`098664121700`) | `986.641.237.00` (`098664123700`) | `996.641.227.00` (`099664122700`) | `996.641.227.00` (`099664122700`) |
| **DSN (`0x023`)** | `0x15` (**K21**) | `0x18` (**K24**) | `0x17` (**K23**) | `0x17` (**K23**) |
| **`Parameterkodierung` (`0x032–0x039`)** | `84 02 1F 00 B5 07 00 00` | `84 02 1F 00 B5 07 00 00` | `84 03 1F 10 B5 02 00 00` | `84 03 1F 10 B5 02 00 00` |
| **`Menükonfiguration` (`0x03A–0x041`)** | `19 01 0C 00 19 01 0D 00` *(MPH default, knob toggles km/h, 24h)* | `19 01 04 00 19 01 04 00` *(MPH, 12h clock)* | `19 01 04 00 19 01 04 00` *(MPH, 12h clock)* | `19 01 04 00 19 01 04 00` *(MPH, 12h clock)* |
| **Spoiler Retract / Extend (`0x050–0x051`)** | `50 78` (`80 / 120 km/h`) | `50 78` (`80 / 120 km/h`) | `3C 78` (`60 / 120 km/h`) | `3C 78` (`60 / 120 km/h`) |
| **`K-Zahl` (`0x052–0x053`)** | `FA 5C` (`23,802 Imp./km`) | `FA 5C` (`23,802 Imp./km`) | `FA 5C` (`23,802 Imp./km`) | `FA 5C` (`23,802 Imp./km`) |
| **Primary Speedo Curve (`0x192–0x19B`)** | `00 00 C9 04 77 2D 8C 6E 8A 98` | `00 00 C9 04 77 2D 8C 6E 8A 98` | `00 00 D5 04 82 2D 70 7B 35 99` | `00 00 D5 04 82 2D 70 7B 35 99` |
| **LCD Bias (`0x2C6`)** | `0x21` | `0x21` | `0x20` | `0x20` |

*(Note: The original 16-bit byte-swapped programmer dumps `Porsche 911 996 2002 C2 Geoff Mge 93C86 74336 original dump.bin` and `...206913 original dump.bin` are also preserved in `dumps/` for backward compatibility.)*

### 4.2 Old Style (`93C56B`, 256 Bytes) — Side-by-Side Comparison

| Feature | `eeprom_dump_986_cluster_1999_avn_orig.bin` | `eeprom_dump_996_ref_986_rennlist_guide.bin` | `eeprom_dump_working_with_eeprom_illustrated.bin` |
|---|---|---|---|
| **VIN** | `WP0CA2986XU624175` | `WP0ZZZ98ZYU600985` | `WP0AA2995YS623225` |
| **Vehicle Type (`0x35–0x36`)** | `09 96` (996) | **`09 86` (986)** | `09 96` (996) |
| **PST2 Mode (`0x3B`)** | `0x08` (996) | **`0x06` (986)** | `0x08` (996) |
| **OBC (`0x47`)** | `0x1F` (ENABLED) | `0x1F` (ENABLED) | `0x1F` (ENABLED) |
| **Oil Pressure (`0x49`)** | `0x3C` (ENABLED) | `0x3C` (ENABLED) | `0x3C` (ENABLED) |
| **Voltmeter (`0x56`)** | **`0x00` (DISABLED)** | `0x01` (ENABLED) | `0x01` (ENABLED) |
| **`0xE2–0xE3`** | `18 10` | `1B 12` | `1B 12` |
| **Speedo Scaling (`0xEB–0xED`)** | `E9 66 83` (MPH) | `E4 52 94` (KM) | `E9 66 83` (MPH) |

---

## 5. Physical EEPROM Access & SOIC-8 Clip Guide

When working on an early cluster (`93C56B`) or performing offline recovery on a dead late cluster (`93C86`):

### 5.1 Disassembly
- **Old Style (`93C56B`, MY1997–2000):**
  1. Slide the retaining latches on the rear 26-pin connectors outward.
  2. Release the black lower retaining clip beneath the tachometer and separate the gauge assembly from the PCB.
  3. The `93C56B` SOIC-8 chip is located on the front of the PCB above the center LCD, slightly right of the upper-left corner.
- **New Style (`93C86`, MY2001–2005):**
  1. Unclip the rear white plastic housing cover and remove the Torx screws securing the PCB.
  2. **Short the crystal resonator legs** (near the main VDO processor) using a jumper wire or alligator clip before attaching the SOIC-8 programmer clip. Without shorting the crystal, the 3.3V/5V supply from the EEPROM programmer wakes up the main MCU, which drives the Microwire bus lines and corrupts the read/write.
  3. Clean the VDO conformal lacquer from the 8 pins of the `93C86` with isopropyl alcohol or contact cleaner so the SOIC-8 clip makes reliable contact.

```text
Chip Pin 1 (marked with a dot or bevelled edge)
    ↓
    ┌─────────┐
  1 │ •     8 │ VCC (+5V)
  2 │       7 │
  3 │       6 │ ORG (16-bit vs 8-bit organization on 93C86)
  4 │       5 │ GND
    └─────────┘
```

---

## 6. Conversion & Recovery Checklists

### 6.1 Converting an Early 996 Cluster (`93C56B`) to a 986 Boxster
```text
1. Copy mileage:        0x00–0x0F from original 986 → 996 cluster
2. Copy VIN:            0x18–0x28 from original 986 → 996 cluster
3. Set vehicle type:    0x35–0x36 = 09 86
4. Set PST2 mode:       0x3B = 06
5. Enable OBC:          0x47 = 1F (if desired)
6. Enable oil pressure: 0x49 = 3C
7. Enable voltmeter:    0x56 = 01
```

### 6.2 Adapting or Recovering a Late Cluster (`93C86`) Over K-Line (`0x64`)
On MY2001+ clusters, you do **not** need to open the cluster or touch the physical EEPROM chip to configure options, fix corrupted coding, or adapt a replacement cluster:
1. **Dump a full 2048-byte backup first** over OBD Pin 3 (`A28`) using KWP2000 Service `0x23` (`23 08 00 00 10` .. `23 08 07 F0 10`).
2. **Verify or restore `Parameterkodierung` (`0x032–0x039`)** via `30 01 08 <8 bytes>`:
   - Always start from the verified factory baseline (`84 02 1F 00 B5 07 00 00` for 986 Boxster, or `84 03 1F 10 B5 02 00 00` for 996 Carrera) and only toggle the specific feature bits you need.
3. **Verify or update `Menükonfiguration` (`0x03A–0x041`)** via `30 01 09 <8 bytes>` (e.g., `19 01 0C 00 19 01 0D 00` for UK MPH with km/h knob twist and 24h clock).
4. **Verify or update `Primary Speedometer Curve` (`0x192–0x19B`)** via `3B 78 00 <10 bytes>` (e.g., `00 00 C9 04 77 2D 8C 6E 8A 98` for factory UK 180 mph).
5. **Commit to non-volatile EEPROM** using `10 F5` followed by `11 01` (ECU Reset), then wait 5 seconds and re-read to confirm persistence.

---

## Acknowledgments & References

- **Gavin Yuill** — Original 93C56B EEPROM research
- **Shaun Merriman** — New-style cluster testing
- **freserf** — OBC enable byte discovery (`0x47 = 0x1F`, BoXa.net, May 2023)
- **KevinH2000** — Rennlist PDF documentation (*Working with the EPROM on Porsche Boxster*)
- **Alex Nesta** — Old-style offset mapping, reference images, and repository maintainer
- **James Galbally** — Complete 93C86 memory map (`0x000–0x7FF`), bit-level `Parameterkodierung` & `Menükonfiguration` tables, speedometer stepper curve math, warning lamp driver recovery (`0x036 = 0xB5`), KWP2000 `0x23` OBD dumping, and verified UK `K21`/`K24` 986 Boxster S dumps
