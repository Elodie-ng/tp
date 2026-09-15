import sys
import csv
import sqlite3
from pathlib import Path
from src.generate import generate_csvs
from src.process import process_transactions
from src.db import init_db, insert_transactions

def run_pipeline(data_dir: Path, db_path: Path) -> int:
    generate_csvs(data_dir)
    init_db(db_path)
    has_error = False
    
    for filepath in data_dir.glob("*.csv"):
        try:
            with open(filepath, 'r') as f:
                reader = csv.reader(f)
                next(reader) # skip header
                rows = list(reader)
                
            txs = process_transactions(rows)
            insert_transactions(db_path, filepath, txs)
            print(f"Succès: {filepath.name}")
            
        except sqlite3.IntegrityError:
            print(f"Ignoré (déjà traité): {filepath.name}")
        except Exception as e:
            print(f"Échec sur {filepath.name}: {e}")
            has_error = True
            
    return 1 if has_error else 0

if __name__ == "__main__":
    sys.exit(run_pipeline(Path("data"), Path("pipeline.db")))
