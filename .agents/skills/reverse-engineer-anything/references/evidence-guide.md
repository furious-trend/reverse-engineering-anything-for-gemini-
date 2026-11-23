# Evidence Guide & Citation Standards

Evidence discipline is the hallmark of professional reverse engineering with Gemini AI. This guide defines how to record, reference, and verify evidence.

## Evidence ID Schema

Every key technical claim must cite an `[EVD-xx]` identifier in your response or analysis artifact.

```markdown
### Evidence Item: EVD-01
- **File**: `client_core.dll`
- **SHA-256**: `b4578b7b25c38d2179a667b9319e8cf19c3c1e285d88686d11f5abcb813f619b`
- **Offset / VA**: `0x180014280` (`.text` section)
- **Symbol**: `VerifySignature`
- **Raw Snippet**:
  ```x86asm
  mov     rax, [rcx+20h]
  cmp     dword ptr [rax], 0DEADBEEFh
  jne     loc_1800142C0
  ```
- **Finding**: Verifies signature magic `0xDEADBEEF` at offset `+0x20` of context structure.
```

## Evidence Verification Checklist

Before publishing findings:
1. Is the Virtual Address (VA) or file offset accurate and reproducible?
2. Is the disassembly snippet copy-pasted verbatim from decompiler output, rather than summarized or approximated?
3. Are string references verified against raw binary strings?
4. Is cryptographic key material identified accurately (e.g. distinguishing AES-GCM tag verification from HMAC-SHA256)?
