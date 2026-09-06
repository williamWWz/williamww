import json
import sqlite3
from pathlib import Path
from app.models import ApplicationStatus, Job, Profile

class Repository:
    def __init__(self, database_path="app/data/applications.db"):
        self.database_path = str(database_path); Path(self.database_path).parent.mkdir(parents=True, exist_ok=True); self._initialize()
    def _connect(self):
        connection = sqlite3.connect(self.database_path); connection.row_factory = sqlite3.Row; return connection
    def _initialize(self):
        with self._connect() as connection:
            connection.executescript("""
            CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS applications (
              id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT NOT NULL UNIQUE,
              company TEXT NOT NULL DEFAULT '', title TEXT NOT NULL DEFAULT '',
              status TEXT NOT NULL DEFAULT 'saved', notes TEXT NOT NULL DEFAULT '',
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            """)
    def save_profile(self, profile):
        profile.validate(); payload = json.dumps(profile.__dict__, ensure_ascii=False)
        with self._connect() as connection:
            connection.execute("INSERT INTO settings(key,value) VALUES('profile',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (payload,))
    def load_profile(self):
        with self._connect() as connection: row = connection.execute("SELECT value FROM settings WHERE key='profile'").fetchone()
        return Profile(**json.loads(row["value"])) if row else None
    def add_job(self, job):
        job.validate()
        with self._connect() as connection:
            cursor = connection.execute("INSERT INTO applications(url,company,title) VALUES(?,?,?)", (job.url.strip(), job.company.strip(), job.title.strip()))
        return cursor.lastrowid
    def list_applications(self):
        with self._connect() as connection: rows = connection.execute("SELECT * FROM applications ORDER BY id DESC").fetchall()
        return [dict(row) for row in rows]
    def update_application(self, application_id, status, notes):
        with self._connect() as connection:
            cursor = connection.execute("UPDATE applications SET status=?,notes=?,updated_at=CURRENT_TIMESTAMP WHERE id=?", (status.value, notes.strip(), application_id))
            if cursor.rowcount != 1: raise ValueError("Application not found.")
    def delete_application(self, application_id):
        with self._connect() as connection: connection.execute("DELETE FROM applications WHERE id=?", (application_id,))
