from typing import TypedDict
from decimal import Decimal, InvalidOperation

class Transaction(TypedDict):
    datetime: str
    iban_origine: str
    pays_source: str
    banque_source: str
    iban_dest: str
    pays_dest: str
    montant: Decimal
    devise: str
    is_large: bool

def parse_line(row: list[str]) -> Transaction:
    if len(row) != 8:
        raise ValueError("Nombre de colonnes invalide")
    try:
        montant = Decimal(row[6])
    except InvalidOperation:
        raise ValueError("Montant non numérique")
        
    return {
        "datetime": row[0],
        "iban_origine": row[1],
        "pays_source": row[2],
        "banque_source": row[3],
        "iban_dest": row[4],
        "pays_dest": row[5],
        "montant": montant,
        "devise": row[7],
        "is_large": montant > Decimal("5000.00")
    }

def process_transactions(rows: list[list[str]]) -> list[Transaction]:
    return [parse_line(row) for row in rows]

def sum_by_iban_origine(txs: list[Transaction]) -> dict[str, Decimal]:
    result: dict[str, Decimal] = {}
    for tx in txs:
        result[tx["iban_origine"]] = result.get(tx["iban_origine"], Decimal("0")) + tx["montant"]
    return result

def sum_by_banque_source(txs: list[Transaction]) -> dict[str, Decimal]:
    result: dict[str, Decimal] = {}
    for tx in txs:
        result[tx["banque_source"]] = result.get(tx["banque_source"], Decimal("0")) + tx["montant"]
    return result

def sum_by_iban_dest(txs: list[Transaction]) -> dict[str, Decimal]:
    result: dict[str, Decimal] = {}
    for tx in txs:
        result[tx["iban_dest"]] = result.get(tx["iban_dest"], Decimal("0")) + tx["montant"]
    return result
