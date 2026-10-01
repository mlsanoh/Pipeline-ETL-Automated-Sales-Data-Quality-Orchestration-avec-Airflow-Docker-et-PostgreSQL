import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = Path(os.getenv('SALES_DATA_PATH', str(BASE_DIR / 'data' / 'sales_data.csv')))
ARTIFACT_DIR = Path(os.getenv('SALES_ARTIFACT_DIR', str(BASE_DIR / 'data' / 'runs')))


def postgres_url():
    required = ['PostgreSQL_HOST', 'PostgreSQL_USER', 'PostgreSQL_PASSWORD', 'PostgreSQL_DATABASE']
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise ValueError(f'Configuration PostgreSQL incomplète : {missing}')
    return URL.create(
        'postgresql+psycopg2', username=os.environ['PostgreSQL_USER'],
        password=os.environ['PostgreSQL_PASSWORD'], host=os.environ['PostgreSQL_HOST'],
        port=int(os.getenv('PostgreSQL_PORT', '5432')), database=os.environ['PostgreSQL_DATABASE'],
    )
