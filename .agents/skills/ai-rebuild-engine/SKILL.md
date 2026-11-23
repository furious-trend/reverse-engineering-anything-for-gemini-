---
name: ai-rebuild-engine
description: Reconstruct and rebuild closed-source software, features, or protocols using clean-room specifications and behavior-checked differential testing. Use when turning reverse-engineering findings into clean, modern implementations (Rust, Python, TypeScript, Go, C++) verified step-by-step against original behavior.
---

# AI Rebuild Engine: Behavior-Checked Clean-Room Reconstruction

The goal of reverse engineering in Antigravity is not merely passive inspection, but active understanding, interoperability, and clean reconstruction. Inspired by the verified showcases in the REA ecosystem (such as DX-Ball byte-matching, `rust-anything`, `rec-rs`, and `feature-heist`), this skill guides the agent in writing modern replacements that match original behavior with zero copyright contamination.

---

## 1. The 4-Stage Reconstruction Pipeline

```
  ┌─────────────────────────┐
  │ 1. Vector Recording     │  Capture real inputs & outputs from original binary
  └───────────┬─────────────┘
              ▼
  ┌─────────────────────────┐
  │ 2. Clean-Room Spec      │  Write algorithmic invariants & behavioral contract
  └───────────┬─────────────┘
              ▼
  ┌─────────────────────────┐
  │ 3. Clean Implementation │  Implement in modern stack (Rust/Go/TS/Python/C++)
  └───────────┬─────────────┘
              ▼
  ┌─────────────────────────┐
  │ 4. Differential Testing │  Replay vectors across original & rebuild; compare diff
  └─────────────────────────┘
```

### Stage 1: Behavior & Vector Recording
Before writing any replacement code, record how the original program behaves:
- Identify key functional boundaries: Command-line inputs, config files, network requests, binary function parameters.
- Generate or capture a dataset of input-output pairs (test vectors):
  - Normal inputs (representative data)
  - Boundary conditions (0, -1, MAX_INT, empty strings, null bytes)
  - Malformed or invalid inputs (to check error handling and return codes)

### Stage 2: Clean-Room Specification
Create a formal functional specification:
- **Interface Contract**: Function signatures, parameters, types, return values.
- **Invariants**: Mathematical formulas, state machines, ordering constraints.
- **Side Effects**: File system changes, sockets opened, environmental reads.
- **Legal Clean-Room Boundary**: Do NOT copy proprietary comments, proprietary strings, asset files, or obfuscated variable names. Re-express logic cleanly using standard language idioms.

### Stage 3: Modern Implementation
Implement the feature in your selected target language (e.g. Rust, TypeScript, Go, Python):
- Adhere strictly to the clean-room specification.
- Use modern idioms, strict type checking, and robust memory safety.
- Expose identical interfaces or CLI arguments to enable seamless differential validation.

### Stage 4: Differential Testing Loop
Execute the differential test suite:
- Run the test inputs through both the original target and the new implementation.
- Compare outputs byte-for-byte or semantic-field-for-semantic-field:
  ```powershell
  python scripts/rea_helper.py diff-test --original "orig.exe" --rebuild "target/release/rebuild.exe" --vectors "tests/vectors.json"
  ```
- If discrepancies occur:
  1. Isolate the failing test vector.
  2. Inspect the mathematical or logical divergence.
  3. Refactor the implementation until 100% vector parity is achieved.

---

## 2. Best Practices for High Parity

1. **Byte-Level Matching vs. Semantic Parity**:
   - For mathematical helpers, hashing, encryption, compression, and encoding: Aim for 100% byte-exact parity.
   - For UI applications, screen recorders, and web services: Aim for functional and protocol parity (clean architecture, identical wire formats, responsive UX).
2. **Never Drift**:
   - As observed in `rust-anything`, agents drift when they write large blocks of code without feedback. Always write code incrementally: one function, one module, or one endpoint at a time, backed by immediate test execution.
3. **Asset Handling**:
   - Proprietary assets (fonts, icons, sound files, 3D models) should remain separate from the code. Instruct users to supply their own assets or load assets dynamically from their licensed installation.

