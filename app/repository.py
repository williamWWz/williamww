import json
import sqlite3
from pathlib import Path
from typing import Any

from app.models import ApplicationStatus, Job, Profile


class Repository:
    def __init__(self, database_path: str | Path = "app/data/applications.db") -> None:
        self.database_path = str(database_path)
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        statuses = ", ".join(f"'{status.value}'" for status in ApplicationStatus)
        with self._connect() as connection:
            connection.executescript(
                f"""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL UNIQUE,
                    company TEXT NOT NULL DEFAULT '',
                    title TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'saved'
                        CHECK(status IN ({statuses})),
                    notes TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

    def save_profile(self, profile: Profile) -> None:
        profile.validate()
        payload = json.dumps(profile.as_dict(), ensure_ascii=False)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO settings(key, value) VALUES('profile', ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
                """,
                (payload,),
            )

    def load_profile(self) -> Profile | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT value FROM settings WHERE key='profile'"
            ).fetchone()
        return Profile(**json.loads(row["value"])) if row else None

    def add_job(self, job: Job) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO applications(url, company, title) VALUES(?, ?, ?)",
                (job.normalized_url(), job.company.strip(), job.title.strip()),
            )
            return int(cursor.lastrowid)

    def list_applications(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM applications ORDER BY id DESC"
            ).fetchall()
        return [dict(row) for row in rows]

    def update_application(
        self, application_id: int, status: ApplicationStatus, notes: str
    ) -> None:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE applications
                SET status=?, notes=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
                """,
                (status.value, notes.strip(), application_id),
            )
            if cursor.rowcount != 1:
                raise ValueError("Application not found.")

    def delete_application(self, application_id: int) -> None:
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM applications WHERE id=?", (application_id,)
            )
            if cursor.rowcount != 1:
                raise ValueError("Application not found.")
