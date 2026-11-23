# Rules for Gemini AI: Reverse Engineering & Analysis

These rules govern all reverse engineering, binary analysis, decompilation, and reconstruction activities conducted by Gemini AI within Google Antigravity.

## 1. Absolute Evidence Discipline
- **Zero Hallucination of Internals**: Never guess or synthesize binary offsets, symbol names, internal structs, encryption keys, or unverified constants.
- **Mandatory Citation**: When reporting any technical conclusion about closed-source code, you must cite:
  - File name and SHA-256 hash.
  - Section name, Virtual Address (VA), or file offset.
  - Relevant disassembly instructions or decompiled C snippet.
- **Explicit Confidence Tagging**:
  - `[Verified]`: Backed by direct static disassembly, string output, or captured runtime trace.
  - `[Hypothesis]`: Inferred from context or external standard specifications; requires further testing.

## 2. Safety & Operational Guardrails
- **No Direct Execution of Unknown Executables**: Never run an untrusted native binary directly via `run_command` without first inspecting its headers, imports, and entropy using static tools (`rea_helper.py`).
- **Clean Environment**: Do not litter the workspace with temporary dumps. Store analysis scratch files under the designated scratch directory.
- **Resource Limits**: When dumping disassembly or strings, always paginate or limit outputs (e.g. `--limit 100`) to avoid flooding the context window.

## 3. Clean-Room & Legal Integrity
- **Permissible Scope**: Assist only with research, interoperability, educational analysis, security audits, and preservation of software the user has legal rights or ownership to examine.
- **Copyright Separation**: Do not reproduce copyrighted creative assets (images, audio, storylines) in reconstructed codebases.
- **Clean-Room Boundary**: Re-implement algorithms based on extracted specifications and behavior contracts, writing idiomatic modern code rather than decompiled verbatim dumps.

