# Using REA with Google Antigravity & Gemini AI

**English** · [简体中文](antigravity-guide.zh-CN.md) · [Back to the list](../README.md)

This guide documents how to use **Reverse Engineer Anything (REA)** and the **AI Rebuild Engine** inside **Google Antigravity**, powered by **Gemini AI** (such as Gemini 3.8 Flash and Gemini Pro).

---

## 1. Why Antigravity & Gemini for Reverse Engineering?

Gemini models feature massive context windows, deep code reasoning, and multi-turn architectural synthesis. Antigravity combines this with:
- **Progressive Skill Loading**: Skills like `reverse-engineer-anything` and `ai-rebuild-engine` are loaded into context only when needed.
- **Dedicated Subagents**: Seamless delegation to specialized subagents like `reverse-engineer-expert` for long-running, deep-dive decompilation tasks.
- **Interactive Workflows & Slash Commands**: Fast iteration with `/plan`, `/boost`, and background tasks.
- **Zero-Dependency Fallbacks**: Local companion tools (`scripts/rea_helper.py`) that run instantly on Windows, Linux, and macOS without package conflicts.

---

## 2. Included Customizations in this Repository

This repository includes a turnkey Antigravity workspace and global plugin configuration:

```
.agents/
├── plugin.json                                # Antigravity plugin manifest
├── mcp_config.json                            # REA MCP server definition
├── agents/
│   └── reverse-engineer-expert.md             # Specialist subagent definition
├── rules/
│   ├── AGENTS.md                              # Rules for AI coding agents
│   └── GEMINI.md                              # Mandatory evidence-first rules for Gemini
└── skills/
    ├── reverse-engineer-anything/             # Main REA analysis skill
    │   ├── SKILL.md
    │   └── references/
    │       ├── target-routing.md
    │       ├── evidence-guide.md
    │       └── tools-and-fallbacks.md
    └── ai-rebuild-engine/                     # Clean-room rebuild skill
        ├── SKILL.md
        └── references/
            ├── differential-testing.md
            └── clean-room-protocol.md
```

---

## 3. Quick Start & Setup

### Option A: Automatic Setup (Windows PowerShell)
Run the bundled setup script:
```powershell
.\scripts\setup-antigravity.ps1
```
This script checks Python, Node.js, validates `scripts/rea_helper.py`, and registers the plugin globally into `~/.gemini/config/plugins/reverse-engineer-anything`.

### Option B: Automatic Setup (Linux / macOS)
```bash
bash scripts/setup-antigravity.sh
```

---

## 4. End-to-End Walkthroughs

### Walkthrough 1: Reversing a Windows PE Binary
1. **Triage the file**:
   Ask Antigravity:
   > "Inspect `sample.exe`, compute its entropy and sections, and tell me if it is packed."
   Antigravity will run:
   ```powershell
   python scripts/rea_helper.py identify sample.exe
   python scripts/rea_helper.py pe-info sample.exe
   ```
2. **Decompile & Extract Logic**:
   Antigravity decompiles key entry points or uses string analysis:
   ```powershell
   python scripts/rea_helper.py strings sample.exe --min-len 6 --filter url,api
   ```
3. **Evidence Citations**:
   The report produced by Gemini will cite file offsets (`[EVD-01]`, `0x1400019C0`) and verified disassembly snippets.

---

### Walkthrough 2: Deconstructing an Electron Desktop Application
1. **Unpack the ASAR bundle**:
   > "Extract `resources/app.asar` and map the IPC routes."
   Antigravity executes:
   ```powershell
   python scripts/rea_helper.py asar-unpack resources/app.asar unpacked_app/
   ```
2. **Trace the IPC Bridge**:
   Gemini reads `unpacked_app/package.json`, inspects `preload.js` and `main.js`, and maps all `ipcRenderer.send` and `ipcMain.handle` events into a Mermaid sequence diagram.

---

### Walkthrough 3: Clean-Room Differential Rebuild
1. **Generate Test Vectors**:
   Antigravity captures inputs and outputs from the target module into `tests/vectors.json`.
2. **Implement in Modern Language**:
   Gemini writes a clean implementation in Rust, Go, TypeScript, or Python.
3. **Run Differential Assertions**:
   ```powershell
   python scripts/rea_helper.py diff-test --original original.exe --rebuild target/release/rebuild.exe --vectors tests/vectors.json
   ```
   Ensures 100% behavioral parity before finalizing.
