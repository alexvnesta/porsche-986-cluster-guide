#!/usr/bin/env python3
"""
Porsche 986/996 Instrument Cluster EEPROM Analyzer (93C56B & 93C86)

Analyzes cluster EEPROM dumps (256-byte Old Style 93C56B or 2048-byte New Style 93C86)
and decodes all known identification, coding, calibration, and diagnostic fields:

- Old Style (93C56B, 256 bytes, MY1997-2000):
  * Encrypted Mileage (0x00-0x0F)
  * VIN (0x18-0x28)
  * Vehicle Type (0x35-0x36: 09 86=986, 09 96=996)
  * PST2 Mode (0x3B: 06=986, 08=996)
  * OBC Trip Computer (0x47: 00=OFF, 1F=ON)
  * Oil Pressure Gauge (0x49: 3C=ON, 50=OFF)
  * Voltmeter (0x56: 01=ON, 00=OFF)
  * Dial Calibration & Speedo Scaling (0xE2-0xED)

- New Style ("Kombi 2000", 93C86, 2048 bytes, MY2001-2005):
  * Auto-detects native 8-bit dumps vs 16-bit byte-swapped programmer dumps
  * VIN (0x000-0x010), BCD Part Number (0x01D-0x022), DSN (0x023)
  * Parameterkodierung (0x032-0x039) bit-level decode & tell-tale driver health check
  * Menuekonfiguration (0x03A-0x041) default & knob-twist units (MPH/km/h, MPG/l/100km, C/F, 12h/24h)
  * Spoiler Thresholds (0x050-0x051), K-Zahl Pulses/km (0x052-0x053), Tank Offset (0x056)
  * VDO BCD Production Timestamps (0x0D4, 0x0DA, 0x0F0) & Firmware Index (0x0E5-0x0E7)
  * Primary (0x192-0x19B) & Secondary (0x184-0x18D) Speedometer Stepper Curves (5x uint16 LE)
  * Fuel Tank Curves X/Y/Z (0x202-0x235), LCD Voltage Bias (0x2C6), Oil Level Curve (0x380-0x3AD)
  * Event Memory Active Bitmask (0x6F4-0x6F5) & Odometer History (0x644-0x65B)
  * Primary (0x300-0x31F) & Backup (0x500-0x51F) Encrypted Odometer Blocks & rolling parity check

Usage:
    python3 tools/cluster_analyzer.py dump.bin
    python3 tools/cluster_analyzer.py dump1.bin --compare dump2.bin
"""

import argparse
import struct
import sys
from pathlib import Path


DSN_DESCRIPTIONS = {
    0x14: "K20 (MY2001 996 Carrera / Early CAN)",
    0x15: "K21 (MY2001 986 Boxster / Boxster S)",
    0x16: "K22 (MY2001 996 Turbo / GT2)",
    0x17: "K23 (MY2002 996 Carrera / Turbo)",
    0x18: "K24 (MY2002 986 Boxster / Boxster S)",
    0x19: "K25 (MY2002 996 Facelift)",
    0x1A: "K26 (MY2003-2004 986 Boxster / Boxster S Facelift)",
    0x1B: "K27 (MY2003 996 Carrera Dot-Matrix)",
    0x20: "K32 (MY2003-2005 996 Carrera / Turbo / GT3)",
    0x32: "K50 (Replacement Service Dataset)",
}

LANGUAGES = {
    0: "German (Deutsch)",
    1: "English",
    2: "French (Francais)",
    3: "Italian (Italiano)",
    4: "Spanish (Espanol)",
    5: "Japanese",
}

CONSUMPTION_UNITS = {
    0: "l/100km (EU/RDW)",
    1: "km/l (Japan)",
    2: "MPG (US)",
    3: "MPG (UK Imperial)",
}

KNOWN_SPEEDO_CURVES = {
    (0, 1225, 11639, 28300, 39050): "Factory UK 986 Boxster S (180 mph dial, +4.4% EU margin)",
    (0, 1237, 11650, 31600, 39221): "Factory UK 996 Carrera K23 (180/200 mph dial)",
    (0, 639, 11639, 25399, 38993): "Factory RDW 986 Boxster 2.7L (250 km/h dial - OVER-READS +15.3% on 180 mph dial!)",
    (0, 639, 11639, 29275, 38944): "Factory RDW 986 Boxster S 3.2L (280 km/h dial)",
    (0, 768, 11650, 31600, 39221): "Factory RDW 996 Carrera / Turbo (300 km/h dial)",
    (0, 1609, 11639, 28968, 39050): "Calibrated UK 180 mph - True 1:1 GPS (0.0 mph error)",
    (0, 1562, 11639, 28124, 39050): "Calibrated UK 180 mph - +3.0% Safety Cushion",
}

EVENT_MEMORY_NAMES = [
    (0, 0, "Brake fluid level (Bremsfluessigkeitsstand)"),
    (0, 1, "Brake pad wear (Bremsbelagverschleiss)"),
    (0, 2, "Coolant level (Kuehlmittelstand)"),
    (0, 3, "Coolant over-temperature (Kuehlmitteltemperatur zu hoch)"),
    (0, 4, "Oil pressure (Oeldruck)"),
    (0, 5, "Oil level (Oelstand)"),
    (0, 6, "Roll-over bar (Ueberrollbuegel)"),
    (0, 7, "Airbag warning (Airbag)"),
    (1, 0, "Check Engine (MIL)"),
    (1, 1, "ABD / TC / PSM intervention"),
    (1, 2, "Brake booster (Bremskraftverstaerker)"),
    (1, 3, "Engine bay blower (Motorraumgeblaese)"),
]


def read_dump(filepath: str) -> bytes:
    """Read binary dump file."""
    with open(filepath, 'rb') as f:
        return f.read()


def detect_cluster_type(data: bytes) -> str:
    """Detect cluster type based on dump size."""
    size = len(data)
    if size == 256:
        return "old_style"  # 93C56B
    elif size == 2048:
        return "new_style"  # 93C86
    else:
        return f"unknown ({size} bytes)"


def is_byteswapped_93c86(data: bytes) -> bool:
    """Detect if a 2048-byte 93C86 dump was read with 16-bit word byte-swapping."""
    if len(data) < 0x24:
        return False
    # Native 8-bit VIN starts with "WP0" (57 50 30); 16-bit byte-swapped starts with "PW" (50 57)
    if data[0:2] == b'PW' and data[2:4] in (b'Z0', b'A0', b'C0', b'B0'):
        return True
    # Also check BCD part number at 0x01D: native has 09 86 or 09 96 at 0x1D-0x1E
    if data[0x1C:0x1E] in (b'\x09\x86', b'\x09\x96') and data[0x1D:0x1F] not in (b'\x09\x86', b'\x09\x96'):
        return True
    return False


def byteswap_16(data: bytes) -> bytes:
    """Swap adjacent bytes in every 16-bit word."""
    out = bytearray(len(data))
    for i in range(0, len(data) - 1, 2):
        out[i] = data[i + 1]
        out[i + 1] = data[i]
    if len(data) % 2 == 1:
        out[-1] = data[-1]
    return bytes(out)


def extract_vin_old_style(data: bytes) -> str:
    """Extract VIN from old-style cluster (93C56B)."""
    if len(data) < 0x29:
        return "(dump too small)"

    vin_part1 = data[0x18:0x20]  # 8 bytes
    vin_part2 = data[0x20:0x29]  # 9 bytes

    vin = ""
    for byte in vin_part1 + vin_part2:
        if 0x20 <= byte <= 0x7E:
            vin += chr(byte)
        else:
            vin += "?"

    if vin and not vin[0].isalnum():
        vin_area = data[0x10:0x30]
        extracted = ""
        for byte in vin_area:
            if 0x30 <= byte <= 0x5A:
                extracted += chr(byte)
        if len(extracted) >= 17:
            return extracted[:17] + " (may need byte swap verification)"

    return vin if vin.replace("?", "") else "(could not extract - check byte swap)"


def extract_vin_new_style(data: bytes) -> str:
    """Extract 17-character ASCII VIN from new-style cluster (0x000-0x010)."""
    vin_area = data[0x00:0x11]
    vin = "".join(chr(b) if 0x20 <= b <= 0x7E else "?" for b in vin_area)
    return vin.strip() if vin else "(not found)"


def extract_part_and_dsn_new_style(data: bytes) -> dict:
    """Extract BCD Porsche part number (0x01D-0x022) and DSN (0x023)."""
    bcd = data[0x01D:0x023]
    bcd_str = bcd.hex().upper()
    if len(bcd_str) == 12 and bcd_str.startswith("0"):
        formatted_part = f"{bcd_str[1:4]}.{bcd_str[4:7]}.{bcd_str[7:10]}.{bcd_str[10:12]}"
    else:
        formatted_part = bcd_str

    dsn_byte = data[0x023]
    dsn_code = f"K{dsn_byte}"
    dsn_desc = DSN_DESCRIPTIONS.get(dsn_byte, f"{dsn_code} (0x{dsn_byte:02X})")
    return {
        "raw_bcd": bcd_str,
        "part_number": formatted_part,
        "dsn_byte": f"0x{dsn_byte:02X}",
        "dsn_code": dsn_code,
        "dsn_description": dsn_desc,
    }


def decode_parameterkodierung(data: bytes) -> dict:
    """Decode the 8-byte Parameterkodierung block at 0x032-0x039."""
    p = data[0x032:0x03A]
    b0, b1, b2, b3, b4, b5, b6, b7 = p

    warnings = []
    if (b0 & 0x84) != 0x84:
        warnings.append(
            f"Byte 0 (0x032 = 0x{b0:02X}) is missing VDO baseline bits 0x84! "
            "Expected 0x84 (non-PSM) or 0x9E (with PSM)."
        )
    if (b4 & 0xB5) != 0xB5:
        warnings.append(
            f"Byte 4 (0x036 = 0x{b4:02X}) is missing tell-tale driver baseline bits 0xB5! "
            "Airbag key-on bulb check, seatbelt tell-tale, and lights-on chime will be DISABLED!"
        )

    psm_enabled = bool(b0 & 0x1A)
    platform = "996 (5-Gauge Pod: Oil Pressure + Voltmeter active)" if (b1 & 0x01) else "986 Boxster (3-Dial Cluster)"
    most_pcm = bool(b1 & 0x04)
    cruise_lamp = bool(b1 & 0x20)

    obc_items = []
    if b2 & 0x01:
        obc_items.append("Master ON")
    if b2 & 0x02:
        obc_items.append("Outside Temp")
    if b2 & 0x04:
        obc_items.append("Avg Speed")
    if b2 & 0x08:
        obc_items.append("Avg Consumption")
    if b2 & 0x10:
        obc_items.append("Range")
    if b2 & 0x20:
        obc_items.append("Turbo Boost")
    obc_status = ", ".join(obc_items) if obc_items else "DISABLED"

    chime_items = []
    if (b4 & 0xB5) == 0xB5:
        chime_items.append("Tell-Tale Drivers OK (Airbag/Seatbelt/Lights-On 0xB5)")
    else:
        chime_items.append(f"CORRUPTED Tell-Tale Drivers (0x{b4:02X})")
    if b4 & 0x02:
        chime_items.append("USA Seatbelt Chime")
    if b4 & 0x08:
        chime_items.append("USA Key-in-Ignition Chime")
    if b4 & 0x40:
        chime_items.append("Gulf 120 km/h Speed Chime")

    spoiler_profile = "986 Boxster Active Spoiler (0x07)" if (b5 & 0x01) else f"996 / Fixed Profile (0x{b5:02X})"

    return {
        "hex": " ".join(f"{b:02X}" for b in p),
        "psm": "WITH PSM (CAN brake/traction)" if psm_enabled else "WITHOUT PSM (Bosch ABS 5.3, discrete B22 handbrake)",
        "platform": platform,
        "most_pcm": "Installed" if most_pcm else "Not installed",
        "cruise_lamp": "Enabled" if cruise_lamp else "Disabled",
        "obc": f"0x{b2:02X} ({obc_status})",
        "infotainment_byte3": f"0x{b3:02X}",
        "telltales_byte4": f"0x{b4:02X} ({'; '.join(chime_items)})",
        "spoiler_byte5": spoiler_profile,
        "warnings": warnings,
    }


def decode_menu_half(half: bytes) -> str:
    """Decode a 4-byte half of Menuekonfiguration."""
    b0, b1, b2, b3 = half
    lang = LANGUAGES.get(b0 & 0x07, f"Lang({b0 & 0x07})")
    cons = CONSUMPTION_UNITS.get((b0 >> 3) & 0x03, f"Cons({(b0 >> 3) & 0x03})")
    dist = "km / km/h" if (b2 & 0x01) else "Miles / MPH"
    temp = "°C" if (b2 & 0x04) else "°F"
    clock = "24h" if (b2 & 0x08) else "12h"
    return f"{dist}, {cons}, {temp}, {clock}, {lang} [{' '.join(f'{x:02X}' for x in half)}]"


def decode_menuekonfiguration(data: bytes) -> dict:
    """Decode the 8-byte Menuekonfiguration block at 0x03A-0x041."""
    m = data[0x03A:0x042]
    return {
        "hex": " ".join(f"{b:02X}" for b in m),
        "default_half1": decode_menu_half(m[0:4]),
        "knob_twist_half2": decode_menu_half(m[4:8]),
    }


def decode_bcd_timestamp(raw6: bytes) -> str:
    """Format a 6-byte VDO BCD timestamp (DD MM YY HH MM SS)."""
    h = [f"{b:02X}" for b in raw6]
    return f"20{h[2]}-{h[1]}-{h[0]} {h[3]}:{h[4]}:{h[5]} ({' '.join(h)})"


def decode_speedo_curve(raw10: bytes) -> dict:
    """Decode a 10-byte (5x uint16 LE) speedometer stepper curve."""
    words = struct.unpack("<5H", raw10)
    w0, w1, w2, w3, w4 = words
    name = KNOWN_SPEEDO_CURVES.get(words, "Custom / Uncatalogued Curve")

    # Calculate indicated speed on a UK 180 mph dial at true 50.0 mph (80.47 km/h -> v = 8047)
    indicated_50mph = None
    if w3 > w1 and w4 > w2:
        v_50 = 8046.72
        stepper_pos = w2 + ((v_50 - w1) / (w3 - w1)) * (w4 - w2)
        # On a physical UK 180 mph dial, 10.0 mph is at stepper 11639 and 180.0 mph is at stepper 39050
        dial_mph = 10.0 + ((stepper_pos - 11639.0) / (39050.0 - 11639.0)) * 170.0
        indicated_50mph = round(dial_mph, 2)

    return {
        "hex": " ".join(f"{b:02X}" for b in raw10),
        "words": list(words),
        "x1_kmh": f"{w1 / 100.0:.2f} km/h ({w1 / 160.9344:.2f} mph) -> Stepper {w2}",
        "x2_kmh": f"{w3 / 100.0:.2f} km/h ({w3 / 160.9344:.2f} mph) -> Stepper {w4}",
        "profile_name": name,
        "indicated_at_50mph_uk_dial": f"{indicated_50mph} mph" if indicated_50mph is not None else "N/A",
    }


def extract_vehicle_type_old_style(data: bytes) -> dict:
    """Extract vehicle type from old-style cluster (0x35-0x36)."""
    result = {}
    if len(data) > 0x36:
        type_bytes = data[0x35:0x37]
        result['offset'] = '0x35-0x36'
        result['hex'] = type_bytes.hex()

        if type_bytes == b'\x09\x86':
            result['model'] = "986 Boxster"
        elif type_bytes == b'\x09\x96':
            result['model'] = "996 Carrera"
        elif type_bytes == b'\x86\x09':
            result['model'] = "986 Boxster (byte-swapped)"
        elif type_bytes == b'\x96\x09':
            result['model'] = "996 Carrera (byte-swapped)"
        else:
            result['model'] = f"Unknown ({type_bytes.hex()})"

    return result


def extract_pst2_mode_old_style(data: bytes) -> dict:
    """Extract PST2 mode byte from old-style cluster (0x3B)."""
    result = {}
    if len(data) > 0x3B:
        mode_byte = data[0x3B]
        result['offset'] = '0x3B'
        result['value'] = f"0x{mode_byte:02X}"
        if mode_byte == 0x06:
            result['mode'] = "986 Boxster mode"
        elif mode_byte == 0x08:
            result['mode'] = "996 Carrera mode"
        else:
            result['mode'] = f"Unknown (0x{mode_byte:02X})"
    return result


def extract_obc_old_style(data: bytes) -> dict:
    """Extract OBC status from old-style cluster (0x47)."""
    result = {}
    if len(data) > 0x47:
        obc_byte = data[0x47]
        result['offset'] = '0x47'
        result['value'] = f"0x{obc_byte:02X}"
        result['status'] = "DISABLED" if obc_byte == 0x00 else ("ENABLED" if obc_byte == 0x1F else f"UNKNOWN (0x{obc_byte:02X})")
    return result


def extract_oil_pressure_old_style(data: bytes) -> dict:
    """Extract oil pressure gauge status from old-style cluster (0x49)."""
    result = {}
    if len(data) > 0x49:
        oil_byte = data[0x49]
        result['offset'] = '0x49'
        result['value'] = f"0x{oil_byte:02X}"
        result['status'] = "ENABLED" if oil_byte == 0x3C else ("DISABLED" if oil_byte == 0x50 else f"UNKNOWN (0x{oil_byte:02X})")
    return result


def extract_voltmeter_old_style(data: bytes) -> dict:
    """Extract voltmeter status from old-style cluster (0x56)."""
    result = {}
    if len(data) > 0x56:
        volt_byte = data[0x56]
        result['offset'] = '0x56'
        result['value'] = f"0x{volt_byte:02X}"
        result['status'] = "ENABLED" if volt_byte == 0x01 else ("DISABLED" if volt_byte == 0x00 else f"UNKNOWN (0x{volt_byte:02X})")
    return result


def extract_dial_calibration_old_style(data: bytes) -> dict:
    """Extract dial calibration data from old-style cluster (0xE2-0xED)."""
    result = {}
    if len(data) > 0xED:
        cal_bytes = data[0xE2:0xEE]
        result['offset'] = '0xE2-0xED'
        result['hex'] = cal_bytes.hex()
    return result


def decode_93c86_odometer_block(block: bytes) -> float:
    """Decode a single 32-byte 93C86 odometer block into its base km contribution."""
    if len(block) != 32 or block == b"\xFF" * 32:
        return 0.0

    w0 = block[0] | (block[1] << 8)
    base_chunks = (0xFFFF - w0 - 1) & 0xFFFF
    base_km = base_chunks * 32

    h1_words = [block[i] | (block[i + 1] << 8) for i in range(0, 16, 2)]
    h2_words = [(block[i] << 8) | block[i + 1] for i in range(16, 32, 2)]

    diffs = [h2_words[i] - h1_words[i] for i in range(8)]
    active = [i for i in range(8) if diffs[i] == (1 << i)]

    if not active:
        state = 0
    elif len(active) == 8:
        state = 8
    elif active[0] == 0:
        state = len(active)
    else:
        state = active[0] + 8

    return float(base_km + state * 2)


def extract_mileage_data(data: bytes, cluster_type: str) -> dict:
    """Extract mileage data areas, decode odometer, and verify Primary vs Backup parity."""
    result = {}

    if cluster_type == "old_style":
        result['primary'] = {
            'offset': '0x00-0x0F',
            'hex': data[0x00:0x10].hex(),
            'note': '16 bytes - early 93C56B encrypted mileage'
        }

    elif cluster_type == "new_style" and len(data) >= 0x520:
        pri = data[0x300:0x320]
        bak = data[0x500:0x520]

        pri_km = decode_93c86_odometer_block(pri)
        bak_km = decode_93c86_odometer_block(bak)
        total_km = int(round((pri_km + bak_km) / 2.0))
        total_miles = round(total_km * 0.621371)

        result['decoded_km'] = total_km
        result['decoded_miles'] = total_miles
        result['pri_km'] = int(pri_km)
        result['bak_km'] = int(bak_km)

        result['primary'] = {
            'offset': '0x300-0x31F',
            'hex': pri.hex(),
            'note': f'Primary mileage block ({int(pri_km):,} km)'
        }
        result['backup'] = {
            'offset': '0x500-0x51F',
            'hex': bak.hex(),
            'note': f'Backup mileage block ({int(bak_km):,} km)'
        }

        if pri == bak:
            result['match'] = True
            result['parity_note'] = f"100% byte-identical ({total_km:,} km, even distance)"
        else:
            diffs = [(i, pri[i], bak[i]) for i in range(32) if pri[i] != bak[i]]
            result['match'] = False
            if abs(pri_km - bak_km) == 2.0 or (len(diffs) == 1 and bin(diffs[0][1] ^ diffs[0][2]).count("1") == 1):
                idx = diffs[0][0] if diffs else 0x19
                result['parity_note'] = (
                    f"Valid odd-kilometer dual-buffer half-step ({int(pri_km):,} km vs {int(bak_km):,} km -> {total_km:,} km / {total_miles:,} mi). "
                    f"Word offset at +0x{idx:02X} is normal factory interleaving."
                )
            else:
                result['parity_note'] = f"WARNING: {len(diffs)} byte(s) differ between Primary and Backup!"

    return result


def analyze_dump(filepath: str) -> dict:
    """Analyze a single dump file."""
    raw_data = read_dump(filepath)
    cluster_type = detect_cluster_type(raw_data)
    swapped = False
    data = raw_data

    if cluster_type == "new_style" and is_byteswapped_93c86(raw_data):
        swapped = True
        data = byteswap_16(raw_data)

    result = {
        'file': filepath,
        'size': len(raw_data),
        'cluster_type': cluster_type,
        'byteswapped_16bit': swapped,
    }

    if cluster_type == "old_style":
        result['vin'] = extract_vin_old_style(data)
        result['vehicle_type'] = extract_vehicle_type_old_style(data)
        result['pst2_mode'] = extract_pst2_mode_old_style(data)
        result['obc'] = extract_obc_old_style(data)
        result['oil_pressure'] = extract_oil_pressure_old_style(data)
        result['voltmeter'] = extract_voltmeter_old_style(data)
        result['dial_calibration'] = extract_dial_calibration_old_style(data)

    elif cluster_type == "new_style":
        result['vin'] = extract_vin_new_style(data)
        result['id'] = extract_part_and_dsn_new_style(data)
        result['parameterkodierung'] = decode_parameterkodierung(data)
        result['menuekonfiguration'] = decode_menuekonfiguration(data)
        result['spoiler_retract_kmh'] = data[0x050]
        result['spoiler_extend_kmh'] = data[0x051]
        result['k_zahl'] = struct.unpack("<H", data[0x052:0x054])[0]
        result['tank_offset'] = data[0x056]
        result['sw_version'] = " ".join(f"{b:02X}" for b in data[0x0E5:0x0E8])
        result['timestamps'] = {
            'ts1_0x0D4': decode_bcd_timestamp(data[0x0D4:0x0DA]),
            'ts2_0x0DA': decode_bcd_timestamp(data[0x0DA:0x0E0]),
            'ts3_0x0F0': decode_bcd_timestamp(data[0x0F0:0x0F6]),
        }
        result['speedo_primary'] = decode_speedo_curve(data[0x192:0x19C])
        result['speedo_secondary'] = decode_speedo_curve(data[0x184:0x18E])

        tank_x = struct.unpack("<6H", data[0x21A:0x226])
        result['tank_curve_x_ohms'] = [round(w * 0.1, 1) for w in tank_x]
        result['lcd_bias_0x2C6'] = f"0x{data[0x2C6]:02X} ({data[0x2C6]})"

        oil_b1 = data[0x38A:0x394]
        if oil_b1.startswith(b'\x18\x00'):
            result['oil_curve_profile'] = "MY2001 K21 Profile (0x38A = 18 00 28 00 ...)"
        elif oil_b1.startswith(b'\x12\x00'):
            result['oil_curve_profile'] = "MY2002+ K23/K24 Profile (0x38A = 12 00 22 00 ...)"
        else:
            result['oil_curve_profile'] = f"Custom ({oil_b1[:4].hex()})"

        ev0, ev1 = data[0x6F4], data[0x6F5]
        active_events = []
        for byte_idx, bit_idx, name in EVENT_MEMORY_NAMES:
            val = ev0 if byte_idx == 0 else ev1
            if val & (1 << bit_idx):
                active_events.append(name)
        result['event_memory'] = {
            'raw': f"{ev0:02X} {ev1:02X}",
            'active_events': active_events if active_events else ["None (00 00)"],
        }

    result['mileage'] = extract_mileage_data(data, cluster_type)
    return result


def print_analysis(analysis: dict):
    """Print formatted analysis results."""
    print("=" * 78)
    print(f"FILE: {analysis['file']}")
    print(f"SIZE: {analysis['size']} bytes")

    cluster_type = analysis['cluster_type']
    if cluster_type == "old_style":
        print("TYPE: Old Style (93C56B, 256 bytes, MY1997-2000)")
    elif cluster_type == "new_style":
        order_str = "16-bit byte-swapped (auto-unswapped for analysis)" if analysis.get('byteswapped_16bit') else "Native 8-bit linear"
        print(f"TYPE: New Style ('Kombi 2000' 93C86, 2048 bytes, MY2001-2005) [{order_str}]")
    else:
        print(f"TYPE: {cluster_type}")

    print("-" * 78)
    if 'vin' in analysis:
        print(f"VIN [0x000-0x010]:          {analysis['vin']}")

    if cluster_type == "old_style":
        vt = analysis.get('vehicle_type', {})
        print(f"VEHICLE TYPE [0x35-0x36]:   {vt.get('model', 'N/A')} ({vt.get('hex', '')})")
        pst2 = analysis.get('pst2_mode', {})
        print(f"PST2 MODE [0x3B]:           {pst2.get('mode', 'N/A')} ({pst2.get('value', '')})")
        obc = analysis.get('obc', {})
        print(f"OBC (TRIP COMPUTER) [0x47]: {obc.get('status', 'N/A')} ({obc.get('value', '')})")
        oil = analysis.get('oil_pressure', {})
        print(f"OIL PRESSURE GAUGE [0x49]:  {oil.get('status', 'N/A')} ({oil.get('value', '')})")
        volt = analysis.get('voltmeter', {})
        print(f"VOLTMETER [0x56]:           {volt.get('status', 'N/A')} ({volt.get('value', '')})")
        cal = analysis.get('dial_calibration', {})
        print(f"DIAL CALIBRATION [0xE2-ED]: {cal.get('hex', '')}")

    elif cluster_type == "new_style":
        ident = analysis['id']
        print(f"PART NUMBER [0x01D-0x022]:  {ident['part_number']} (BCD: {ident['raw_bcd']})")
        print(f"DATASET (DSN) [0x023]:      {ident['dsn_description']}")
        print(f"SW VERSION [0x0E5-0x0E7]:   {analysis['sw_version']}")
        print(f"VDO FLASH DATE [0x0D4]:     {analysis['timestamps']['ts1_0x0D4']}")
        print(f"VDO EOL TEST DATE [0x0F0]:  {analysis['timestamps']['ts3_0x0F0']}")
        print("-" * 78)

        pk = analysis['parameterkodierung']
        print(f"PARAMETERKODIERUNG [0x032-0x039]: {pk['hex']}")
        print(f"  * Platform / Pod:         {pk['platform']}")
        print(f"  * Brake / Stability:      {pk['psm']}")
        print(f"  * On-Board Computer:      {pk['obc']}")
        print(f"  * Tell-Tales & Chimes:    {pk['telltales_byte4']}")
        print(f"  * Spoiler Profile:        {pk['spoiler_byte5']}")
        print(f"  * MOST/PCM & Cruise:      MOST={pk['most_pcm']}, Cruise Lamp={pk['cruise_lamp']}")
        for w in pk['warnings']:
            print(f"  [!] WARNING: {w}")

        mk = analysis['menuekonfiguration']
        print("-" * 78)
        print(f"MENUEKONFIGURATION [0x03A-0x041]: {mk['hex']}")
        print(f"  * Default (Half 1):       {mk['default_half1']}")
        print(f"  * Knob Twist (Half 2):    {mk['knob_twist_half2']}")

        print("-" * 78)
        print("CALIBRATION & GAUGE CURVES:")
        print(f"  * K-Zahl [0x052-0x053]:   {analysis['k_zahl']} pulses/km")
        print(
            f"  * Spoiler [0x050-0x051]:  Extend @ {analysis['spoiler_extend_kmh']} km/h, "
            f"Retract @ {analysis['spoiler_retract_kmh']} km/h"
        )
        sp = analysis['speedo_primary']
        print(f"  * Primary Speedo [0x192]: {sp['hex']}")
        print(f"    - Words (uint16 LE):    {sp['words']}")
        print(f"    - Breakpoints:          X1={sp['x1_kmh']} | X2={sp['x2_kmh']}")
        print(f"    - Matched Profile:      {sp['profile_name']}")
        print(f"    - At True 50.0 mph:     Indicates {sp['indicated_at_50mph_uk_dial']} on UK 180 mph face")
        print(f"  * Tank Curve X [0x21A]:   {analysis['tank_curve_x_ohms']} Ohms (Empty -> Full)")
        print(f"  * Oil Curve [0x380-3AD]:  {analysis['oil_curve_profile']}")
        print(f"  * LCD Bias [0x2C6]:       {analysis['lcd_bias_0x2C6']}")
        ev = analysis['event_memory']
        print(f"  * Event Memory [0x6F4]:   [{ev['raw']}] {', '.join(ev['active_events'])}")

    print("-" * 78)
    print("MILEAGE DATA:")
    mileage = analysis.get('mileage', {})
    if 'decoded_km' in mileage:
        print(f"  * Decoded Odometer:       {mileage['decoded_miles']:,} miles ({mileage['decoded_km']:,} km)")
    for key in ('primary', 'backup'):
        if key in mileage:
            val = mileage[key]
            print(f"  * {key.capitalize()} [{val['offset']}]:       {val.get('note', '')}")
            hex_str = val['hex']
            for i in range(0, len(hex_str), 32):
                print(f"      {hex_str[i:i+32]}")
    if 'parity_note' in mileage:
        print(f"  * Parity Status:          {mileage['parity_note']}")
    print("=" * 78)


def compare_dumps(data1: bytes, data2: bytes, name1: str, name2: str) -> list:
    """Compare two dumps and return differences."""
    differences = []
    min_len = min(len(data1), len(data2))

    diff_ranges = []
    in_diff = False
    diff_start = 0

    for i in range(min_len):
        if data1[i] != data2[i]:
            if not in_diff:
                in_diff = True
                diff_start = i
        else:
            if in_diff:
                in_diff = False
                diff_ranges.append((diff_start, i))

    if in_diff:
        diff_ranges.append((diff_start, min_len))

    merged = []
    for start, end in diff_ranges:
        if merged and start - merged[-1][1] <= 4:
            merged[-1] = (merged[-1][0], end)
        else:
            merged.append((start, end))

    for start, end in merged:
        differences.append({
            'offset': f"0x{start:03X}-0x{end-1:03X}",
            'length': end - start,
            'file1': data1[start:end].hex(),
            'file2': data2[start:end].hex()
        })

    if len(data1) != len(data2):
        differences.append({
            'note': f"File sizes differ: {len(data1)} vs {len(data2)} bytes"
        })

    return differences


def print_comparison(diff_list: list, file1: str, file2: str):
    """Print comparison results."""
    print("=" * 78)
    print("COMPARISON RESULTS")
    print(f"  File 1: {file1}")
    print(f"  File 2: {file2}")
    print("-" * 78)

    if not diff_list:
        print("  Files are IDENTICAL")
    else:
        print(f"  Found {len(diff_list)} difference region(s):")
        print()
        for diff in diff_list:
            if 'note' in diff:
                print(f"  NOTE: {diff['note']}")
            else:
                print(f"  OFFSET: {diff['offset']} ({diff['length']} bytes)")
                print(f"    File 1: {diff['file1']}")
                print(f"    File 2: {diff['file2']}")
                print()

    print("=" * 78)


def main():
    parser = argparse.ArgumentParser(
        description='Analyze Porsche 986/996 instrument cluster EEPROM dumps (93C56B & 93C86)',
    )
    parser.add_argument('dump', help='EEPROM dump file to analyze')
    parser.add_argument('--compare', '-c', help='Second dump file to compare')

    args = parser.parse_args()

    if not Path(args.dump).exists():
        print(f"Error: File not found: {args.dump}")
        sys.exit(1)

    analysis1 = analyze_dump(args.dump)
    print_analysis(analysis1)

    if args.compare:
        if not Path(args.compare).exists():
            print(f"Error: File not found: {args.compare}")
            sys.exit(1)

        analysis2 = analyze_dump(args.compare)
        print_analysis(analysis2)

        d1 = read_dump(args.dump)
        d2 = read_dump(args.compare)
        if len(d1) == 2048 and is_byteswapped_93c86(d1):
            d1 = byteswap_16(d1)
        if len(d2) == 2048 and is_byteswapped_93c86(d2):
            d2 = byteswap_16(d2)

        differences = compare_dumps(d1, d2, args.dump, args.compare)
        print_comparison(differences, args.dump, args.compare)


if __name__ == '__main__':
    main()
