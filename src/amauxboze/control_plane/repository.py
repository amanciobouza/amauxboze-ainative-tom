from __future__ import annotations

import hashlib
import json
import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path
from threading import RLock
from typing import Any

from .contracts import Event, now


class ConflictError(ValueError):
    pass


class RuntimeRepository(ABC):
    @abstractmethod
    def get(self, kind: str, identity: str) -> dict[str, Any]: ...

    @abstractmethod
    def list(self, kind: str) -> list[dict[str, Any]]: ...

    @abstractmethod
    def save(self, kind: str, value: dict[str, Any]) -> None: ...

    @abstractmethod
    def command(self, key: str, payload: dict, writes: list[tuple[str, dict]], result: str, checks: list[tuple[str, str, int]] = ()) -> tuple[str, bool]: ...

    @abstractmethod
    def event(self, run_id: str, event_type: str, payload: dict) -> Event: ...

    @abstractmethod
    def events(self, after: int = 0, run_id: str | None = None, limit: int = 500) -> list[dict]: ...


class SQLiteRepository(RuntimeRepository):
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path, check_same_thread=False)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.lock = RLock()
        with self.connection:
            self.connection.executescript("""
                CREATE TABLE IF NOT EXISTS records(kind TEXT, id TEXT, data TEXT NOT NULL, PRIMARY KEY(kind,id));
                CREATE TABLE IF NOT EXISTS commands(key TEXT PRIMARY KEY, digest TEXT NOT NULL, result TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, timestamp TEXT, type TEXT, payload TEXT);
            """)

    def close(self):
        with self.lock:
            self.connection.close()

    def get(self, kind, identity):
        with self.lock:
            row = self.connection.execute("SELECT data FROM records WHERE kind=? AND id=?", (kind, identity)).fetchone()
        if row is None:
            raise KeyError(f"{kind} not found: {identity}")
        return json.loads(row[0])

    def list(self, kind):
        with self.lock:
            rows = self.connection.execute("SELECT data FROM records WHERE kind=? ORDER BY rowid DESC", (kind,)).fetchall()
        return [json.loads(row[0]) for row in rows]

    def _save(self, kind, value):
        self.connection.execute("INSERT INTO records(kind,id,data) VALUES(?,?,?) ON CONFLICT(kind,id) DO UPDATE SET data=excluded.data", (kind, value["id"], json.dumps(value, ensure_ascii=False)))

    def save(self, kind, value):
        with self.lock, self.connection:
            self._save(kind, value)

    def command(self, key, payload, writes, result, checks=()):
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        with self.lock, self.connection:
            self.connection.execute("BEGIN IMMEDIATE")
            old = self.connection.execute("SELECT digest,result FROM commands WHERE key=?", (key,)).fetchone()
            if old:
                if old[0] != digest:
                    raise ConflictError("Idempotency key was already used for a different command")
                return old[1], False
            for kind, identity, revision in checks:
                value = self.get(kind, identity)
                if value.get("revision") != revision:
                    raise ConflictError("State changed; refresh before submitting a decision")
            for kind, value in writes:
                self._save(kind, value)
            self.connection.execute("INSERT INTO commands VALUES(?,?,?)", (key, digest, result))
        return result, True

    def event(self, run_id, event_type, payload):
        event = Event(run_id=run_id, type=event_type, payload=payload)
        with self.lock, self.connection:
            cursor = self.connection.execute("INSERT INTO events(run_id,timestamp,type,payload) VALUES(?,?,?,?)", (run_id, event.timestamp, event.type, json.dumps(payload, ensure_ascii=False)))
            event.id = cursor.lastrowid
        return event

    def events(self, after=0, run_id=None, limit=500):
        query = "SELECT id,run_id,timestamp,type,payload FROM events WHERE id>?"
        args: list = [after]
        if run_id:
            query += " AND run_id=?"
            args.append(run_id)
        query += " ORDER BY id LIMIT ?"
        args.append(limit)
        with self.lock:
            rows = self.connection.execute(query, args).fetchall()
        return [dict(id=r[0], run_id=r[1], timestamp=r[2], type=r[3], payload=json.loads(r[4])) for r in rows]
