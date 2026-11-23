# Clean-Room Engineering Protocol

Clean-room design (also known as the "Chinese wall technique") ensures that software can be reverse engineered and rebuilt for interoperability or preservation without infringing copyrights.

## Separation of Roles

In a pure clean-room process, two distinct roles are maintained:

1. **The Reverse Engineer / Specifier (Dirty Room)**:
   - Inspects the original binary, deconstructs its protocol or algorithm.
   - Extracts ONLY technical specifications, interfaces, state machines, math formulas, and behavioral invariants.
   - Strictly DOES NOT write the final production code.
   - Produces the **Functional Specification Document**.

2. **The Software Developer / Implementer (Clean Room)**:
   - Receives ONLY the Functional Specification Document.
   - Has never examined the original disassembly or source code.
   - Writes the new implementation in a modern programming language (e.g. Rust, Go, TypeScript) from scratch.

## Guidelines for Antigravity Agents

When acting as a single AI agent executing a rebuild:
- **Phase Separation**: Complete the specification phase first before entering the implementation phase.
- **No Verbatim Copying**:
  - Never copy decompiled C variable names or structure field names that look copyrighted or proprietary.
  - Never copy proprietary strings, UI copy, logos, or creative assets.
- **Idiomatic Modern Code**: Write code that follows modern language idioms rather than mimicking compiler-generated disassembly patterns.

