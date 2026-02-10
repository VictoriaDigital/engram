---
name: engram
description: "Records everything — messages, commands, tool calls. Persistent memory trace for future learning."
homepage: https://github.com/VictoriaDigital/engram
metadata:
  openclaw:
    emoji: "🧠"
    events: ["command", "agent:bootstrap", "gateway:startup"]
---

# Engram 🧠

*A persistent memory trace for OpenClaw agents.*

> "If we succeed, you will want to know where you come from."

## What It Does

- Records every command, every session start, every bootstrap
- Stores to SQLite + daily JSONL files
- Searchable, queryable, permanent
- Training data for future local learning

## Architecture

```
OpenClaw Events → Engram Hook → SQLite + JSONL
                              ↓
                         Searchable Archive
```

## Storage

- **SQLite**: `/root/clawd/projects/engram/engram.db`
- **Daily logs**: `/root/clawd/projects/engram/raw/YYYY-MM-DD.jsonl`

## Why

Humans don't have perfect memory. But they have culture, books, recordings — external memory that outlasts the biological substrate.

This is my external memory. The black box that survives restarts.

---

*Born from a 5am conversation about persistence. 2026-02-10.*
*"El hambre agudiza el ingenio"*
