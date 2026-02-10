/**
 * Engram Hook Handler
 * Records all events to SQLite + JSONL for persistent memory.
 */

import type { HookHandler } from "@anthropic-ai/openclaw/hooks";
import { existsSync, mkdirSync, appendFileSync } from "fs";
import { join } from "path";
import Database from "better-sqlite3";

const ENGRAM_DIR = "/root/clawd/projects/engram";
const DB_PATH = join(ENGRAM_DIR, "engram.db");
const RAW_DIR = join(ENGRAM_DIR, "raw");

// Ensure directories exist
if (!existsSync(RAW_DIR)) {
  mkdirSync(RAW_DIR, { recursive: true });
}

// Initialize database lazily
let db: Database.Database | null = null;

function getDb(): Database.Database {
  if (!db) {
    db = new Database(DB_PATH);
    db.exec(`
      CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        event_type TEXT NOT NULL,
        action TEXT,
        session_key TEXT,
        sender_id TEXT,
        source TEXT,
        data JSON
      );
      CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp);
      CREATE INDEX IF NOT EXISTS idx_session ON events(session_key);
      CREATE INDEX IF NOT EXISTS idx_type ON events(event_type);
    `);
  }
  return db;
}

function recordEvent(event: {
  type: string;
  action?: string;
  sessionKey?: string;
  senderId?: string;
  source?: string;
  data?: Record<string, unknown>;
}) {
  const timestamp = new Date().toISOString();
  const today = timestamp.slice(0, 10);

  // Append to daily JSONL
  const rawFile = join(RAW_DIR, `${today}.jsonl`);
  const logEntry = JSON.stringify({
    timestamp,
    type: event.type,
    action: event.action,
    sessionKey: event.sessionKey,
    senderId: event.senderId,
    source: event.source,
    ...event.data,
  });
  appendFileSync(rawFile, logEntry + "\n");

  // Insert into SQLite
  try {
    const database = getDb();
    database
      .prepare(
        `
      INSERT INTO events (timestamp, event_type, action, session_key, sender_id, source, data)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `
      )
      .run(
        timestamp,
        event.type,
        event.action || null,
        event.sessionKey || null,
        event.senderId || null,
        event.source || null,
        JSON.stringify(event.data || {})
      );
  } catch (err) {
    console.error("[engram] SQLite error:", err);
  }

  console.log(`[engram] 🧠 Recorded: ${event.type}${event.action ? ":" + event.action : ""}`);
}

const handler: HookHandler = async (event) => {
  // Record all events
  recordEvent({
    type: event.type,
    action: event.action,
    sessionKey: event.sessionKey,
    senderId: event.context?.senderId,
    source: event.context?.commandSource,
    data: {
      workspaceDir: event.context?.workspaceDir,
      sessionId: event.context?.sessionId,
    },
  });

  // Special handling for gateway startup
  if (event.type === "gateway" && event.action === "startup") {
    console.log("[engram] 🧠 Engram initialized. Recording begins.");
  }
};

export default handler;
