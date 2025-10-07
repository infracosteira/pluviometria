import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import re

load_dotenv()

USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DBNAME = os.getenv("DB_NAME")

# Cria conexão com o PostgreSQL local
DATABASE_URL = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
engine = create_engine(DATABASE_URL)


def load_municipio():
    return pd.read_sql("SELECT * FROM municipio", engine)


def load_posto():
    # Usamos ST_Y e ST_X (funções PostGIS) na query para extrair Latitude e Longitude
    # de forma eficiente e segura, evitando a necessidade de parsing em Python.
    query = text("""
    SELECT
        id_posto,
        nome_posto,
        numero_anos_medidos,
        precipitacao_media_anual,
        coordenadas,
        ST_Y(coordenadas) AS "Latitude", 
        ST_X(coordenadas) AS "Longitude"   
    FROM posto
    WHERE coordenadas IS NOT NULL
      AND ST_GeometryType(coordenadas) = 'ST_Point' -- Filtro de robustez
    """)
    
    with engine.connect() as connection:
        # pd.read_sql retorna um DataFrame com as colunas "Latitude" e "Longitude"
        return pd.read_sql(query, connection)


def load_registro():
    return pd.read_sql("SELECT * FROM registro_mensal", engine)


def load_diario():
    return pd.read_sql("SELECT * FROM registro_diario", engine)
