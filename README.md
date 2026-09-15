# Projet Pipeline de Données Python / SQLite

## 1. Installation et exécution
- Créer l'environnement : `python3 -m venv venv && source venv/bin/activate`
- Installer les dépendances : `pip install pytest mypy`
- Lancer la pipeline : `python -m src.pipeline`
- Lancer les tests : `pytest tests/`
- Vérifier le typage : `mypy src/ tests/`

## 2. Schéma de la base de données
- **processed_files** : `file_hash` (TEXT, PRIMARY KEY). Stocke l'empreinte des fichiers traités.
- **transactions** : `id` (INTEGER, PRIMARY KEY AUTOINCREMENT), `iban_origine` (TEXT), `montant` (TEXT), `is_large` (BOOLEAN).

## 3. Stratégies implémentées
- **Lignes invalides** : Rejet global. Si une ligne est invalide (ex: montant non convertible), une exception est levée. La transaction SQLite échoue (rollback), garantissant l'absence d'insertion partielle.
- **Idempotence** : Le hash SHA256 du contenu du fichier est calculé et stocké en base. Si un fichier au contenu identique est traité à nouveau, une `IntegrityError` est levée par SQLite, bloquant le traitement des doublons. Le nom du fichier est ignoré dans ce processus.

## 4. Réponses aux questions

### Étape 6 : Comportement en cas d'échec et MyPy vs Tests
**Crash de la pipeline :** 
En insérant un dictionnaire avec des colonnes manquantes (KeyError), le script sort avec un code d'erreur, et SQLite effectue un rollback. La base reste dans un état propre (0 ligne insérée).
**MyPy vs Tests :** 
En assignant un `float` (50.5) à un champ défini comme `Decimal` dans un `TypedDict`, `pytest` valide le code car Python est dynamiquement typé au runtime. En revanche, `mypy` détecte l'incohérence statiquement (`Incompatible types`). Cela montre que les tests valident la logique d'exécution, tandis que MyPy sécurise la structure et les contrats de données avant même l'exécution.

### Étape 7 : Retry
Face à une erreur d'insertion en base :
- **Erreurs justifiant un retry :** `sqlite3.OperationalError` (ex: `database is locked`). C'est une erreur de concurrence transitoire. Attendre quelques millisecondes et réessayer permet souvent de passer.
- **Erreurs ne justifiant aucun retry :** `sqlite3.IntegrityError` ou `sqlite3.ProgrammingError` (syntaxe SQL invalide). Ce sont des erreurs déterministes. Le résultat sera toujours un échec.

**Implémentation :** Une boucle avec un `time.sleep()` intercepte les `OperationalError` pour tenter jusqu'à 3 réinsertions, tandis que les autres exceptions remontent directement pour stopper la pipeline.
