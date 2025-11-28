# Porsche 986/996 Instrument Cluster Guide

Reverse-engineering documentation for the Porsche 986 Boxster and 996 911 instrument cluster (Kombiinstrument).

## ⚠️ Disclaimer

For educational purposes and vehicle owners only. Odometer tampering is illegal. This documentation is for legitimate repair and restoration.

## Cluster Overview

```
     ┌──────────────────────────────────────────────────────────┐
     │                    INSTRUMENT CLUSTER                    │
     │  ┌─────────┐                              ┌─────────┐    │
     │  │  TACH   │    ┌──────────────────┐      │  SPEEDO │    │
     │  │         │    │   LCD DISPLAY    │      │         │    │
     │  │  0-8k   │    │  Trip/Odo/Temp   │      │ 0-180mph│    │
     │  └─────────┘    └──────────────────┘      └─────────┘    │
     │     ┌────┐  ┌────┐            ┌─────┐  ┌────┐            │
     │     │FUEL│  │TEMP│            │ OIL │  │ OIL│            │
     │     │    │  │    │            │PRESS│  │TEMP│            │
     │     └────┘  └────┘            └─────┘  └────┘            │
     └──────────────────────────────────────────────────────────┘
```

## What Do You Need To Do?

| Task | What You Need | Guide |
|------|---------------|-------|
| **Swap 986↔996 cluster** | EEPROM programmer | [EEPROM_MAP.md](docs/EEPROM_MAP.md) |
| **Enable OBC/voltmeter** | EEPROM access | [EEPROM_MAP.md](docs/EEPROM_MAP.md#feature-enable-flags) |
| **Transfer mileage** | EEPROM programmer | [EEPROM_MAP.md](docs/EEPROM_MAP.md#mileage-storage) |
| **Repair dead pixels** | Soldering iron, ribbon cable | [LCD_REPAIR.md](docs/LCD_REPAIR.md) |
| **Diagnose gauges** | Multimeter | [DIAGNOSTICS.md](docs/DIAGNOSTICS.md) |
| **Fix backlight** | LED/bulb replacement | [BACKLIGHT.md](docs/BACKLIGHT.md) |

## Quick Facts

| Detail | Old Style (MY2000-) | New Style (MY2001+) |
|--------|---------------------|---------------------|
| **EEPROM** | 93C56B (256 bytes) | 93C86 (2048 bytes) |
| **Read Mode** | 16-bit, byte-swapped | 8-bit, no swap |
| **VIN Location** | Lines 0x10-0x20 | Line 0x000 |
| **Mileage** | Line 0x00 | Lines 0x300 & 0x500 |
| **OBC Enable** | Position 0x2F: 00→1F | TBD |

**Common for both:**
- Part Numbers: 996.641.xxx.xx
- Programmer: Willem GQ-4X recommended
- SOIC-8 test clip required

## Common Issues

- LCD pixel failure (ribbon cable bond)
- Dim/dead backlight (bulbs)
- Sticky gauges
- VIN mismatch after swap (radio won't work on 2001+)
- OBC not working after 996→986 swap

## Documentation

| Document | Contents |
|----------|----------|
| [docs/EEPROM_MAP.md](docs/EEPROM_MAP.md) | Complete memory map, VIN/mileage transfer, feature flags |
| [docs/LCD_REPAIR.md](docs/LCD_REPAIR.md) | Pixel repair, ribbon cable replacement |
| [docs/WIRING.md](docs/WIRING.md) | Connector pinouts, CAN bus info |
| [docs/DIAGNOSTICS.md](docs/DIAGNOSTICS.md) | Testing procedures, self-test mode |
| [docs/PART_NUMBERS.md](docs/PART_NUMBERS.md) | Cluster variants, compatibility matrix |
| [docs/BACKLIGHT.md](docs/BACKLIGHT.md) | Bulb replacement, LED conversion |

## Tools Required

**For EEPROM work:**
- Willem GQ-4X programmer (recommended) or CH341A (~$5)
- SOIC-8 test clip (~$5)
- HxD Hex Editor (free)

**For LCD repair:**
- Soldering iron with fine tip
- Replacement ribbon cable
- Torx T10/T20 drivers

**For general diagnostics:**
- Multimeter
- PIWIS/PST2/Durametric

## Resources

- [Rennlist PDF: Working with the EPROM on Porsche Boxster](https://rennlist.com/forums/attachments/boxster-and-boxster-s-986-forum/1278842d1523504323-programming-a-996-cluster-to-work-in-a-986-working-with-the-eprom-on-porsche-boxster-illustrated-old-and-new-style-clusters-minimum.pdf)
- [BoXa.net - 986 to 996 Gauge Cluster Thread](https://www.boxa.net/)
- [Rennlist 996 Forum](https://rennlist.com/forums/996-forum/)
- [986 Forum](https://986forum.com)
- [Pelican Parts Technical Articles](https://www.pelicanparts.com/techarticles/)

## Acknowledgments

- Gavin Yuill - Original EEPROM reverse engineering
- Shaun Merriman - New style cluster testing
- freserf - OBC enable discovery
- KevinH2000 - Rennlist documentation

## License

MIT License. Use at your own risk. See LICENSE for details.

## Contributing

Found something useful? PRs welcome! Please include:
- Clear documentation with hex offsets
- Photos/diagrams where helpful
- Part numbers and model year applicability
- EEPROM dumps (see dumps/ folder)
