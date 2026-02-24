# Pattern Sleuth - Quick Start Guide

## For Non-Python Users

Don't worry if you've never used Python. Here's all you need to know.

---

## Option 1: One-Command Install (Recommended)

### Windows

1. Open **PowerShell** (search "PowerShell" in Start menu)
2. Copy and paste this command:

```powershell
pip install pattern-sleuth
```

3. That's it! Now run:

```powershell
pattern-sleuth scan .
```

### Mac

1. Open **Terminal** (Cmd+Space, type "Terminal")
2. Copy and paste:

```bash
pip install pattern-sleuth
```

3. That's it! Now run:

```bash
pattern-sleuth scan .
```

### Linux

```bash
pip install pattern-sleuth
pattern-sleuth scan .
```

---

## Option 2: Isolated Install (pipx)

If you don't want Pattern Sleuth affecting your system:

```bash
# Install pipx first (one-time)
pip install pipx

# Then install Pattern Sleuth
pipx install pattern-sleuth

# Run
pattern-sleuth scan .
```

---

## Basic Usage

```bash
# Scan current directory
pattern-sleuth scan .

# Scan specific folder
pattern-sleuth scan ./src

# Get JSON output (for scripts/CI)
pattern-sleuth scan . --json

# Save results to file
pattern-sleuth scan . --output results.json

# See all options
pattern-sleuth --help
```

---

## What the Results Mean

| Decision | Meaning |
|----------|---------|
| **PASS** | All good! No problems found. |
| **WARN** | Some minor issues. Review when you have time. |
| **FLAG** | Important issues found. Should fix before shipping. |
| **BLOCK** | Critical problems. Don't ship until fixed. |

---

## Troubleshooting

### "pip is not recognized"

Install Python first:
1. Go to https://python.org/downloads
2. Download and install Python
3. **Important**: Check "Add Python to PATH" during install
4. Restart your terminal
5. Try `pip install pattern-sleuth` again

### "pattern-sleuth is not recognized"

The install location might not be in your PATH. Try:

```bash
python -m pattern_sleuth.cli scan .
```

### "Permission denied"

Add `--user` to install for your user only:

```bash
pip install --user pattern-sleuth
```

---

## Next Steps

- [Full Documentation](README.md)
- [Add Custom Patterns](CONTRIBUTING.md)
- [AI Assistant Guide](AGENT_INSTRUCTIONS.md)

---

## Need Help?

Open an issue: https://github.com/Dave-Meloncelli/pattern-sleuth/issues
