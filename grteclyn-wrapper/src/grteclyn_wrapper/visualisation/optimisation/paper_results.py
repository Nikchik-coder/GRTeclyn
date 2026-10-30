"""Single selection ledger shared by article tables and the spin figure."""
import csv
from pathlib import Path
REPO = Path(__file__).resolve().parents[5]
LEDGER = REPO / "results/optimisation/article/ledger_models.tsv"

def load_models():
    with LEDGER.open() as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    for row in rows:
        for key in ("record", "nx", "ny"):
            row[key] = int(row[key])
        for key in ("ve", "mass", "q1", "q2", "q3", "X", "X_v0", "E19", "E_c"):
            row[key] = float(row[key])
        row["delta"] = 100 * (row["X"]/row["X_v0"] - 1)
    return rows
