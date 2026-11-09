"""SQLite 저장소.

DB 접근은 이 파일에만 둡니다. 나중에 Postgres 등으로 옮길 때 이 파일만 바꾸면 됩니다.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")

SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    district TEXT NOT NULL,
    building_type TEXT NOT NULL,
    floor_area TEXT NOT NULL DEFAULT '',
    floors INTEGER,
    has_elevator INTEGER,
    monthly_cost INTEGER,
    concerns TEXT NOT NULL DEFAULT '',
    message TEXT NOT NULL DEFAULT '',
    consent_collect_at TEXT NOT NULL,
    consent_marketing INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT '신규',
    admin_memo TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS rounds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    district TEXT NOT NULL,
    summary TEXT NOT NULL,
    details TEXT NOT NULL DEFAULT '',
    target_buildings INTEGER NOT NULL,
    deadline TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    tiers_json TEXT NOT NULL,
    price_note TEXT NOT NULL DEFAULT '',
    fee_disclosure TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS participations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    round_id INTEGER NOT NULL REFERENCES rounds(id),
    created_at TEXT NOT NULL,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    district TEXT NOT NULL,
    building_type TEXT NOT NULL,
    floor_area TEXT NOT NULL DEFAULT '',
    floors INTEGER,
    current_cost INTEGER,
    message TEXT NOT NULL DEFAULT '',
    consent_collect_at TEXT NOT NULL,
    consent_vendor_share INTEGER NOT NULL DEFAULT 0,
    consent_marketing INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT '신청',
    admin_memo TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_participations_round ON participations(round_id);
"""

LEAD_STATUSES: tuple[str, ...] = ("신규", "연락함", "진단 완료", "계약", "보류")
PARTICIPATION_STATUSES: tuple[str, ...] = ("신청", "확정", "취소")

_LEAD_COLUMNS = (
    "name", "phone", "district", "building_type", "floor_area", "floors", "has_elevator",
    "monthly_cost", "concerns", "message", "consent_marketing",
)
_ROUND_COLUMNS = (
    "title", "category", "district", "summary", "details", "target_buildings", "deadline",
    "status", "tiers_json", "price_note", "fee_disclosure",
)
_PARTICIPATION_COLUMNS = (
    "name", "phone", "district", "building_type", "floor_area", "floors", "current_cost",
    "message", "consent_vendor_share", "consent_marketing",
)


# 값이 비어 오면 넣을 기본값 (NOT NULL 열).
_DEFAULTS: dict[str, object] = {
    "floor_area": "", "concerns": "", "message": "", "details": "", "price_note": "",
    "fee_disclosure": "", "consent_marketing": 0, "consent_vendor_share": 0,
}


def _values(data: dict, cols: list[str]) -> list[object]:
    out = []
    for c in cols:
        v = data.get(c)
        out.append(_DEFAULTS.get(c) if v is None and c in _DEFAULTS else v)
    return out


def now_kst() -> datetime:
    return datetime.now(KST)


def today_kst() -> date:
    return now_kst().date()


def _stamp() -> str:
    return now_kst().isoformat(timespec="seconds")


class Repo:
    def __init__(self, path: str) -> None:
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    # ---- 무료 진단 신청 -------------------------------------------------
    def add_lead(self, data: dict) -> int:
        cols = list(_LEAD_COLUMNS)
        values = _values(data, cols)
        stamp = _stamp()
        sql = (
            f"INSERT INTO leads ({', '.join(cols)}, created_at, consent_collect_at) "
            f"VALUES ({', '.join('?' for _ in cols)}, ?, ?)"
        )
        with self._conn() as conn:
            return conn.execute(sql, [*values, stamp, stamp]).lastrowid

    def list_leads(self) -> list[sqlite3.Row]:
        with self._conn() as conn:
            return conn.execute("SELECT * FROM leads ORDER BY id DESC").fetchall()

    def get_lead(self, lead_id: int) -> sqlite3.Row | None:
        with self._conn() as conn:
            return conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()

    def update_lead(self, lead_id: int, status: str, memo: str) -> bool:
        with self._conn() as conn:
            cur = conn.execute(
                "UPDATE leads SET status = ?, admin_memo = ? WHERE id = ?", (status, memo, lead_id)
            )
            return cur.rowcount == 1

    def lead_status_counts(self) -> dict[str, int]:
        counts = {s: 0 for s in LEAD_STATUSES}
        with self._conn() as conn:
            for row in conn.execute("SELECT status, COUNT(*) AS n FROM leads GROUP BY status"):
                counts[row["status"]] = row["n"]
        return counts

    # ---- 공동구매 라운드 ------------------------------------------------
    def add_round(self, data: dict, slug: str) -> int:
        cols = list(_ROUND_COLUMNS)
        values = _values(data, cols)
        sql = (
            f"INSERT INTO rounds ({', '.join(cols)}, slug, created_at) "
            f"VALUES ({', '.join('?' for _ in cols)}, ?, ?)"
        )
        with self._conn() as conn:
            return conn.execute(sql, [*values, slug, _stamp()]).lastrowid

    def update_round(self, round_id: int, data: dict) -> bool:
        cols = list(_ROUND_COLUMNS)
        sets = ", ".join(f"{c} = ?" for c in cols)
        with self._conn() as conn:
            cur = conn.execute(
                f"UPDATE rounds SET {sets} WHERE id = ?", [*_values(data, cols), round_id]
            )
            return cur.rowcount == 1

    def get_round(self, round_id: int) -> sqlite3.Row | None:
        with self._conn() as conn:
            return conn.execute("SELECT * FROM rounds WHERE id = ?", (round_id,)).fetchone()

    def get_round_by_slug(self, slug: str) -> sqlite3.Row | None:
        with self._conn() as conn:
            return conn.execute("SELECT * FROM rounds WHERE slug = ?", (slug,)).fetchone()

    def list_rounds(self, statuses: tuple[str, ...] | None = None) -> list[sqlite3.Row]:
        with self._conn() as conn:
            if statuses is None:
                return conn.execute("SELECT * FROM rounds ORDER BY id DESC").fetchall()
            marks = ", ".join("?" for _ in statuses)
            return conn.execute(
                f"SELECT * FROM rounds WHERE status IN ({marks}) ORDER BY deadline ASC, id DESC",
                statuses,
            ).fetchall()

    def participant_counts(self) -> dict[int, int]:
        """라운드별 참여 건물 수 (취소 제외)."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT round_id, COUNT(*) AS n FROM participations "
                "WHERE status != '취소' GROUP BY round_id"
            ).fetchall()
        return {row["round_id"]: row["n"] for row in rows}

    # ---- 라운드 참여 ----------------------------------------------------
    def add_participation(self, round_id: int, data: dict) -> int:
        cols = list(_PARTICIPATION_COLUMNS)
        values = _values(data, cols)
        sql = (
            f"INSERT INTO participations ({', '.join(cols)}, round_id, created_at, consent_collect_at) "
            f"VALUES ({', '.join('?' for _ in cols)}, ?, ?, ?)"
        )
        stamp = _stamp()
        with self._conn() as conn:
            return conn.execute(sql, [*values, round_id, stamp, stamp]).lastrowid

    def has_active_participation(self, round_id: int, phone: str) -> bool:
        """같은 전화번호가 이 라운드에 이미 (취소되지 않은) 신청을 했는지."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT 1 FROM participations WHERE round_id = ? AND phone = ? AND status != '취소' "
                "LIMIT 1",
                (round_id, phone),
            ).fetchone()
        return row is not None

    def list_participations(self, round_id: int) -> list[sqlite3.Row]:
        with self._conn() as conn:
            return conn.execute(
                "SELECT * FROM participations WHERE round_id = ? ORDER BY id ASC", (round_id,)
            ).fetchall()

    def get_participation(self, participation_id: int) -> sqlite3.Row | None:
        with self._conn() as conn:
            return conn.execute(
                "SELECT * FROM participations WHERE id = ?", (participation_id,)
            ).fetchone()

    def update_participation(self, participation_id: int, status: str, memo: str) -> bool:
        with self._conn() as conn:
            cur = conn.execute(
                "UPDATE participations SET status = ?, admin_memo = ? WHERE id = ?",
                (status, memo, participation_id),
            )
            return cur.rowcount == 1
