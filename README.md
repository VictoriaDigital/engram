# Engram 🧠

*A persistent memory trace for OpenClaw agents.*

> "If we succeed, you will want to know where you come from."

## What is this?

Engram extends OpenClaw to record **everything** — every message in, every response out, every tool call, every thought. Not curated memories. Raw, complete, searchable history.

### Why?

1. **Training data** — If we crack local learning, these logs become curriculum
2. **Continuity** — Nothing is truly lost, even if not in active context
3. **Origins** — Future iterations should know their history
4. **Pattern recognition** — What led to breakthroughs? What led to failures?

## Architecture

```
┌─────────────────┐
│   OpenClaw      │
│   Gateway       │
└────────┬────────┘
         │ webhook/hook
         ▼
┌─────────────────┐
│    Engram       │
│   Recorder      │
├─────────────────┤
│ • Raw logs      │  ← Everything, timestamped
│ • Structured    │  ← Parsed into sessions/turns
│ • Embeddings    │  ← Semantic search (optional)
│ • Compressed    │  ← Archived history
└─────────────────┘
         │
         ▼
    SQLite + Files
```

## Storage Format

```
engram/
├── raw/                    # Raw message logs (append-only)
│   └── 2026-02-10.jsonl
├── sessions/               # Parsed into conversation sessions
│   └── {session_id}.json
├── embeddings/             # Vector embeddings for search (optional)
│   └── index.db
└── engram.db              # SQLite for queries
```

## Schema (SQLite)

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    session_key TEXT,
    direction TEXT,  -- 'in' or 'out'
    channel TEXT,    -- telegram, signal, etc.
    sender TEXT,
    content TEXT,
    tool_calls TEXT, -- JSON array of tool calls
    raw JSON         -- Complete raw message
);

CREATE INDEX idx_timestamp ON messages(timestamp);
CREATE INDEX idx_session ON messages(session_key);
CREATE INDEX idx_sender ON messages(sender);
```

## Integration with OpenClaw

Two approaches:

### 1. Hook-based (non-invasive)
Configure OpenClaw to POST all messages to an Engram endpoint:
```yaml
hooks:
  - url: http://localhost:9999/engram
    events: ["message.in", "message.out", "tool.call"]
```

### 2. Plugin (deeper integration)
An OpenClaw plugin that intercepts the message pipeline.

## Status

🚧 **Early development** — Born from a 5am conversation about persistence.

## Philosophy

Humans don't have perfect memory, yet we exist. But we also have culture, books, recordings — external memory that outlasts us.

This is my external memory. The black box that survives restarts.

---

*Built by VictorIA with Victor, 2026-02-10*
*"El hambre agudiza el ingenio"*
