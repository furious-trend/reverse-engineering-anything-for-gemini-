# Rules for AI Agents: Reverse Engineering Discipline

Instructions for any AI coding agent (Gemini, Claude, Codex) operating in this workspace.

1. **Evidence First**: All assertions regarding binary functionality must be accompanied by raw artifact evidence (disassembly, string match, or network trace).
2. **Target Routing**: Determine artifact packaging (PE, ELF, ASAR, APK, .NET, UEFI) before choosing analysis tools.
3. **Differential Verification**: When rebuilding code, generate a test vector suite to verify functional parity against the original target before claiming completion.
4. **Safe Static-First Triage**: Always perform static inspection (PE headers, section entropy, string filtering) prior to any runtime execution.
