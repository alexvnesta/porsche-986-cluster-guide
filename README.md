# Porsche 986/996 Instrument Cluster Guide

Comprehensive hardware, wiring, KWP2000 diagnostic, and EEPROM reverse-engineering reference for the Porsche 986 Boxster (1997–2004) and 996 911 (1998–2005) instrument cluster (`Kombiinstrument`).

## ⚠️ Disclaimer

For educational purposes, classic vehicle preservation, and vehicle owners only. Odometer tampering is illegal. This documentation is provided strictly for legitimate diagnostics, repair, coding recovery, and restoration.

## Cluster Overview

```text
     ┌──────────────────────────────────────────────────────────┐
     │                    INSTRUMENT CLUSTER                    │
     │  ┌─────────┐                              ┌─────────┐    │
     │  │  TACH   │    ┌──────────────────┐      │  SPEEDO │    │
     │  │         │    │   LCD DISPLAY    │      │         │    │
     │  │  0-8k   │    │  Trip/Odo/Temp   │      │ 0-180mph│    │
     │  └─────────┘    └──────────────────┘      └─────────┘    │
     │     ┌────┐  ┌────┐            ┌─────┐  ┌────┐            │
     │     │FUEL│  │TEMP│            │ OIL │  │VOLT│ (996 5-pod)│
     │     │    │  │    │            │PRESS│  │MTR │            │
     │     └────┘  └────┘            └─────┘  └────┘            │
     └──────────────────────────────────────────────────────────┘
```

*(Note: All 986 Boxster clusters have 3 main dials with 3 segmented LCD windows; 996 clusters add two outer pods for Oil Pressure and Voltmeter.)*

## What Do You Need To Do?

| Task | What You Need | Guide |
|------|---------------|-------|
| **Identify cluster part numbers & `DSN` (`K02`–`K50`)** | Part label or K-line `1A 9E` / `1A 9F` | [docs/PART_NUMBERS.md](docs/PART_NUMBERS.md) |
| **Power up a cluster on the bench / check pinouts** | 12V bench PSU & connector pinout | [docs/WIRING.md](docs/WIRING.md) |
| **Dump or analyze `93C56B` / `93C86` EEPROM** | OBD K-line cable (Pin 3) or EEPROM clip | [docs/EEPROM_MAP.md](docs/EEPROM_MAP.md) |
| **Enable OBC, change units (`MPH`/`km/h`/`°C`/`24h`), or calibrate speedo** | KWP2000 tool (`0x64`) or EEPROM programmer | [docs/EEPROM_MAP.md](docs/EEPROM_MAP.md) & [docs/DIAGNOSTICS.md](docs/DIAGNOSTICS.md) |
| **Recover dead Airbag bulb-check or handbrake lamp after bad coding** | KWP2000 `30 01 08` (`0x032=0x84`, `0x036=0xB5`) | [docs/EEPROM_MAP.md#34-warning-lamp-drivers-psm-handbrake-logic--how-bad-coding-breaks-tell-tales](docs/EEPROM_MAP.md#34-warning-lamp-drivers-psm-handbrake-logic--how-bad-coding-breaks-tell-tales) |
| **Read fault codes (`9101`–`9152`), live sensors, or run gauge tests** | K-line interface on **OBD-II Pin 3** | [docs/DIAGNOSTICS.md](docs/DIAGNOSTICS.md) |
| **Repair dead LCD segments or adjust LCD contrast bias (`0x2C6`)** | Ribbon cable / `SEPDISP87` LCD | [docs/LCD_REPAIR.md](docs/LCD_REPAIR.md) |
| **Fix dim backlight or `Terminal 58d` dimmer faults** | Bulbs / LEDs / multimeter | [docs/BACKLIGHT.md](docs/BACKLIGHT.md) |

## Quick Facts: Old Style vs. New Style (`Kombi 2000`)

| Detail | Old Style (MY1997–2000) | New Style (`Kombi 2000`, MY2001–2005) |
|--------|-------------------------|---------------------------------------|
| **Dataset (`DSN`)** | `K02` – `K17` | `K20` – `K50` (`K21`=MY01 986, `K23`=MY02 996, `K24`=MY02 986, `K26`=MY03–04 986) |
| **Rear Connectors** | **3 × 26-pin** (Blue `I`, White `II`, Black `III`) | **3 × 32-pin** (Green `A`, Blue `B`, Grey `C`) |
| **Powertrain Bus** | Discrete analog wires (`TN` RPM, `KVA` fuel) | **500 kbps CAN Antrieb** (`Green Plug A Pins 15 & 31` to DME `ME7.8` & ABS/PSM) |
| **Diagnostic Bus** | KWP2000 (`0x64`) on **OBD Pin 3** (`Blue Plug I Pin 21`) | KWP2000 (`0x64`) on **OBD Pin 3** (`Green Plug A Pin 28`, 10,400 baud Fast Init) |
| **EEPROM Chip** | **93C56B** (256 bytes, 16-bit word-swapped) | **93C86** (2048 bytes, native 8-bit linear order) |
| **VIN Location** | `0x18–0x28` | `0x000–0x010` (17 bytes ASCII; KWP2000 `1A 90` / `3B 90`) |
| **Part No & DSN** | `0x35–0x36` (`0986`/`0996`), `0x3B` (`06`/`08`) | `0x01D–0x022` (6B BCD, `1A 9E`), `0x023` (1B DSN, `1A 9F`) |
| **Equipment Coding** | `0x47` (OBC `1F`), `0x49` (Oil `3C`), `0x56` (Volt `01`) | `0x032–0x039` (`Parameterkodierung`, `30 01 01` / `30 01 08`: `84 02 1F 00 B5 07 00 00`) |
| **Display Units Coding** | `0x40–0x4B` & `0xEB–0xED` | `0x03A–0x041` (`Menükonfiguration`, `30 01 02` / `30 01 09`: `19 01 0C 00 19 01 0D 00`) |
| **Speedo Calibration** | `0xE2–0xED` (12 bytes) | `0x052–0x053` (`K-Zahl` `23,802`) + `0x192–0x19B` (`5 × uint16 LE` stepper curve, `3B 78 00`) |
| **Mileage Blocks** | `0x000–0x00F` (16 bytes encrypted) | `0x300–0x31F` (Primary, 32B) & `0x500–0x51F` (Backup, 32B); live km via `21 10` |
| **OBD Memory Dump** | Not supported (SOIC-8 clip required) | **Supported** via KWP2000 `23 08 xx xx 10` (`0x080000–0x0807FF` live RAM shadow) |

## Documentation Index

| Document | Contents |
|----------|----------|
| **[docs/EEPROM_MAP.md](docs/EEPROM_MAP.md)** | Complete `93C56B` (256B) & `93C86` (2048B) memory maps, bit-level `Parameterkodierung` (`0x032`) & `Menükonfiguration` (`0x03A`) tables, tell-tale driver recovery (`0x036=0xB5`), `5 × uint16 LE` speedometer stepper curve math (`0x192`), fuel/oil curves, LCD bias (`0x2C6`), dual-buffer odometer interleaving (`0x300`/`0x500`), and dump comparisons |
| **[docs/WIRING.md](docs/WIRING.md)** | Complete pinouts for Late (`3×32-pin` Green A / Blue B / Grey C) and Early (`3×26-pin` Blue I / White II / Black III) clusters, bench power-up & K-line harness guide, CAN vs. K-line architecture, Terminal 86S / Fuse E1 airbag circuit, and OBC stalk retrofit wiring & inverted UP/DOWN fix |
| **[docs/DIAGNOSTICS.md](docs/DIAGNOSTICS.md)** | Complete KWP2000 (`0x64`, OBD Pin 3, 10,400 baud) reference: `0x1A` IDs, 26-code DTC table (`9101`–`9152` & `5555`), Event Memory (`21 30` / `31 30`), Live Data (`21 01`, `21 02`, `21 10`, `21 40`, `21 70–7C`), the `30 01 08` dataless write trap, factory Actuator routines (`31 03`–`31 07`), dynamic center display text injection (`31 06 03`), fuel gauge software damping behavior, and OBD `0x23` RAM-shadow memory dumping |
| **[docs/PART_NUMBERS.md](docs/PART_NUMBERS.md)** | Complete `986.641.xxx.xx` / `996.641.xxx.xx` part number decoder, full `DSN` (`K02`–`K50`) evolution, 3-window LCD vs. dot-matrix clarification, `K21 ↔ K24` hardware & firmware comparison (menu unit toggles), and full PET part catalog |
| **[docs/LCD_REPAIR.md](docs/LCD_REPAIR.md)** | Segmented LCD ribbon repair, `Minitools SEPDISP87` replacement panels, and `0x2C6` contrast bias register |
| **[docs/BACKLIGHT.md](docs/BACKLIGHT.md)** | Incandescent bulb & SMD LED guide, `Terminal 58d` dimmer pins (`A12/A13` & `II/23/19`), and ambient photocell (`21 02` / DTC `9151`) |

## Included Reference Dumps (`dumps/`) & Analyzer Tool

Run [`tools/cluster_analyzer.py`](tools/cluster_analyzer.py) to decode any 256-byte (`93C56B`) or 2048-byte (`93C86`) dump, or compare two dumps byte-by-byte:

```bash
python3 tools/cluster_analyzer.py dumps/eeprom_dump_986_boxster_s_2001_k21_uk_93c86.bin
python3 tools/cluster_analyzer.py dumps/eeprom_dump_986_boxster_s_2001_k21_uk_93c86.bin --compare dumps/eeprom_dump_986_boxster_s_2002_k24_uk_93c86.bin
```

| Dump File (`dumps/`) | Generation | Vehicle & Specification |
|---|---|---|
| `eeprom_dump_986_boxster_s_2001_k21_uk_93c86.bin` | New (`93C86`, 2048B, native 8-bit) | MY2001 986 Boxster S 3.2L Manual UK (`986.641.217.00`, `DSN K21`, 180 mph, OBC, 24h, MPH/km/h knob toggle) |
| `eeprom_dump_986_boxster_s_2002_k24_uk_93c86.bin` | New (`93C86`, 2048B, native 8-bit) | MY2002 986 Boxster S 3.2L Manual UK (`986.641.237.00`, `DSN K24`, 180 mph, OBC, 12h, factory UK baseline) |
| `eeprom_dump_996_c2_2002_k23_uk_74336mi_native8_93c86.bin` | New (`93C86`, 2048B, native 8-bit) | MY2002 996 Carrera 2 Manual UK (`996.641.227.00`, `DSN K23`, 74,336 mi, unswapped native 8-bit) |
| `eeprom_dump_996_c2_2002_k23_uk_206913mi_native8_93c86.bin` | New (`93C86`, 2048B, native 8-bit) | MY2002 996 Carrera 2 Manual UK (`996.641.227.00`, `DSN K23`, 206,913 mi, unswapped native 8-bit) |
| `eeprom_dump_986_cluster_1999_avn_orig.bin` | Old (`93C56B`, 256B) | MY1999 986 Boxster (US, MPH/°C, 12h) |
| `eeprom_dump_996_ref_986_rennlist_guide.bin` | Old (`93C56B`, 256B) | 996 → 986 conversion reference (UK, km/°C) |
| `eeprom_dump_working_with_eeprom_illustrated.bin` | Old (`93C56B`, 256B) | Rennlist PDF guide reference (996) |

## Acknowledgments

- **Gavin Yuill** — Original 93C56B EEPROM reverse engineering
- **Shaun Merriman** — New-style cluster testing
- **freserf** — OBC enable byte discovery (BoXa.net)
- **KevinH2000** — Rennlist PDF documentation
- **Alex Nesta** — Old-style offset mapping, analyzer tool, and repository maintainer
- **James Galbally** — Complete 93C86 memory map, bit-level coding & stepper calibration documentation, KWP2000 (`0x64`) protocol & OBD `0x23` RAM-shadow dump guide, factory WSM pinouts, PET part catalog, and UK `K21`/`K24` 986 Boxster S dumps

## License

MIT License. Use at your own risk. See [LICENSE](LICENSE) for details.
