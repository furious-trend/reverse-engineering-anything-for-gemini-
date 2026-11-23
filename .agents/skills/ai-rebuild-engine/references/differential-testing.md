# Differential Testing Guide

Differential testing verifies that a reconstructed module matches the behavior of the original binary across hundreds or thousands of test cases.

## The Differential Testing Loop

```
                     ┌──────────────────┐
                     │ Test Vector Pool │
                     └────────┬─────────┘
                              │ Input vector: x_i
              ┌───────────────┴───────────────┐
              ▼                               ▼
     ┌─────────────────┐             ┌─────────────────┐
     │ Original Binary │             │ Rebuilt Target  │
     └────────┬────────┘             └────────┬────────┘
              │ Output y_orig                 │ Output y_rebuild
              └───────────────┬───────────────┘
                              ▼
                     ┌──────────────────┐
                     │  Diff Assertion  │
                     │ y_orig == y_reb? │
                     └──────────────────┘
```

## Test Vector Schema (`test_vectors.json`)
```json
[
  {
    "id": "TC-001",
    "name": "Normal input boundary",
    "args": ["--mode", "encrypt", "--input", "hello world", "--key", "secret123"],
    "stdin": "",
    "expected_exit_code": 0,
    "expected_stdout_contains": "CIPHER:"
  },
  {
    "id": "TC-002",
    "name": "Invalid key length",
    "args": ["--mode", "encrypt", "--input", "test", "--key", "short"],
    "stdin": "",
    "expected_exit_code": 1,
    "expected_stderr_contains": "Error: key must be at least 8 bytes"
  }
]
```

## Running Differential Tests with `rea_helper.py`
```powershell
python scripts/rea_helper.py diff-test \
  --original "original_binary.exe" \
  --rebuild "rebuild_binary.exe" \
  --vectors "tests/vectors.json" \
  --verbose
```

