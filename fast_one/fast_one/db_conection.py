import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, registry
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")

DATABASE_URL = f"postgresql://postgres:344gwd5W1MDwZ9up@db.hqnkhorlbswlklcfvoob.supabase.co:5432/postgres"

# Criando o motor de conexão
engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=30)

# Criando a sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Registry para a ORM
reg = registry()
