#!/usr/bin/env python3
"""
Porsche 986/996 Instrument Cluster EEPROM Analyzer

Analyzes cluster EEPROM dumps (93C56B or 93C86) and extracts:
- VIN
- Model type (986/996)
- OBC status
- Oil pressure gauge status
- PST2 mode byte
- Mileage data (raw hex, encoding not yet decoded)

Usage:
    python3 cluster_analyzer.py dump.bin
    python3 cluster_analyzer.py dump1.bin --compare dump2.bin
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

    VIN spans from middle of line 0x10 to first half of line 0x20.
    Note: Data may be byte-swapped depending on how it was read.
    """
    # Try to find VIN pattern - typically starts with W (Porsche) or other letters
    # VIN is 17 characters
    vin_area = data[0x10:0x30]

    # Try to extract readable ASCII
    vin = ""
    for byte in vin_area:
        if 0x20 <= byte <= 0x7E:  # Printable ASCII
            vin += chr(byte)

    # Clean up and try to find 17-char VIN
    vin = vin.strip()
    if len(vin) >= 17:
        # Look for VIN pattern
        for i in range(len(vin) - 16):
            potential_vin = vin[i:i+17]
            if potential_vin[0].isalpha():  # VINs start with a letter
                return potential_vin

    return vin if vin else "(could not extract - may need byte swap)"


def extract_vin_new_style(data: bytes) -> str:
    """Extract VIN from new-style cluster (93C86).

    VIN is stored in the first line (0x000).
    """
    vin_area = data[0x00:0x20]

    # Extract readable ASCII
    vin = ""
    for byte in vin_area:
        if 0x20 <= byte <= 0x7E:  # Printable ASCII
            vin += chr(byte)

    # VIN should be 17 characters starting with a letter
    vin = vin.strip()
    if len(vin) >= 17:
        return vin[:17]

    return vin if vin else "(not found)"


def extract_vehicle_type_old_style(data: bytes) -> dict:
    """Extract vehicle type from old-style cluster (0x26-0x27)."""
    result = {}
    if len(data) > 0x27:
        type_bytes = data[0x26:0x28]
        result['offset'] = '0x26-0x27'
        result['hex'] = type_bytes.hex()

        if type_bytes == b'\x09\x96' or type_bytes == b'\x96\x09':
            result['model'] = "996 Carrera"
        elif type_bytes == b'\x09\x86' or type_bytes == b'\x86\x09':
            result['model'] = "986 Boxster"
        else:
            result['model'] = f"Unknown ({type_bytes.hex()})"

    return result


def extract_model_code(data: bytes) -> str:
    """Extract model code from new-style cluster.

    Stored as "09 96" or "09 86" in lines 0x010-0x020.
    """
    if len(data) < 0x30:
        return "(dump too small)"

    model_area = data[0x10:0x30]

    # Look for model code patterns
    model_str = model_area.hex()

    if "0996" in model_str or "9609" in model_str:
        return "996 Carrera"
    elif "0986" in model_str or "8609" in model_str:
        return "986 Boxster"

    # Try ASCII
    for i in range(len(model_area) - 4):
        chunk = model_area[i:i+4]
        try:
            text = chunk.decode('ascii')
            if '996' in text or '986' in text:
                return text.strip()
        except:
            pass

    return "(not identified)"


def extract_pst2_mode(data: bytes) -> dict:
    """Extract PST2 mode byte from old-style cluster (0x2C)."""
    result = {}
    if len(data) > 0x2C:
        mode_byte = data[0x2C]
        result['offset'] = '0x2C'
        result['value'] = f"0x{mode_byte:02X}"

        if mode_byte == 0x7A:
            result['mode'] = "986 Boxster mode"
        elif mode_byte == 0x78:
            result['mode'] = "996 Carrera mode"
        else:
            result['mode'] = f"Unknown (0x{mode_byte:02X})"

    return result


def extract_obc_status(data: bytes, cluster_type: str) -> dict:
    """Extract OBC (On-Board Computer) enable status."""
    result = {}

    if cluster_type == "old_style":
        if len(data) > 0x2F:
            obc_byte = data[0x2F]
            result['offset'] = '0x2F'
            result['value'] = f"0x{obc_byte:02X}"
            if obc_byte == 0x00:
                result['status'] = "DISABLED"
            elif obc_byte == 0x1F:
                result['status'] = "ENABLED"
            else:
                result['status'] = f"UNKNOWN (0x{obc_byte:02X})"

    elif cluster_type == "new_style":
        result['offset'] = 'TBD'
        result['status'] = "Location not yet documented for new-style clusters"

    return result


def extract_oil_pressure_status(data: bytes, cluster_type: str) -> dict:
    """Extract oil pressure gauge enable status."""
    result = {}

    if cluster_type == "old_style":
        if len(data) > 0x31:
            oil_bytes = data[0x30:0x32]
            result['offset'] = '0x30-0x31'
            result['hex'] = oil_bytes.hex()

            # Check first nibble
            first_nibble = (oil_bytes[0] >> 4) & 0x0F
            if first_nibble == 0x0:
                result['status'] = "ENABLED"
            elif first_nibble == 0x5:
                result['status'] = "DISABLED"
            else:
                result['status'] = f"UNKNOWN (first nibble: {first_nibble:X})"

    elif cluster_type == "new_style":
        result['offset'] = 'TBD'
        result['status'] = "Location not yet documented for new-style clusters"

    return result


def extract_mileage_data(data: bytes, cluster_type: str) -> dict:
    """Extract mileage data areas.

    Note: Mileage is ENCRYPTED - we can only show the raw hex.
    The encoding algorithm has not been publicly documented.
    """
    result = {}

    if cluster_type == "old_style":
        # Line 0x00 contains repeated mileage values
        result['primary'] = {
            'offset': '0x00-0x0F',
            'hex': data[0x00:0x10].hex(),
            'note': 'First 16 bytes - encrypted mileage'
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
        result['pst2_mode'] = extract_pst2_mode(data)
        result['obc'] = extract_obc_status(data, cluster_type)
        result['oil_pressure'] = extract_oil_pressure_status(data, cluster_type)

    elif cluster_type == "new_style":
        result['vin'] = extract_vin_new_style(data)
        result['model'] = extract_model_code(data)
        result['obc'] = extract_obc_status(data, cluster_type)
        result['oil_pressure'] = extract_oil_pressure_status(data, cluster_type)

    result['mileage'] = extract_mileage_data(data, cluster_type)

    return result


def print_analysis(analysis: dict):
    """Print analysis results."""
    print("=" * 60)
    print(f"FILE: {analysis['file']}")
    print(f"SIZE: {analysis['size']} bytes")

    cluster_type = analysis['cluster_type']
    if cluster_type == "old_style":
        print(f"TYPE: Old Style (93C56B)")
    elif cluster_type == "new_style":
        print(f"TYPE: New Style (93C86)")
    else:
        print(f"TYPE: {cluster_type}")

    print("-" * 60)

    if 'vin' in analysis:
        print(f"VIN: {analysis['vin']}")

    if 'vehicle_type' in analysis:
        vt = analysis['vehicle_type']
        print(f"VEHICLE TYPE: {vt.get('model', 'N/A')} [{vt.get('offset', '')}={vt.get('hex', '')}]")

    if 'model' in analysis:
        print(f"MODEL: {analysis['model']}")

    if 'pst2_mode' in analysis:
        pst2 = analysis['pst2_mode']
        print(f"PST2 MODE: {pst2.get('mode', 'N/A')} [{pst2.get('offset', '')}={pst2.get('value', '')}]")

    if 'obc' in analysis:
        obc = analysis['obc']
        print(f"OBC: {obc.get('status', 'N/A')} [{obc.get('offset', '')}={obc.get('value', '')}]")

    if 'oil_pressure' in analysis:
        oil = analysis['oil_pressure']
        status = oil.get('status', 'N/A')
        offset = oil.get('offset', '')
        hex_val = oil.get('hex', '')
        if hex_val:
            print(f"OIL PRESSURE GAUGE: {status} [{offset}={hex_val}]")
        else:
            print(f"OIL PRESSURE GAUGE: {status}")

    print("-" * 60)
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

    print("=" * 60)


def print_comparison(diff_list: list, file1: str, file2: str):
    """Print comparison results."""
    print("=" * 60)
    print("COMPARISON RESULTS")
    print(f"  File 1: {file1}")
    print(f"  File 2: {file2}")
    print("-" * 60)

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

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Analyze Porsche 986/996 instrument cluster EEPROM dumps'
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
