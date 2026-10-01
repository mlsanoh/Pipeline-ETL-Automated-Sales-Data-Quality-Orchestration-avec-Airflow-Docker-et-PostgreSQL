import hashlib
import os
from pathlib import Path
import pandas as pd
from include.config import ARTIFACT_DIR


def write_artifact(df, run_id, stage):
    # Un dossier par exécution et une écriture atomique pour les reprises de tâche.
    directory = ARTIFACT_DIR / hashlib.sha256(run_id.encode()).hexdigest()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f'{stage}.parquet'
    temporary = path.with_suffix('.parquet.tmp')
    df.to_parquet(temporary, index=False)
    os.replace(temporary, path)
    return str(path)


def read_artifact(path):
    return pd.read_parquet(Path(path))
