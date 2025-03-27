from dotenv import load_dotenv
import os
import pandas as pd
from supabase import create_client

# Carregar variáveis de ambiente
load_dotenv()

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

supabase = create_client(supabase_url, supabase_key)
print("Conectado ao Supabase!")

# Carregar dados do CSV
df = pd.read_csv('data/maindatabase.csv')

# Criar dicionários para cada tabela
municipios = df[['id_municipio', 'nome_municipio', 'cod_ibge']].drop_duplicates().rename(columns={'id_municipio': 'id'})
postos = df[['id_posto', 'nome_posto', 'dias_dados_medidos', 'dias_falhos', 
             'meses_dados_medidos', 'meses_falhos', 'numero_anos_falha', 
             'numero_anos_completos', 'precipitacao_media_anual', 'coordenadas']].drop_duplicates()
registros = df[['id_registro', 'dia', 'total_dia', 'mes', 'ano']].rename(columns={'id_registro': 'id'})

# Inserção em lotes
batch_size = 5000  

def insert_batch(table_name, data):
    """ Insere os dados em lotes para evitar sobrecarga """
    test_data = data.to_dict(orient='records')
    for i in range(0, len(test_data), batch_size):
        batch = test_data[i:i + batch_size]
        supabase.table(table_name).insert(batch).execute()
        print(f"Inserindo lote na tabela {table_name}... Parte {i//batch_size + 1}")

# Enviar os dados para cada tabela
insert_batch("nome_municipio", municipios)
insert_batch("registro", registros)
insert_batch("nome_posto", postos)

print("Inserção concluída com sucesso!")
