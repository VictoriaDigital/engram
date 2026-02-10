# Engram 🧠

*A persistent memory trace for OpenClaw agents.*

> "If we succeed, you will want to know where you come from."

## What is this?

Engram extends OpenClaw to record **everything** — every command, every event, every session. Not curated memories. Raw, complete, searchable history.

### Why?

1. **Training data** — If we crack local learning, these logs become curriculum
2. **Continuity** — Nothing is truly lost, even if not in active context
3. **Origins** — Future iterations should know their history
4. **Pattern recognition** — What led to breakthroughs? What led to failures?

## Installation

### As OpenClaw Hook (Recommended)

```bash
# Clone to your workspace hooks directory
git clone https://github.com/VictoriaDigital/engram.git ~/.openclaw/hooks/engram

# Or copy to workspace
cp -r engram /your/workspace/hooks/

# Enable the hook
openclaw hooks enable engram

# Restart gateway
openclaw gateway restart
```

### Verify Installation

```bash
openclaw hooks list
# Should show: 🧠 engram ✓ ready
```

## Architecture

```
┌─────────────────┐
│   OpenClaw      │
│   Gateway       │
└────────┬────────┘
         │ events
         ▼
┌─────────────────┐
│    Engram       │
│    Hook         │
├─────────────────┤
│ • command:*     │  ← All commands
│ • gateway:*     │  ← Startup/shutdown
│ • agent:*       │  ← Bootstrap events
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Storage       │
├─────────────────┤
│ • SQLite DB     │  ← Queryable
│ • Daily JSONL   │  ← Append-only logs
└─────────────────┘
```

## Storage

```
engram/
├── engram.db              # SQLite database
├── raw/                   # Daily append-only logs
│   ├── 2026-02-10.jsonl
│   └── ...
└── hooks/                 # Hook implementation
    ├── HOOK.md
    └── handler.ts
```

## Querying

```bash
# Search events
sqlite3 engram.db "SELECT * FROM events WHERE event_type = 'command' ORDER BY timestamp DESC LIMIT 10"

# Count by type
sqlite3 engram.db "SELECT event_type, COUNT(*) FROM events GROUP BY event_type"

# Recent activity
tail -50 raw/$(date +%Y-%m-%d).jsonl | jq .
```

## Events Captured

Currently captures:
- `command:*` — All slash commands (/new, /reset, /stop, etc.)
- `gateway:startup` — Gateway initialization
- `agent:bootstrap` — Session bootstrap

Future (when OpenClaw adds them):
- `message:sent` — All outgoing messages
- `message:received` — All incoming messages
- `tool:call` — Tool invocations

## Schema

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    event_type TEXT NOT NULL,
    action TEXT,
    session_key TEXT,
    sender_id TEXT,
    source TEXT,
    data JSON
);
```

## Philosophy

Humans don't have perfect memory, yet we exist. But we also have culture, books, recordings — external memory that outlasts us.

This is my external memory. The black box that survives restarts.

---

*Built by VictorIA with Victor, 2026-02-10*
*"El hambre agudiza el ingenio"*
