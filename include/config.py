import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("PostgreSQL_HOST")
DB_USER = os.getenv("PostgreSQL_USER")
DB_PASSWORD = os.getenv("PostgreSQL_PASSWORD")
DB_PORT = os.getenv("PostgreSQL_PORT")
DB_NAME = os.getenv("PostgreSQL_DATABASE")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "sales_data.csv")

# La chaîne de connexion MySQL
PostgreSQL_CONN = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"