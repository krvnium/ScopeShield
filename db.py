"""Local SQLite persistence for ScopeShield."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).with_name("scopeshield.db")


def get_connection(db_path: str | Path = DB_PATH) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db(db_path: str | Path = DB_PATH) -> None:
    with get_connection(db_path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                upload_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS contract_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_id INTEGER NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
                page_number INTEGER NOT NULL,
                text_content TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS change_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_id INTEGER NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
                feature_summary TEXT NOT NULL,
                verdict TEXT NOT NULL,
                cited_page INTEGER,
                hours REAL NOT NULL,
                rate REAL NOT NULL,
                total_cost REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'confirmed',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )


def insert_contract(title: str, pages: list[dict[str, Any]], db_path: str | Path = DB_PATH) -> int:
    with get_connection(db_path) as connection:
        cursor = connection.execute("INSERT INTO contracts (title) VALUES (?)", (title,))
        contract_id = int(cursor.lastrowid)
        connection.executemany(
            "INSERT INTO contract_pages (contract_id, page_number, text_content) VALUES (?, ?, ?)",
            [(contract_id, page["page_number"], page["text"]) for page in pages],
        )
    return contract_id


def get_contract_pages(contract_id: int, db_path: str | Path = DB_PATH) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            "SELECT page_number, text_content FROM contract_pages WHERE contract_id = ? ORDER BY page_number",
            (contract_id,),
        ).fetchall()
    return [{"page_number": row["page_number"], "text": row["text_content"]} for row in rows]


def save_change_order(
    contract_id: int,
    feature_summary: str,
    verdict: str,
    cited_page: int | None,
    hours: float,
    rate: float,
    total_cost: float,
    db_path: str | Path = DB_PATH,
) -> int:
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """INSERT INTO change_orders
            (contract_id, feature_summary, verdict, cited_page, hours, rate, total_cost)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (contract_id, feature_summary, verdict, cited_page, hours, rate, total_cost),
        )
        return int(cursor.lastrowid)


def get_dashboard_totals(db_path: str | Path = DB_PATH) -> dict[str, int | float]:
    with get_connection(db_path) as connection:
        contracts = connection.execute("SELECT COUNT(*) FROM contracts").fetchone()[0]
        caught = connection.execute(
            "SELECT COUNT(*) FROM change_orders WHERE LOWER(verdict) IN ('out of scope', 'scope creep', 'no')"
        ).fetchone()[0]
        revenue = connection.execute(
            "SELECT COALESCE(SUM(total_cost), 0) FROM change_orders WHERE status = 'confirmed'"
        ).fetchone()[0]
    return {"contracts": contracts, "caught": caught, "revenue_saved": float(revenue)}


def calculate_total_revenue_saved(db_path: str | Path = DB_PATH) -> float:
    return float(get_dashboard_totals(db_path)["revenue_saved"])
