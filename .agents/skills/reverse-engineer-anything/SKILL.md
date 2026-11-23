---
name: reverse-engineer-anything
description: Reverse engineer native binaries (PE/ELF/Mach-O), Electron/JavaScript applications, Android APKs, .NET assemblies, firmware, network protocols, and web apps with REA evidence discipline. Use when inspecting closed-source targets, recovering algorithms, comparing versions, or building verified reconstructions with Gemini AI.
---

# Reverse Engineer Anything (REA) for Antigravity & Gemini AI

Use this skill when an investigation or user request requires inspecting a compiled binary, packed archive, closed-source runtime behavior, or decompiled code. For ordinary source code repository exploration, use standard Antigravity file reading and code search tools instead of REA workflows.

---

## 1. Core Operating Philosophy: Evidence-Driven Analysis

Gemini AI models are exceptionally capable at reading decompiled C, disassembling assembly code, and identifying complex data structures. To eliminate hallucination and maintain absolute engineering fidelity:

1. **Every claim requires an Evidence Citation**:
   - Never assert that an algorithm works in a certain way without pointing to the exact instruction, decompiled line, extracted string, or captured packet.
   - Evidence Citation Format:
     ```markdown
     > **Evidence `[EVD-01]`**:
     > - **Target**: `target_app.exe` (SHA256: `a3f89...`)
     > - **Location**: Function `sub_1400021A0` (VA: `0x1400021A0`, File Offset: `0x15A0`)
     > - **Disassembly / Code**:
     >   ```c
     >   if (param_1 == 0x7a) {
     >       return decrypt_payload(param_2, 0x10);
     >   }
     >   ```
     > - **Interpretation**: Validates license packet header magic `0x7a` before invoking decryption.
     ```
2. **Distinguish Verified vs. Inferred**:
   - Tag concrete findings as `[Verified]`.
   - Tag deductions or educated guesses as `[Hypothesis - Unverified]`.

---

## 2. Target Routing Matrix

Identify the target format first, then execute the corresponding analysis pipeline:

| Target Type | Primary Identification | Recommended Tools | Antigravity Action |
| :--- | :--- | :--- | :--- |
| **Windows Native (PE)** | `MZ` header, `.exe`, `.dll`, `.sys` | `rea_helper.py pe-info`, Ghidra, Hopper, IDA, x64dbg | Inspect PE headers, imports (e.g. `Advapi32`, `Ws2_32`), entropy of sections to detect packers, then decompile key functions. |
| **Linux Native (ELF)** | `\x7fELF`, `.so`, executables | `rea_helper.py elf-info`, Ghidra, objdump, radare2 | Check dynamic symbols, sections, strings, and decompiled control flow. |
| **macOS Native (Mach-O)** | `\xfe\xed\xfa\xce` / `\xcf\xfa\xed\xfe` | Hopper, Ghidra, `otool`, `class-dump` | Recover Objective-C / Swift classes, selectors, and Mach-O load commands. |
| **Electron / Node.js** | `app.asar`, `resources/`, JavaScript bundles | `rea_helper.py asar-unpack`, `rea` CLI | Unpack ASAR archive, locate `package.json`, trace `main` process and `preload.js`, map IPC channels (`ipcRenderer.send`, `ipcMain.handle`). |
| **Android APK** | `.apk` (ZIP container), `classes.dex` | `rea_helper.py apk-info`, JADX, Apktool | Inspect `AndroidManifest.xml`, extract permissions and exported components, decompile DEX to Java, inspect native `.so` in `lib/`. |
| **.NET / C# Assembly** | PE with CLR Runtime Header | ILSpy CLI, dnSpy, ICSharpCode.Decompiler | Decompile MSIL directly back to high-fidelity C# source code. |
| **Python Executable** | PyInstaller, Py2exe, `MEI` signature | `pyinstxtractor`, `pycdc`, `uncompyle6` | Extract CArchive, extract `.pyc` bytecode, decompile to Python script. |
| **Firmware / ROM** | Flash images, UEFI, ESP32 (`0xE9`) | Binwalk, Unblob, `rea_helper.py` | Carve filesystems (SquashFS, CramFS, JFFS2), extract kernel, inspect bootloader. |
| **Network Protocol** | `.pcap`, WebSocket, TLS traffic | Wireshark, `tshark`, `mitmproxy`, CDP | Reconstruct handshake, packet headers, serialization format (Protobuf, JSON, MsgPack). |

---

## 3. Tool Orchestration & Fallback Strategy

This skill supports dual-mode operation:

### Mode A: REA MCP Server (When connected)
If the REA MCP server (`rea-agents`) is registered and available in the Antigravity session:
- Use `open_binary` to mount native executables.
- Use `inspect_artifact` with `detail: "summary"` to inventory headers and symbols.
- Use `analyze_javascript_application` for Electron/Web targets.
- Use `inspect_managed_artifact` for .NET assemblies.
- Use `inspect_android_package` for APKs.

### Mode B: Antigravity Companion CLI (Zero-dependency fallback)
If MCP tools are not active or the environment lacks prerequisites, run the local Python companion script directly via `run_command`:
```powershell
# 1. Identify file type, architecture, and SHA256
python scripts/rea_helper.py identify "path/to/binary"

# 2. Extract ASCII and UTF-16 strings (filter by URLs, IPs, keys)
python scripts/rea_helper.py strings "path/to/binary" --min-len 6 --filter url,ip

# 3. Parse PE Header, sections, imports, and entropy
python scripts/rea_helper.py pe-info "path/to/binary.exe"

# 4. Unpack Electron ASAR without Node.js
python scripts/rea_helper.py asar-unpack "path/to/app.asar" "output_dir"

# 5. Inspect APK Manifest and DEX details
python scripts/rea_helper.py apk-info "path/to/app.apk"
```

---

## 4. Reverse Engineering Workflow

Follow this phased investigation workflow:

### Phase 1: Triage & Environmental Scoping
- Calculate SHA-256 hash.
- Measure Shannon entropy across sections:
  - Entropy > 7.2 typically indicates encryption, packing (UPX, Themida, VMProtect), or compressed payload.
- Extract strings to find build paths, libraries, debug symbols, endpoints, and error messages.

### Phase 2: Surface Architecture Mapping
- Map entry points (`main`, `WinMain`, `_start`, `JNI_OnLoad`).
- Inventory imported APIs (Networking, Cryptography, File I/O, Process Injection).
- For Electron/Web: Map all registered IPC event names and REST API routes.
- For Android: Extract exported Activities, Services, Broadcast Receivers, and Content Providers.

### Phase 3: Targeted Decompilation & Logic Isolation
- Focus exclusively on the target function or algorithm requested by the user.
- Convert raw disassembly into structured pseudocode.
- Document variable types, loops, bitwise operations, mathematical constants (e.g. S-boxes, CRC polynomials, hashing initializers).

### Phase 4: Output Synthesis & Rebuild Specification
Present findings in a structured report containing:
1. **Executive Summary**: What the software does and key architectural findings.
2. **Evidence Table**: List of `[EVD-xx]` citations.
3. **Control Flow / Sequence Diagram**: Mermaid diagram showing data or execution flow.
4. **Clean-Room Specification**: Algorithmic rules, input/output contracts, and edge cases necessary to re-implement or interoperate with the feature.
