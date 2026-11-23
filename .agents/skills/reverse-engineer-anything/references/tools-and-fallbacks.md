# Tools and Fallback Matrix

This guide details the reverse engineering tools integrated with Antigravity, including headless automation and zero-dependency fallbacks.

## 1. Zero-Dependency Antigravity Companion (`rea_helper.py`)
Ships directly in `scripts/rea_helper.py`. Requires only Python 3.8+ (standard library):
- `identify`: Magic bytes, format detection, architecture, hashes.
- `pe-info`: PE32/PE32+ headers, DataDirectories, sections, section entropy, imports, exports.
- `elf-info`: ELF32/ELF64 headers, program headers, section headers, dynamic symbols.
- `strings`: ASCII and UTF-16LE string search with regex pattern filters.
- `asar-unpack`: Unpacks Electron Chromium ASAR archives.
- `apk-info`: Android APK zip parser, binary XML de-obfuscation, manifest extractor.
- `diff-test`: Automated differential tester comparing output across binaries.

## 2. Headless Ghidra Automation
When Ghidra is installed on the machine, you can run headless analysis directly:
```powershell
# Windows
& "$env:GHIDRA_HOME\support\analyzeHeadless.bat" "C:\temp\ghidra_projects" "ProjectName" -import "path\to\target.exe" -postScript DecompileFunction.java "target_function_name"
```

## 3. JADX for Android
When JADX is available:
```powershell
jadx --deobf -d "output_src" "path\to\target.apk"
```

## 4. Node REA MCP Server
To launch REA via MCP in Antigravity:
```json
{
  "mcpServers": {
    "rea": {
      "command": "npx.cmd",
      "args": ["-y", "rea-agents@latest", "mcp"]
    }
  }
}
```
If Node engine version mismatches occur, use the `rea_helper.py` companion or run with updated Node LTS.

