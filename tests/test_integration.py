import pytest
import sqlite3
from decimal import Decimal
from pathlib import Path
from src.db import init_db, insert_transactions
from src.process import Transaction

@pytest.fixture
def test_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "test.db"
    init_db(db_path)
    return db_path

#test d'intégration
def test_integration_and_idempotence(test_db: Path, tmp_path: Path) -> None:
    file_path = tmp_path / "dummy.csv"
    file_path.write_text("dummy content")
    
    txs: list[Transaction] = [
        {"datetime": "2024", "iban_origine": "FR123", "pays_source": "FR", "banque_source": "BNP", "iban_dest": "DE123", "pays_dest": "DE", "montant": Decimal("6000.00"), "devise": "EUR", "is_large": True},
        {"datetime": "2024", "iban_origine": "FR123", "pays_source": "FR", "banque_source": "BNP", "iban_dest": "DE456", "pays_dest": "DE", "montant": Decimal("1000.00"), "devise": "EUR", "is_large": False}
    ]
    
    insert_transactions(test_db, file_path, txs)
    
    with sqlite3.connect(test_db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        assert count == 2 # Le nombre de lignes insérées[cite: 1]
        
        large_count = conn.execute("SELECT COUNT(*) FROM transactions WHERE is_large = 1").fetchone()[0]
        assert large_count == 1 # Le nombre de transactions marquées au-dessus de 5000[cite: 1]
        
    with pytest.raises(sqlite3.IntegrityError): # Ne crée pas de doublons[cite: 1]
        insert_transactions(test_db, file_path, txs)

#la base reste propre en cas de bug
def test_failure_leaves_clean_state(test_db: Path, tmp_path: Path) -> None:
    file_path = tmp_path / "fail.csv"
    file_path.write_text("fail content")
    txs = [{"iban_origine": "FR123"}] #dictionnaire incomplet
    
    with pytest.raises(KeyError):
        insert_transactions(test_db, file_path, txs) #type: ignore
        
    with sqlite3.connect(test_db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM processed_files").fetchone()[0]
        assert count == 0 

#simulation d'erreur retryable
def test_retry_on_locked_db(test_db: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    file_path = tmp_path / "retry.csv"
    file_path.write_text("retry content")
    txs: list[Transaction] = []
    
    attempts = 0
    original_connect = sqlite3.connect
    
    #on simule un crash lors de la première tentative de connexion à sqlite
    def mock_connect(*args, **kwargs):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise sqlite3.OperationalError("database is locked")
        return original_connect(*args, **kwargs)
        
    monkeypatch.setattr(sqlite3, "connect", mock_connect)
    
    #l'insertion passe quand même grâce au retry, et on vérifie qu'il a bien essayé 2 fois
    insert_transactions(test_db, file_path, txs)
    assert attempts == 2
