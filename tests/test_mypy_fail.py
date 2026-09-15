from src.process import Transaction

#étape 6 : Erreur détectée par mypy mais pas par les tests
def test_mypy_error() -> None:
    tx: Transaction = {
        "datetime": "2024",
        "iban_origine": "FR1",
        "pays_source": "FR",
        "banque_source": "BNP",
        "iban_dest": "DE1",
        "pays_dest": "DE",
        "montant": 50.5,  #float au lieu de decimal
        "devise": "EUR",
        "is_large": False
    }
    assert tx["iban_origine"] == "FR1"
