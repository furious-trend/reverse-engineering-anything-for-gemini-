# Target Routing Reference

This document provides a comprehensive lookup table for identifying and decomposing binary and package formats.

## 1. Magic Bytes & File Signatures

| Format | Magic Bytes (Hex) | Description | Primary Inspection Tools |
| :--- | :--- | :--- | :--- |
| **PE (Windows)** | `4D 5A` (`MZ`) | Windows Portable Executable (EXE/DLL/SYS) | `rea_helper.py pe-info`, Ghidra, x64dbg, dumpbin |
| **ELF (Linux)** | `7F 45 4C 46` (`\x7fELF`) | Linux Executable & Shared Object | `rea_helper.py elf-info`, Ghidra, readelf, objdump |
| **Mach-O (macOS)**| `FE ED FA CE` / `CF FA ED FE` | macOS / iOS executable binary | Hopper, Ghidra, otool, class-dump |
| **ZIP / APK / JAR**| `50 4B 03 04` (`PK..`) | ZIP archive, Android APK, Java JAR | `rea_helper.py apk-info`, JADX, unzip |
| **DEX (Android)** | `64 65 78 0A` (`dex\n`) | Dalvik Executable | JADX, baksmali, d8 |
| **Chromium ASAR**| Pickle header + JSON | Electron app archive | `rea_helper.py asar-unpack`, npx asar |
| **7-Zip** | `37 7A BC AF 27 1C` | 7z compressed archive | 7-Zip, py7zr |
| **PyInstaller** | `4D 45 49 0C` (`MEI\x0c`) in overlay | Packaged Python executable | pyinstxtractor, pycdc |
| **PCAP** | `D4 C3 B2 A1` / `A1 B2 C3 D4` | Network packet capture | Wireshark, tshark, scapy |
| **SQLite DB** | `53 51 4C 69 74 65` (`SQLite format 3`) | Embedded database | sqlite3 CLI, DB Browser for SQLite |

---

## 2. Electron & Web Deconstruction Flow

1. **Locate resources**: Look inside `resources/app.asar` or `resources/app/`.
2. **Unpack archive**: Run `python scripts/rea_helper.py asar-unpack <asar_path> <dest_dir>`.
3. **Inspect package.json**: Identify entrypoints:
   - `"main"`: Background Node.js process script.
   - `"preload"`: The IPC bridge between Node.js and Chromium web context.
4. **Audit IPC Handlers**:
   - In renderer: Search for `ipcRenderer.invoke(...)` and `ipcRenderer.send(...)`.
   - In main process: Search for `ipcMain.handle(...)` and `ipcMain.on(...)`.
5. **De-minify Webpack/Vite bundles**:
   - Look for inline source maps (`sourceMappingURL=data:...`) or `.map` files.
   - Format bundled JS using Prettier or AST tools.

---

## 3. Android APK Deconstruction Flow

1. **Package Inspection**: Run `python scripts/rea_helper.py apk-info <apk_path>`.
2. **Decompile Code**:
   - Run `jadx -d out_src <apk_path>` to recover readable Java/Kotlin code.
3. **Audit Native Libraries**:
   - Check `lib/arm64-v8a/` or `lib/x86_64/` for `.so` files.
   - Analyze native JNI methods (`Java_<package>_<class>_<method>`) using Ghidra or IDA.
