import csv
from pathlib import Path

def generate_csvs(output_dir: Path) -> None:
    output_dir.mkdir(exist_ok=True)
    
    # On respecte la règle : 3 fichiers, 5 transactions par fichier
    # Les IBAN 'FR...1' et 'FR...2' reviennent plusieurs fois
    data = [
        # Fichier 1
        [
            ["2024-03-01T09:12:00", "FR763000600001", "FR", "BNP", "DE89370", "DE", "1250.00", "EUR"],
            ["2024-03-01T10:45:00", "FR763000600001", "FR", "BNP", "ES91210", "ES", "7400.50", "EUR"],
            ["2024-03-01T11:20:00", "FR763000600002", "FR", "SG", "IT12345", "IT", "45.00", "EUR"],
            ["2024-03-01T14:15:00", "FR763000600003", "FR", "CA", "BE98765", "BE", "320.00", "EUR"],
            ["2024-03-01T16:30:00", "FR763000600001", "FR", "BNP", "NL55443", "NL", "15.99", "EUR"]
        ],
        # Fichier 2
        [
            ["2024-03-02T09:12:00", "FR763000600002", "FR", "SG", "DE89371", "DE", "250.00", "EUR"],
            ["2024-03-02T10:45:00", "FR763000600004", "FR", "LCL", "IT91210", "IT", "6000.00", "EUR"],
            ["2024-03-02T11:00:00", "FR763000600002", "FR", "SG", "ES11223", "ES", "112.50", "EUR"],
            ["2024-03-02T15:40:00", "FR763000600005", "FR", "CM", "DE44332", "DE", "890.00", "EUR"],
            ["2024-03-02T17:10:00", "FR763000600006", "FR", "BP", "GB99887", "GB", "55.00", "EUR"]
        ],
        # Fichier 3
        [
            ["2024-03-03T09:12:00", "FR763000600003", "FR", "CA", "DE89372", "DE", "10.00", "EUR"],
            ["2024-03-03T10:00:00", "FR763000600001", "FR", "BNP", "ES33445", "ES", "450.00", "EUR"],
            ["2024-03-03T11:30:00", "FR763000600007", "FR", "SG", "IT22110", "IT", "20.00", "EUR"],
            ["2024-03-03T14:20:00", "FR763000600002", "FR", "SG", "BE33221", "BE", "99.99", "EUR"],
            ["2024-03-03T18:05:00", "FR763000600008", "FR", "LCL", "DE55667", "DE", "105.50", "EUR"]
        ]
    ]

    headers = ["datetime", "iban_origine", "pays_source", "banque_source", "iban_dest", "pays_dest", "montant", "devise"]
    
    for i, rows in enumerate(data, 1):
        with open(output_dir / f"transactions_{i}.csv", 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

if __name__ == "__main__":
    generate_csvs(Path("data"))
    print("Fichiers CSV générés avec succès dans le dossier 'data/'")
