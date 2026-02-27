import sqlite3

DB_NAME = "photo_booking.db"

def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # Packages table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS packages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price INTEGER NOT NULL,
        duration_hours INTEGER,
        includes TEXT,
        delivery_days INTEGER,
        is_active INTEGER DEFAULT 1
    )
    """)

    # Bookings table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT,
        event_type TEXT NOT NULL,
        event_date TEXT NOT NULL,
        location TEXT NOT NULL,
        package_id INTEGER NOT NULL,
        message TEXT,
        status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(package_id) REFERENCES packages(id)
    )
    """)

    conn.commit()
    conn.close()

def seed_packages_if_empty():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM packages")
    count = cur.fetchone()[0]

    if count == 0:
        sample = [
            ("Wedding Basic", 15000, 6, "1 Photographer, 200 edited photos", 7, 1),
            ("Wedding Premium", 35000, 10, "2 Photographers, 1 Album, 500 edited photos", 10, 1),
            ("Pre-Wedding", 12000, 4, "Outdoor shoot, 150 edited photos", 5, 1),
            ("Birthday/Event", 8000, 3, "Event coverage, 100 edited photos", 4, 1),
        ]
        cur.executemany("""
            INSERT INTO packages (name, price, duration_hours, includes, delivery_days, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, sample)

    conn.commit()
    conn.close()