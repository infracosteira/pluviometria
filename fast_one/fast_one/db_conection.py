import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, registry
from dotenv import load_dotenv

load_dotenv()

USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DBNAME = os.getenv("DB_NAME")

if not all([USER, PASSWORD, HOST, PORT, DBNAME]):
    raise ValueError("Uma ou mais variáveis de ambiente do banco de dados estão faltando. Por favor, verifique seu arquivo .env.")

DATABASE_URL = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
#postgresql://postgres:973717@localhost:5432/pluviometria

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
reg = registry()

print("✅ Conexão com o banco de dados (via Pooler) configurada com sucesso!")
