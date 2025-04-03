
import os

## NONE SAFE Variante --> Credentials in .env file speichern
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "user")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "Nuts3")
DB_PORT = os.getenv("DB_PORT", "5432")

# Create SQLAlchemy engine
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

