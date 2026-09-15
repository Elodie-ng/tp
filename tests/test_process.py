import pytest
from decimal import Decimal
from src.process import (
    parse_line, 
    sum_by_iban_origine, 
    sum_by_banque_source,
    sum_by_iban_dest,
    Transaction
)

def test_parse_line_valid():
    row = ["2024-03-01T09:12:00", "FR123", "FR", "BNP", "DE456", "DE", "1250.00", "EUR"]
    tx = parse_line(row)
    assert tx["iban_origine"] == "FR123"
    assert tx["montant"] == Decimal("1250.00")
    assert tx["is_large"] is False

def test_parse_line_is_large():
    row = ["2024-03-01T09:12:00", "FR123", "FR", "BNP", "DE456", "DE", "5000.01", "EUR"]
    tx = parse_line(row)
    assert tx["is_large"] is True

def test_parse_line_invalid_montant():
    row = ["2024-03-01T09:12:00", "FR123", "FR", "BNP", "DE456", "DE", "AAAA", "EUR"]
    with pytest.raises(ValueError, match="Montant non numérique"):
        parse_line(row)

def test_aggregations():
    txs: list[Transaction] = [
        {"datetime": "", "iban_origine": "FR1", "pays_source": "", "banque_source": "BNP", "iban_dest": "DE1", "pays_dest": "", "montant": Decimal("10.50"), "devise": "EUR", "is_large": False},
        {"datetime": "", "iban_origine": "FR1", "pays_source": "", "banque_source": "BNP", "iban_dest": "DE2", "pays_dest": "", "montant": Decimal("5.00"), "devise": "EUR", "is_large": False},
        {"datetime": "", "iban_origine": "FR2", "pays_source": "", "banque_source": "SG", "iban_dest": "DE1", "pays_dest": "", "montant": Decimal("20.00"), "devise": "EUR", "is_large": False},
    ]
    
    res_iban = sum_by_iban_origine(txs)
    assert res_iban["FR1"] == Decimal("15.50")
    assert res_iban["FR2"] == Decimal("20.00")
    
    res_banque = sum_by_banque_source(txs)
    assert res_banque["BNP"] == Decimal("15.50")
    assert res_banque["SG"] == Decimal("20.00")

    res_dest = sum_by_iban_dest(txs)
    assert res_dest["DE1"] == Decimal("30.50")
    assert res_dest["DE2"] == Decimal("5.00")
