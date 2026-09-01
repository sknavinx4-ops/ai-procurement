"""
database.py
Handles SQLite connection and schema creation for the AI Procurement ERP.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "procurement.db")


def get_connection():
    """Return a sqlite3 connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they do not already exist, and seed demo data."""
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS vendors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_name TEXT NOT NULL,
            contact TEXT,
            email TEXT,
            category TEXT,
            rating REAL DEFAULT 0,
            status TEXT DEFAULT 'Active'
        );

        CREATE TABLE IF NOT EXISTS rfqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rfq_number TEXT UNIQUE NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            required_date TEXT,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Open'
        );

        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rfq_id INTEGER NOT NULL,
            vendor_id INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_price REAL,
            delivery_days INTEGER,
            warranty_months INTEGER DEFAULT 0,
            quote_date TEXT DEFAULT CURRENT_TIMESTAMP,
            ai_score REAL,
            FOREIGN KEY (rfq_id) REFERENCES rfqs (id),
            FOREIGN KEY (vendor_id) REFERENCES vendors (id)
        );

        CREATE TABLE IF NOT EXISTS purchase_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            po_number TEXT UNIQUE NOT NULL,
            vendor_id INTEGER NOT NULL,
            rfq_id INTEGER NOT NULL,
            total_amount REAL,
            order_date TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Approved',
            FOREIGN KEY (vendor_id) REFERENCES vendors (id),
            FOREIGN KEY (rfq_id) REFERENCES rfqs (id)
        );

        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            quantity INTEGER DEFAULT 0,
            unit_price REAL,
            supplier TEXT,
            updated_date TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS finance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            po_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            paid_amount REAL DEFAULT 0,
            payment_status TEXT DEFAULT 'Pending',
            updated_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (po_id) REFERENCES purchase_orders (id)
        );
        """
    )

    # Seed a few demo vendors only if the table is empty, so re-running is safe.
    cur.execute("SELECT COUNT(*) AS c FROM vendors")
    if cur.fetchone()["c"] == 0:
        cur.executemany(
            """INSERT INTO vendors (vendor_name, contact, email, category, rating, status)
               VALUES (?, ?, ?, ?, ?, ?)""",
            [
                ("ABC Ltd", "9876543210", "contact@abcltd.com", "Electronics", 4.5, "Active"),
                ("XYZ Corp", "9876500000", "sales@xyzcorp.com", "IT Hardware", 4.2, "Active"),
                ("PQR Industries", "9876511111", "info@pqrind.com", "Office Supplies", 3.8, "Active"),
            ],
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
