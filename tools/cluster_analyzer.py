#!/usr/bin/env python3
"""
Porsche 986/996 Instrument Cluster EEPROM Analyzer

Analyzes cluster EEPROM dumps (93C56B or 93C86) and extracts:
- VIN
- Model type (986/996)
- PST2 mode byte
- Oil pressure gauge status
- Voltmeter status
- Mileage data (raw hex, encoding not yet decoded)

Usage:
    python3 cluster_analyzer.py dump.bin
    python3 cluster_analyzer.py dump1.bin --compare dump2.bin

Old Style (93C56B) Key Offsets:
    0x00-0x0F  Mileage (encrypted)
    0x18-0x1F  VIN part 1
    0x20-0x28  VIN part 2
    0x35-0x36  Vehicle Type (09 86=986, 09 96=996)
    0x3B       PST2 Mode (06=986, 08=996)
    0x49       Oil Pressure Gauge (3C=ON, 50=OFF)
    0x56       Voltmeter (01=ON, 00=OFF)
    0xE2-0xED  Dial Calibration

New Style (93C86) Key Offsets:
    0x000-0x00F  VIN
    0x300-0x31F  Mileage (primary)
    0x500-0x51F  Mileage (backup)
"""

import argparse
import sys
from pathlib import Path


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


def extract_vin_old_style(data: bytes) -> str:
    """Extract VIN from old-style cluster (93C56B).

    VIN is at:
    - Row 0x10, columns 08-0F (bytes 0x18-0x1F) - 8 chars
    - Row 0x20, columns 00-08 (bytes 0x20-0x28) - 9 chars
    Total: 17 characters
    """
    if len(data) < 0x29:
        return "(dump too small)"

    vin_part1 = data[0x18:0x20]  # 8 bytes
    vin_part2 = data[0x20:0x29]  # 9 bytes

    vin = ""
    for byte in vin_part1 + vin_part2:
        if 0x20 <= byte <= 0x7E:  # Printable ASCII
            vin += chr(byte)
        else:
            vin += "?"

    # Try to clean up if byte-swapped
    if vin and not vin[0].isalnum():
        # May need byte swap - try to find valid VIN pattern
        vin_area = data[0x10:0x30]
        extracted = ""
        for byte in vin_area:
            if 0x30 <= byte <= 0x5A:  # 0-9, A-Z
                extracted += chr(byte)
        if len(extracted) >= 17:
            return extracted[:17] + " (may need byte swap verification)"

    return vin if vin.replace("?", "") else "(could not extract - check byte swap)"


def extract_vin_new_style(data: bytes) -> str:
    """Extract VIN from new-style cluster (93C86).

    VIN is stored in the first line (0x000-0x00F).
    """
    vin_area = data[0x00:0x11]

    # Extract readable ASCII
    vin = ""
    for byte in vin_area:
        if 0x20 <= byte <= 0x7E:  # Printable ASCII
            vin += chr(byte)

    # VIN should be 17 characters
    vin = vin.strip()
    if len(vin) >= 17:
        return vin[:17]

    return vin if vin else "(not found)"


def extract_vehicle_type_old_style(data: bytes) -> dict:
    """Extract vehicle type from old-style cluster.

    Located at 0x35-0x36 (row 0x30, columns 05-06).
    """
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
    """Extract PST2 mode byte from old-style cluster.

    Located at 0x3B (row 0x30, column 0B).
    06 = 986 Boxster mode
    08 = 996 Carrera mode
    """
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


def extract_oil_pressure_old_style(data: bytes) -> dict:
    """Extract oil pressure gauge status from old-style cluster.

    Located at 0x49 (row 0x40, column 09).
    3C = ENABLED
    50 = DISABLED
    """
    result = {}
    if len(data) > 0x49:
        oil_byte = data[0x49]
        result['offset'] = '0x49'
        result['value'] = f"0x{oil_byte:02X}"

        if oil_byte == 0x3C:
            result['status'] = "ENABLED"
        elif oil_byte == 0x50:
            result['status'] = "DISABLED"
        else:
            result['status'] = f"UNKNOWN (0x{oil_byte:02X})"

    return result


def extract_voltmeter_old_style(data: bytes) -> dict:
    """Extract voltmeter status from old-style cluster.

    Located at 0x56 (row 0x50, column 06).
    01 = ENABLED
    00 = DISABLED
    """
    result = {}
    if len(data) > 0x56:
        volt_byte = data[0x56]
        result['offset'] = '0x56'
        result['value'] = f"0x{volt_byte:02X}"

        if volt_byte == 0x01:
            result['status'] = "ENABLED"
        elif volt_byte == 0x00:
            result['status'] = "DISABLED"
        else:
            result['status'] = f"UNKNOWN (0x{volt_byte:02X})"

    return result


def extract_dial_calibration_old_style(data: bytes) -> dict:
    """Extract dial calibration data from old-style cluster.

    Located at 0xE2-0xED (row 0xE0, columns 02-0D).
    """
    result = {}
    if len(data) > 0xED:
        cal_bytes = data[0xE2:0xEE]
        result['offset'] = '0xE2-0xED'
        result['hex'] = cal_bytes.hex()
        result['note'] = 'Dial calibration data (interpretation TBD)'

    return result


def extract_mileage_data(data: bytes, cluster_type: str) -> dict:
    """Extract mileage data areas.

    Note: Mileage is ENCRYPTED - we can only show the raw hex.
    """
    result = {}

    if cluster_type == "old_style":
        # Bytes 0x00-0x0F contain encrypted mileage
        result['primary'] = {
            'offset': '0x00-0x0F',
            'hex': data[0x00:0x10].hex(),
            'note': '16 bytes - encrypted mileage'
        }

    elif cluster_type == "new_style":
        # Primary: 0x300-0x31F
        # Backup: 0x500-0x51F
        if len(data) >= 0x520:
            result['primary'] = {
                'offset': '0x300-0x31F',
                'hex': data[0x300:0x320].hex(),
                'note': 'Primary mileage block (32 bytes, encrypted)'
            }
            result['backup'] = {
                'offset': '0x500-0x51F',
                'hex': data[0x500:0x520].hex(),
                'note': 'Backup mileage block (32 bytes, encrypted)'
            }

            # Check if primary matches backup
            if data[0x300:0x320] == data[0x500:0x520]:
                result['match'] = True
            else:
                result['match'] = False
                result['warning'] = "Primary and backup mileage blocks differ!"

    return result


def extract_model_code_new_style(data: bytes) -> str:
    """Extract model code from new-style cluster."""
    if len(data) < 0x30:
        return "(dump too small)"

    model_area = data[0x10:0x30]
    model_str = model_area.hex()

    if "0996" in model_str or "9609" in model_str:
        return "996 Carrera"
    elif "0986" in model_str or "8609" in model_str:
        return "986 Boxster"

    return "(not identified)"


def compare_dumps(data1: bytes, data2: bytes, name1: str, name2: str) -> list:
    """Compare two dumps and return differences."""
    differences = []

    min_len = min(len(data1), len(data2))

    # Find differing bytes
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

    # Merge nearby ranges
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


def analyze_dump(filepath: str) -> dict:
    """Analyze a single dump file."""
    data = read_dump(filepath)
    cluster_type = detect_cluster_type(data)

    result = {
        'file': filepath,
        'size': len(data),
        'cluster_type': cluster_type
    }

    if cluster_type == "old_style":
        result['vin'] = extract_vin_old_style(data)
        result['vehicle_type'] = extract_vehicle_type_old_style(data)
        result['pst2_mode'] = extract_pst2_mode_old_style(data)
        result['oil_pressure'] = extract_oil_pressure_old_style(data)
        result['voltmeter'] = extract_voltmeter_old_style(data)
        result['dial_calibration'] = extract_dial_calibration_old_style(data)

    elif cluster_type == "new_style":
        result['vin'] = extract_vin_new_style(data)
        result['model'] = extract_model_code_new_style(data)

    result['mileage'] = extract_mileage_data(data, cluster_type)

    return result


def print_analysis(analysis: dict):
    """Print analysis results."""
    print("=" * 65)
    print(f"FILE: {analysis['file']}")
    print(f"SIZE: {analysis['size']} bytes")

    cluster_type = analysis['cluster_type']
    if cluster_type == "old_style":
        print(f"TYPE: Old Style (93C56B) - 256 bytes")
    elif cluster_type == "new_style":
        print(f"TYPE: New Style (93C86) - 2048 bytes")
    else:
        print(f"TYPE: {cluster_type}")

    print("-" * 65)

    if 'vin' in analysis:
        print(f"VIN: {analysis['vin']}")

    if 'vehicle_type' in analysis:
        vt = analysis['vehicle_type']
        print(f"VEHICLE TYPE: {vt.get('model', 'N/A')}")
        print(f"             [{vt.get('offset', '')} = {vt.get('hex', '')}]")

    if 'model' in analysis:
        print(f"MODEL: {analysis['model']}")

    if 'pst2_mode' in analysis:
        pst2 = analysis['pst2_mode']
        print(f"PST2 MODE: {pst2.get('mode', 'N/A')}")
        print(f"          [{pst2.get('offset', '')} = {pst2.get('value', '')}]")

    if 'oil_pressure' in analysis:
        oil = analysis['oil_pressure']
        print(f"OIL PRESSURE GAUGE: {oil.get('status', 'N/A')}")
        print(f"                   [{oil.get('offset', '')} = {oil.get('value', '')}]")

    if 'voltmeter' in analysis:
        volt = analysis['voltmeter']
        print(f"VOLTMETER: {volt.get('status', 'N/A')}")
        print(f"          [{volt.get('offset', '')} = {volt.get('value', '')}]")

    if 'dial_calibration' in analysis:
        cal = analysis['dial_calibration']
        print(f"DIAL CALIBRATION: [{cal.get('offset', '')}]")
        print(f"                  {cal.get('hex', '')}")

    print("-" * 65)
    print("MILEAGE DATA (encrypted):")

    mileage = analysis.get('mileage', {})
    for key, val in mileage.items():
        if key in ('primary', 'backup'):
            print(f"  {key.upper()}: [{val['offset']}]")
            # Print hex in readable chunks
            hex_str = val['hex']
            for i in range(0, len(hex_str), 32):
                print(f"    {hex_str[i:i+32]}")
        elif key == 'match':
            if val:
                print("  Primary/Backup: MATCH")
            else:
                print(f"  Primary/Backup: MISMATCH - {mileage.get('warning', '')}")

    print("=" * 65)


def print_comparison(diff_list: list, file1: str, file2: str):
    """Print comparison results."""
    print("=" * 65)
    print("COMPARISON RESULTS")
    print(f"  File 1: {file1}")
    print(f"  File 2: {file2}")
    print("-" * 65)

    if not diff_list:
        print("  Files are IDENTICAL")
    else:
        print(f"  Found {len(diff_list)} difference(s):")
        print()
        for diff in diff_list:
            if 'note' in diff:
                print(f"  NOTE: {diff['note']}")
            else:
                print(f"  OFFSET: {diff['offset']} ({diff['length']} bytes)")
                print(f"    File 1: {diff['file1']}")
                print(f"    File 2: {diff['file2']}")
                print()

    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(
        description='Analyze Porsche 986/996 instrument cluster EEPROM dumps',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Old Style (93C56B) Offsets:
  0x00-0x0F  Mileage (encrypted)
  0x18-0x1F  VIN part 1
  0x20-0x28  VIN part 2
  0x35-0x36  Vehicle Type (09 86=986, 09 96=996)
  0x3B       PST2 Mode (06=986, 08=996)
  0x49       Oil Pressure (3C=ON, 50=OFF)
  0x56       Voltmeter (01=ON, 00=OFF)
  0xE2-0xED  Dial Calibration

New Style (93C86) Offsets:
  0x000-0x00F  VIN
  0x300-0x31F  Mileage (primary)
  0x500-0x51F  Mileage (backup)
"""
    )
    parser.add_argument('dump', help='EEPROM dump file to analyze')
    parser.add_argument('--compare', '-c', help='Second dump file to compare')

    args = parser.parse_args()

    # Check file exists
    if not Path(args.dump).exists():
        print(f"Error: File not found: {args.dump}")
        sys.exit(1)

    # Analyze first dump
    analysis1 = analyze_dump(args.dump)
    print_analysis(analysis1)

    # Compare if second file provided
    if args.compare:
        if not Path(args.compare).exists():
            print(f"Error: File not found: {args.compare}")
            sys.exit(1)

        analysis2 = analyze_dump(args.compare)
        print_analysis(analysis2)

        data1 = read_dump(args.dump)
        data2 = read_dump(args.compare)

        differences = compare_dumps(data1, data2, args.dump, args.compare)
        print_comparison(differences, args.dump, args.compare)


if __name__ == '__main__':
    main()
