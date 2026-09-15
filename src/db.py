import sqlite3
import hashlib
import time
from typing import Iterable
from pathlib import Path
from src.process import Transaction

def get_file_hash(filepath: Path) -> str:
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def init_db(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS processed_files (
                file_hash TEXT PRIMARY KEY
            );
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                iban_origine TEXT,
                montant TEXT,
                is_large BOOLEAN
            );
        """)

def insert_transactions(db_path: Path, filepath: Path, txs: Iterable[Transaction], max_retries: int = 3) -> None:
    file_hash = get_file_hash(filepath)
    txs_list = list(txs)
    
    for attempt in range(max_retries):
        try:
            with sqlite3.connect(db_path) as conn:
                conn.execute("INSERT INTO processed_files (file_hash) VALUES (?)", (file_hash,))
                conn.executemany("""
                    INSERT INTO transactions (iban_origine, montant, is_large)
                    VALUES (?, ?, ?)
                """, [(tx["iban_origine"], str(tx["montant"]), tx["is_large"]) for tx in txs_list])
            break # Succès, on sort de la boucle de retry
        except sqlite3.OperationalError as e:
            # Étape 7 : Retry si la base est temporairement verrouillée[cite: 1]
            if attempt < max_retries - 1 and "locked" in str(e).lower():
                time.sleep(0.1)
            else:
                raise
