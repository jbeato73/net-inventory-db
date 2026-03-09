# =============================================================================
# database_manager.py
#
# Author  : Jose M. Beato
# Created : March 9, 2026
# Built with the assistance of Claude (Anthropic) — claude.ai
#
# Description:
#   Initializes a SQLite inventory database, provides functions to add
#   network devices and display the current inventory. Serves as the
#   core data layer for the network infrastructure tracking system.
#
# Project Setup (run in terminal before opening VS Code):
# ─────────────────────────────────────────────────────
#   1. cd /Users/jmb/PythonProjects
#   2. uv init net-inventory-db
#   3. cd net-inventory-db
#   4. code .
#   5. python3 -m venv .venv
#   6. source .venv/bin/activate
#   # No extra packages — 100% Python standard library (sqlite3)
#   # Create this file as: database_manager.py
#
# GitHub Commit (after completing):
# ──────────────────────────────────
#   git add database_manager.py
#   git commit -m "refactor: standardize database_manager.py header and structure"
#   git push origin main
# =============================================================================

import sqlite3  # Built-in: SQLite database engine


# =============================================================================
# SECTION 1 — CONFIGURATION
# Best Practice: Keep constants at the top for easy updates.
# =============================================================================

DB_FILE = "inventory.db"  # SQLite database file path


# =============================================================================
# SECTION 2 — DATABASE INITIALIZATION
# Best Practice: Always use CREATE TABLE IF NOT EXISTS so the script is
# safe to run multiple times without errors.
# =============================================================================


def init_database():
    """
    Connects to the SQLite database (creates the file if it doesn't exist)
    and creates the devices table if it's not already present.

    Returns:
        sqlite3.Connection: Open database connection.

    Best Practice: Use ? placeholders (parameterized queries) in all
    INSERT/UPDATE statements to prevent SQL injection attacks.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            hostname   TEXT NOT NULL,
            ip_address TEXT UNIQUE NOT NULL,
            model      TEXT,
            status     TEXT
        )
    """)

    conn.commit()
    print(f"[INFO] Database initialized → '{DB_FILE}'")
    return conn


# =============================================================================
# SECTION 3 — DEVICE MANAGEMENT
# Best Practice: Separate insert and query logic into distinct functions.
# Each function does one thing — easier to test and maintain.
# =============================================================================


def add_device(conn, hostname, ip, model):
    """
    Inserts a new device record into the devices table.
    Skips silently if a device with the same IP already exists.

    Args:
        conn     (sqlite3.Connection): Active database connection.
        hostname (str): Device hostname (e.g., "NY-CORE-01").
        ip       (str): Device IP address — must be unique.
        model    (str): Hardware model (e.g., "Cisco Nexus").
    """
    cursor = conn.cursor()
    try:
        # Best Practice: Use ? placeholders — never format values directly
        # into SQL strings. This prevents SQL injection vulnerabilities.
        cursor.execute(
            """
            INSERT INTO devices (hostname, ip_address, model, status)
            VALUES (?, ?, ?, ?)
            """,
            (hostname, ip, model, "OFFLINE"),
        )
        conn.commit()
        print(f"[INFO] Device added → {hostname} ({ip})")
    except sqlite3.IntegrityError:
        print(f"[WARN] Skipping: Device with IP {ip} already exists.")


def show_inventory(conn):
    """
    Retrieves and prints all device records in a formatted table.

    Args:
        conn (sqlite3.Connection): Active database connection.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM devices")
    rows = cursor.fetchall()

    print()
    print("=" * 60)
    print("  NETWORK INVENTORY — CURRENT RECORDS")
    print("  Jose M. Beato | March 9, 2026")
    print("=" * 60)
    for row in rows:
        print(f"  ID: {row[0]}  |  Host: {row[1]}  |  IP: {row[2]}  |  Model: {row[3]}")
    print("=" * 60)
    print()


# =============================================================================
# SECTION 4 — MAIN ENTRY POINT
# Best Practice: Always use `if __name__ == "__main__"` to protect your
# main logic so this module can be safely imported by ai_advisor.py.
# =============================================================================


def main():
    """
    Orchestrates the full pipeline:
    Init DB → Add Devices → Show Inventory → Close Connection
    """
    print()
    print("=" * 60)
    print("  database_manager.py — Starting...")
    print("=" * 60)
    print()

    db_connection = init_database()

    add_device(db_connection, "NY-CORE-01", "10.0.0.1", "Cisco Nexus")
    add_device(db_connection, "LON-BDR-02", "172.16.0.5", "Juniper MX")

    show_inventory(db_connection)

    db_connection.close()
    print("[INFO] Database connection closed.")


if __name__ == "__main__":
    main()

