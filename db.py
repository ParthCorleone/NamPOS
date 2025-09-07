import sqlite3
from datetime import datetime

DB_NAME = "pos.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    # Products table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        barcode TEXT PRIMARY KEY,
        name TEXT,
        price REAL
    )
    """)
    # Bills table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        datetime TEXT,
        total REAL
    )
    """)
    # Bill items
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bill_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_id INTEGER,
        barcode TEXT,
        product TEXT,
        price REAL,
        quantity INTEGER,
        FOREIGN KEY (bill_id) REFERENCES bills(id)
    )
    """)
    conn.commit()
    conn.close()

def upsert_product(barcode, name, price):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO products (barcode, name, price) VALUES (?, ?, ?)",
                (barcode, name, price))
    conn.commit()
    conn.close()

def get_product(barcode):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT barcode, name, price FROM products WHERE barcode = ?", (barcode,))
    row = cur.fetchone()
    conn.close()
    return row

def save_bill(items, total):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO bills (datetime, total) VALUES (?, ?)", 
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), total))
    bill_id = cur.lastrowid

    for item in items:
        cur.execute('''
            INSERT INTO bill_items (bill_id, product, price, quantity)
            VALUES (?, ?, ?, ?)
        ''', (bill_id, item["name"], float(item["price"]), int(item["quantity"])))

    conn.commit()
    conn.close()
    return bill_id

def get_all_bills():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, datetime, total FROM bills ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_bill_items(bill_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM bill_items WHERE bill_id=?", (bill_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

