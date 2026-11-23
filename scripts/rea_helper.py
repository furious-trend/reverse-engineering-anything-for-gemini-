#!/usr/bin/env python3
"""REA Helper: Standalone Reverse Engineering Companion for Antigravity & Gemini AI.

Zero-dependency Python utility providing static triage, PE/ELF parsing,
strings extraction, ASAR unpacking, APK inspection, and differential testing.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import struct
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def calculate_entropy(data: bytes) -> float:
    """Calculate Shannon entropy of a byte sequence (0.0 to 8.0)."""
    if not data:
        return 0.0
    entropy = 0.0
    length = len(data)
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    for count in counts:
        if count > 0:
            p = count / length
            entropy -= p * math.log2(p)
    return entropy


def identify_format(file_path: Path) -> Dict[str, Any]:
    """Identify file magic bytes, format, architecture, and entropy."""
    if not file_path.exists():
        return {"error": f"File not found: {file_path}"}

    file_size = file_path.stat().st_size
    with open(file_path, "rb") as f:
        header = f.read(4096)

    # Hashes
    import hashlib
    with open(file_path, "rb") as f:
        hasher = hashlib.sha256()
        while chunk := f.read(65536):
            hasher.update(chunk)
        sha256 = hasher.hexdigest()

    file_entropy = calculate_entropy(header)

    result: Dict[str, Any] = {
        "file": str(file_path),
        "size_bytes": file_size,
        "sha256": sha256,
        "sample_entropy": round(file_entropy, 4),
        "packed_likelihood": "High (Likely packed or encrypted)" if file_entropy > 7.2 else "Low / Normal",
        "format": "Unknown binary",
        "architecture": "Unknown",
        "subsystem": "Unknown",
        "details": {}
    }

    # 1. PE Check (Windows)
    if header.startswith(b"MZ"):
        result["format"] = "Windows PE (Portable Executable)"
        if len(header) >= 0x40:
            e_lfanew = struct.unpack_from("<I", header, 0x3C)[0]
            if e_lfanew + 4 <= len(header) and header[e_lfanew:e_lfanew+4] == b"PE\x00\x00":
                machine = struct.unpack_from("<H", header, e_lfanew + 4)[0]
                machine_map = {
                    0x014c: "i386 (32-bit x86)",
                    0x8664: "AMD64 (64-bit x86_64)",
                    0xaa64: "ARM64 (Little Endian)",
                    0x01c0: "ARM (Little Endian)"
                }
                result["architecture"] = machine_map.get(machine, f"Unknown machine (0x{machine:04x})")
                opt_magic = struct.unpack_from("<H", header, e_lfanew + 24)[0]
                if opt_magic == 0x10b:
                    result["details"]["pe_type"] = "PE32 (32-bit)"
                elif opt_magic == 0x20b:
                    result["details"]["pe_type"] = "PE32+ (64-bit)"

    # 2. ELF Check (Linux)
    elif header.startswith(b"\x7fELF"):
        result["format"] = "Linux ELF"
        ei_class = header[4] if len(header) > 4 else 0
        ei_data = header[5] if len(header) > 5 else 0
        endian = "<" if ei_data == 1 else ">"
        result["details"]["class"] = "64-bit" if ei_class == 2 else "32-bit"
        if len(header) >= 20:
            e_machine = struct.unpack_from(endian + "H", header, 18)[0]
            elf_machines = {
                0x03: "x86",
                0x3E: "x86_64",
                0x28: "ARM",
                0xB7: "AArch64 (ARM64)",
                0xF3: "RISC-V"
            }
            result["architecture"] = elf_machines.get(e_machine, f"Unknown ELF machine (0x{e_machine:02x})")

    # 3. Mach-O (macOS)
    elif header.startswith((b"\xfe\xed\xfa\xce", b"\xce\xfa\xed\xfe", b"\xfe\xed\xfa\xcf", b"\xcf\xfa\xed\xfe")):
        result["format"] = "macOS Mach-O"
        is_64 = header.startswith((b"\xfe\xed\xfa\xcf", b"\xcf\xfa\xed\xfe"))
        result["details"]["class"] = "64-bit" if is_64 else "32-bit"

    # 4. Chromium ASAR
    elif len(header) >= 16 and header[0:4] == b"\x04\x00\x00\x00":
        result["format"] = "Chromium ASAR (Electron Archive)"
        result["architecture"] = "JavaScript / Electron V8"

    # 5. ZIP / APK / JAR
    elif header.startswith(b"PK\x03\x04"):
        try:
            with zipfile.ZipFile(file_path, "r") as zf:
                names = zf.namelist()
                if "AndroidManifest.xml" in names:
                    result["format"] = "Android APK"
                    result["architecture"] = "Android Dalvik / ART"
                elif "META-INF/MANIFEST.MF" in names:
                    result["format"] = "Java JAR Archive"
                    result["architecture"] = "JVM Bytecode"
                else:
                    result["format"] = "ZIP Archive"
        except Exception:
            result["format"] = "ZIP Archive (Corrupt or Encrypted)"

    # 6. SQLite DB
    elif header.startswith(b"SQLite format 3\x00"):
        result["format"] = "SQLite 3 Database"

    # 7. PCAP
    elif header.startswith((b"\xd4\xc3\xb2\xa1", b"\xa1\xb2\xc3\xd4")):
        result["format"] = "Wireshark PCAP Packet Capture"

    # 8. WebAssembly
    elif header.startswith(b"\x00asm"):
        result["format"] = "WebAssembly Binary (Wasm)"
        result["architecture"] = "Wasm VM"

    return result


def parse_pe(file_path: Path) -> Dict[str, Any]:
    """Parse PE headers, sections, section entropy, and basic imports."""
    with open(file_path, "rb") as f:
        data = f.read()

    if not data.startswith(b"MZ"):
        return {"error": "Not a valid PE file (missing MZ header)"}

    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    if e_lfanew + 24 > len(data) or data[e_lfanew:e_lfanew+4] != b"PE\x00\x00":
        return {"error": "Invalid PE signature"}

    # File Header
    coff_offset = e_lfanew + 4
    machine, num_sections, timestamp, _, _, opt_size, characteristics = struct.unpack_from(
        "<HHIIIHH", data, coff_offset
    )

    opt_offset = coff_offset + 20
    opt_magic = struct.unpack_from("<H", data, opt_offset)[0]
    is_64 = (opt_magic == 0x20b)

    entry_point = struct.unpack_from("<I", data, opt_offset + 16)[0]
    image_base = struct.unpack_from("<Q" if is_64 else "<I", data, opt_offset + 24)[0]
    section_align = struct.unpack_from("<I", data, opt_offset + (32 if is_64 else 32))[0]
    file_align = struct.unpack_from("<I", data, opt_offset + (36 if is_64 else 36))[0]
    subsystem = struct.unpack_from("<H", data, opt_offset + (68 if is_64 else 68))[0]

    subsystems = {
        1: "Native",
        2: "Windows GUI",
        3: "Windows CUI (Console)",
        7: "POSIX CUI",
        9: "Windows CE GUI",
        10: "EFI Application"
    }

    # Section Headers
    sections_offset = opt_offset + opt_size
    sections = []
    for i in range(num_sections):
        sec_hdr = sections_offset + (i * 40)
        if sec_hdr + 40 > len(data):
            break
        name_raw = data[sec_hdr:sec_hdr+8]
        name = name_raw.split(b"\x00")[0].decode("latin-1", errors="replace")
        vsize, vaddr, raw_size, raw_ptr, _, _, _, _, chars = struct.unpack_from(
            "<IIIIIIHHI", data, sec_hdr + 8
        )
        sec_bytes = data[raw_ptr:raw_ptr+raw_size] if raw_ptr + raw_size <= len(data) else b""
        sec_entropy = calculate_entropy(sec_bytes)
        sections.append({
            "name": name,
            "virtual_address": f"0x{vaddr:08x}",
            "virtual_size": vsize,
            "raw_size": raw_size,
            "raw_pointer": f"0x{raw_ptr:08x}",
            "entropy": round(sec_entropy, 4),
            "packed_suspect": sec_entropy > 7.3
        })

    return {
        "file": str(file_path),
        "machine": f"0x{machine:04x} ({'64-bit' if is_64 else '32-bit'})",
        "number_of_sections": num_sections,
        "entry_point_rva": f"0x{entry_point:08x}",
        "entry_point_va": f"0x{image_base + entry_point:012x}",
        "image_base": f"0x{image_base:012x}",
        "subsystem": subsystems.get(subsystem, f"Unknown ({subsystem})"),
        "sections": sections
    }


def extract_strings(file_path: Path, min_len: int = 5, limit: int = 200, filter_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Extract ASCII and UTF-16 strings with optional regex filtering."""
    with open(file_path, "rb") as f:
        data = f.read()

    patterns = {
        "url": re.compile(r"https?://[a-zA-Z0-9_\-\.\:\/\?\#\=\&\%\+]+", re.IGNORECASE),
        "ip": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
        "path": re.compile(r"(?:[a-zA-Z]:\\[a-zA-Z0-9_\-\\]+|/(?:usr|etc|bin|lib|home|var)/[a-zA-Z0-9_\-/]+)"),
        "api": re.compile(r"(?:api[_-]|key[_-]|token|auth|bearer|secret)", re.IGNORECASE)
    }

    # Find ASCII strings
    ascii_re = re.compile(rb"[\x20-\x7E]{" + str(min_len).encode() + rb",}")
    matches = []

    for m in ascii_re.finditer(data):
        s = m.group().decode("latin-1")
        offset = m.start()
        matches.append({"offset": f"0x{offset:08x}", "type": "ASCII", "string": s})

    # Find UTF-16LE strings
    utf16_re = re.compile(rb"(?:[\x20-\x7E]\x00){" + str(min_len).encode() + rb",}")
    for m in utf16_re.finditer(data):
        try:
            s = m.group().decode("utf-16le")
            offset = m.start()
            matches.append({"offset": f"0x{offset:08x}", "type": "UTF-16LE", "string": s})
        except Exception:
            pass

    # Apply filters
    if filter_types:
        filtered = []
        for item in matches:
            text = item["string"]
            for ft in filter_types:
                ft = ft.strip().lower()
                if ft in patterns and patterns[ft].search(text):
                    filtered.append(item)
                    break
        matches = filtered

    return matches[:limit]


def unpack_asar(asar_path: Path, output_dir: Path) -> Dict[str, Any]:
    """Pure-Python unpacker for Chromium ASAR (Electron package) files."""
    if not asar_path.exists():
        return {"error": f"ASAR file not found: {asar_path}"}

    with open(asar_path, "rb") as f:
        data = f.read()

    if len(data) < 16 or data[0:4] != b"\x04\x00\x00\x00":
        return {"error": "Not a valid Chromium ASAR file"}

    header_size = struct.unpack_from("<I", data, 4)[0]
    header_payload_size = struct.unpack_from("<I", data, 8)[0]
    json_len = struct.unpack_from("<I", data, 12)[0]

    json_raw = data[16:16+json_len].decode("utf-8", errors="replace")
    header_json = json.loads(json_raw)

    base_offset = 16 + header_payload_size
    extracted_files = []

    def extract_node(node: Dict[str, Any], current_path: Path):
        if "files" in node:
            current_path.mkdir(parents=True, exist_ok=True)
            for fname, child in node["files"].items():
                extract_node(child, current_path / fname)
        elif "size" in node and "offset" in node:
            offset = int(node["offset"])
            size = int(node["size"])
            file_data = data[base_offset + offset : base_offset + offset + size]
            current_path.parent.mkdir(parents=True, exist_ok=True)
            with open(current_path, "wb") as out_f:
                out_f.write(file_data)
            extracted_files.append({"path": str(current_path.relative_to(output_dir)), "size": size})

    output_dir.mkdir(parents=True, exist_ok=True)
    extract_node(header_json, output_dir)

    return {
        "status": "success",
        "output_dir": str(output_dir),
        "total_files": len(extracted_files),
        "files": extracted_files[:100]
    }


def parse_apk(apk_path: Path) -> Dict[str, Any]:
    """Inspect Android APK zip contents, manifest, DEX list, and native libs."""
    if not apk_path.exists():
        return {"error": f"APK not found: {apk_path}"}

    with zipfile.ZipFile(apk_path, "r") as zf:
        infolist = zf.infolist()
        dex_files = [info.filename for info in infolist if info.filename.endswith(".dex")]
        native_libs = [info.filename for info in infolist if info.filename.startswith("lib/") and info.filename.endswith(".so")]
        has_manifest = "AndroidManifest.xml" in [info.filename for info in infolist]

        manifest_strings = []
        if has_manifest:
            raw_manifest = zf.read("AndroidManifest.xml")
            # Extract readable strings from binary XML
            str_re = re.compile(rb"[\x20-\x7E]{4,}")
            manifest_strings = [m.group().decode("latin-1") for m in str_re.finditer(raw_manifest)]

    return {
        "apk": str(apk_path),
        "dex_files": dex_files,
        "dex_count": len(dex_files),
        "native_libraries": native_libs,
        "native_library_count": len(native_libs),
        "manifest_extracted_strings_sample": manifest_strings[:30]
    }


def run_diff_test(original_bin: str, rebuild_bin: str, vectors_path: Path, verbose: bool = False) -> Dict[str, Any]:
    """Execute differential test comparing outputs across original and rebuilt binaries."""
    if not vectors_path.exists():
        return {"error": f"Vectors file not found: {vectors_path}"}

    with open(vectors_path, "r", encoding="utf-8") as f:
        vectors = json.load(f)

    results = []
    passed = 0
    total = len(vectors)

    for vec in vectors:
        vec_id = vec.get("id", "Unknown")
        args = vec.get("args", [])
        stdin_data = vec.get("stdin", "")

        # Run original
        try:
            res_orig = subprocess.run([original_bin] + args, input=stdin_data, text=True, capture_output=True, timeout=10)
            orig_code = res_orig.returncode
            orig_stdout = res_orig.stdout
            orig_stderr = res_orig.stderr
        except Exception as e:
            results.append({"id": vec_id, "status": "ERROR_ORIGINAL", "error": str(e)})
            continue

        # Run rebuild
        try:
            res_reb = subprocess.run([rebuild_bin] + args, input=stdin_data, text=True, capture_output=True, timeout=10)
            reb_code = res_reb.returncode
            reb_stdout = res_reb.stdout
            reb_stderr = res_reb.stderr
        except Exception as e:
            results.append({"id": vec_id, "status": "ERROR_REBUILD", "error": str(e)})
            continue

        match_code = (orig_code == reb_code)
        match_stdout = (orig_stdout == reb_stdout)
        match_stderr = (orig_stderr == reb_stderr)

        is_match = match_code and match_stdout and match_stderr
        if is_match:
            passed += 1

        record = {
            "id": vec_id,
            "status": "PASS" if is_match else "FAIL",
            "match_exit_code": match_code,
            "match_stdout": match_stdout,
            "match_stderr": match_stderr
        }
        if not is_match or verbose:
            record["original"] = {"exit": orig_code, "stdout": orig_stdout[:200], "stderr": orig_stderr[:200]}
            record["rebuild"] = {"exit": reb_code, "stdout": reb_stdout[:200], "stderr": reb_stderr[:200]}
        results.append(record)

    return {
        "total_vectors": total,
        "passed": passed,
        "failed": total - passed,
        "parity_percentage": round((passed / total * 100), 2) if total > 0 else 0.0,
        "results": results
    }


def main():
    parser = argparse.ArgumentParser(description="REA Helper: Zero-dependency companion for reverse engineering in Antigravity.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. identify
    p_id = subparsers.add_parser("identify", help="Identify file format, architecture, and entropy.")
    p_id.add_argument("file", type=Path, help="Target file path")

    # 2. pe-info
    p_pe = subparsers.add_parser("pe-info", help="Parse PE headers, sections, and entropy.")
    p_pe.add_argument("file", type=Path, help="Target Windows PE executable")

    # 3. strings
    p_str = subparsers.add_parser("strings", help="Extract ASCII and UTF-16LE strings with pattern filters.")
    p_str.add_argument("file", type=Path, help="Target file")
    p_str.add_argument("--min-len", type=int, default=5, help="Minimum string length (default: 5)")
    p_str.add_argument("--limit", type=int, default=150, help="Max strings to return (default: 150)")
    p_str.add_argument("--filter", type=str, default="", help="Comma-separated filters: url, ip, path, api")

    # 4. asar-unpack
    p_asar = subparsers.add_parser("asar-unpack", help="Unpack Chromium ASAR archive.")
    p_asar.add_argument("asar", type=Path, help="Path to app.asar")
    p_asar.add_argument("output", type=Path, help="Output destination folder")

    # 5. apk-info
    p_apk = subparsers.add_parser("apk-info", help="Inspect Android APK DEX files, manifest strings, and native libs.")
    p_apk.add_argument("apk", type=Path, help="Target Android APK file")

    # 6. diff-test
    p_diff = subparsers.add_parser("diff-test", help="Run differential behavior test between original and rebuild.")
    p_diff.add_argument("--original", required=True, help="Path to original binary")
    p_diff.add_argument("--rebuild", required=True, help="Path to rebuilt binary")
    p_diff.add_argument("--vectors", type=Path, required=True, help="Path to test_vectors.json")
    p_diff.add_argument("--verbose", action="store_true", help="Include full output for all test cases")

    args = parser.parse_args()

    if args.command == "identify":
        print(json.dumps(identify_format(args.file), indent=2))
    elif args.command == "pe-info":
        print(json.dumps(parse_pe(args.file), indent=2))
    elif args.command == "strings":
        filters = [f.strip() for f in args.filter.split(",") if f.strip()] if args.filter else None
        print(json.dumps(extract_strings(args.file, min_len=args.min_len, limit=args.limit, filter_types=filters), indent=2))
    elif args.command == "asar-unpack":
        print(json.dumps(unpack_asar(args.asar, args.output), indent=2))
    elif args.command == "apk-info":
        print(json.dumps(parse_apk(args.apk), indent=2))
    elif args.command == "diff-test":
        print(json.dumps(run_diff_test(args.original, args.rebuild, args.vectors, args.verbose), indent=2))


if __name__ == "__main__":
    main()

