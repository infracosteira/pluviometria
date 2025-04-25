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

import pandas as pd

# Carregar dados
df_ibge = pd.read_csv('./data/municipios.csv', encoding='latin1', sep=';')

df = pd.read_csv('./data/maindatabase_sa.csv', encoding='latin1', sep=',')

# Processar municípios
municipios = df_ibge[['cod_ibge', 'municipio']].drop_duplicates().reset_index(drop=True)
municipios.insert(0, 'id', range(len(municipios)))

# Padronizar nomes para minúsculas e remover espaços extras
municipios['municipio'] = municipios['municipio'].str.strip().str.lower()

# Processar postos
postos = df[['ID', 'Nome_Posto', 'Nome_Municipio', 'Dias_dados_medidos', 'Dias_falhos', 
             'Numero_meses_completos', 'Numero_meses_falha', 'Numero_anos_falha', 
             'Numero_anos_completos', 'Precipitacao_media_anual', 'Coordenada_Y', 'Coordenada_X']].drop_duplicates()

postos['Nome_Municipio'] = postos['Nome_Municipio'].str.strip().str.lower()
postos['Nome_Posto'] = postos['Nome_Posto'].str.strip().str.lower()

postos = postos.merge(municipios[['cod_ibge', 'municipio']], 
                      left_on='Nome_Municipio', 
                      right_on='municipio', 
                      how='left').drop(columns=['municipio'])

# Tipos e transformações
integer_columns = ['ID', 'Dias_dados_medidos', 'Dias_falhos', 'Numero_meses_completos', 
                   'Numero_meses_falha', 'Numero_anos_falha', 'Numero_anos_completos']
postos[integer_columns] = postos[integer_columns].astype(int)

postos['Precipitacao_media_anual'] = postos['Precipitacao_media_anual'].astype(str).str.replace(',', '.').astype(float)

postos['coordenadas'] = postos['Coordenada_Y'].astype(str) + ',' + postos['Coordenada_X'].astype(str)
postos.drop(columns=['Coordenada_Y', 'Coordenada_X'], inplace=True)

postos.rename(columns={
    'ID': 'id_posto',
    'Dias_dados_medidos': 'numero_dias_medidos',
    'Dias_falhos': 'numero_dias_falhos',
    'Numero_meses_completos': 'numero_meses_medidos',
    'Numero_meses_falha': 'numero_meses_falhos',
    'Numero_anos_falha': 'numero_anos_falha',
    'Numero_anos_completos': 'numero_anos_medidos'
}, inplace=True)

# Processar registros
registros = df[['Total', 'Meses', 'Anos', 'ID']].rename(columns={
    'Total': 'total_dia',
    'Meses': 'mes',
    'Anos': 'ano',
    'ID': 'id_posto'
})
registros.insert(0, 'id', range(len(registros)))

# Garantir que todas as colunas estejam em lowercase
municipios.columns = municipios.columns.str.lower()
postos.columns = postos.columns.str.lower()
registros.columns = registros.columns.str.lower()
postos.drop(columns=['nome_municipio'], inplace=True)
# Inserção em lotes
batch_size = 5000

def insert_batch(table_name, data):
    """ Insere os dados em lotes para evitar sobrecarga """
    test_data = data.to_dict(orient='records')
    for i in range(0, len(test_data), batch_size):
        batch = test_data[i:i + batch_size]
        supabase.table(table_name).insert(batch).execute()
        print(f"Inserindo lote na tabela {table_name}... Parte {i//batch_size + 1}")

# Enviar dados para o Supabase
insert_batch("municipio", municipios)
insert_batch("posto", postos)
insert_batch("registro", registros)

print("Inserção concluída com sucesso!")