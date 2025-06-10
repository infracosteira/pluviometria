from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime
from supabase import create_client

# === 1. Conexão com o Supabase ===
load_dotenv()
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)
print("Conectado ao Supabase!")

# === 2. Leitura dos arquivos CSV ===
df_ibge = pd.read_csv('./data/municipios.csv', encoding='latin1', sep=';')
df = pd.read_csv('./data/maindatabase_sa.csv', encoding='latin1', sep=',')

# === 3. Processar tabela 'municipio' ===
municipios = df_ibge[['cod_ibge', 'municipio']].drop_duplicates().reset_index(drop=True)
municipios.insert(0, 'id', range(len(municipios)))
municipios['municipio'] = municipios['municipio'].str.strip().str.lower()

# === 4. Processar tabela 'posto' ===
postos = df[['ID', 'Nome_Posto', 'Nome_Municipio', 'Dias_dados_medidos', 'Dias_falhos', 
             'Numero_meses_completos', 'Numero_meses_falha', 'Numero_anos_falha', 
             'Numero_anos_completos', 'Precipitacao_media_anual', 'Coordenada_Y', 'Coordenada_X']].drop_duplicates()

postos['Nome_Municipio'] = postos['Nome_Municipio'].str.strip().str.lower()
postos['Nome_Posto'] = postos['Nome_Posto'].str.strip().str.lower()

postos = postos.merge(
    municipios[['cod_ibge', 'municipio']],
    left_on='Nome_Municipio',
    right_on='municipio',
    how='left'
).drop(columns=['municipio'])

integer_columns = ['ID', 'Dias_dados_medidos', 'Dias_falhos', 'Numero_meses_completos', 
                   'Numero_meses_falha', 'Numero_anos_falha', 'Numero_anos_completos']
postos[integer_columns] = postos[integer_columns].astype(int)

postos['Precipitacao_media_anual'] = postos['Precipitacao_media_anual'].astype(str).str.replace(',', '.').astype(float)

postos['coordenadas'] = postos.apply(
    lambda row: f'POINT({row["Coordenada_X"]} {row["Coordenada_Y"]})',
    axis=1
)

postos.drop(columns=['Coordenada_Y', 'Coordenada_X'], errors='ignore', inplace=True)

postos.rename(columns={
    'ID': 'id_posto',
    'Dias_dados_medidos': 'numero_dias_medidos',
    'Dias_falhos': 'numero_dias_falhos',
    'Numero_meses_completos': 'numero_meses_medidos',
    'Numero_meses_falha': 'numero_meses_falhos',
    'Numero_anos_falha': 'numero_anos_falha',
    'Numero_anos_completos': 'numero_anos_medidos'
}, inplace=True)
# Exibir as primeiras 5 linhas para verificação

postos.drop(columns=['cod_ibge'], inplace=True)
postos.drop(columns=['Nome_Municipio'], inplace=True)

# === 5. Processar tabela 'registro_mensal' ===
registros = df[['Total', 'Meses', 'Anos', 'ID']].rename(columns={
    'Total': 'total_mes',
    'Meses': 'mes',
    'Anos': 'ano',
    'ID': 'id_posto'
})
registros.insert(0, 'id', range(len(registros)))

# === 6. Processar tabela 'registro_diario' ===
df_registro_diario = pd.read_csv('./data/registro_diario.csv', encoding='utf-8')
df_registro_diario = df_registro_diario[['id','id_posto', 'data', 'valor']]

# Converte 'data' para datetime e remove linhas com erros
df_registro_diario['data'] = pd.to_datetime(df_registro_diario['data'], errors='coerce')

df_registro_diario['data'] = df_registro_diario['data'].dt.strftime('%Y-%m-%d')

print(df_registro_diario['data'].head())

print(df_registro_diario['data'].dtype)

print(df_registro_diario.info())

# === 7. Inserção no Supabase (em lotes) ===

batch_size = 5000

def insert_batch(table_name, data):
    print(f"Inserindo dados em {table_name}...")
    records = data.to_dict(orient='records')
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        supabase.table(table_name).insert(batch).execute()
        print(f"Lote {i // batch_size + 1} de {len(records) // batch_size + 1}")

# Garantir lowercase nas colunas
municipios.columns = municipios.columns.str.lower()
postos.columns = postos.columns.str.lower()
registros.columns = registros.columns.str.lower()
df_registro_diario.columns = df_registro_diario.columns.str.lower()

# Inserir dados
insert_batch("municipio", municipios)
insert_batch("posto", postos)
insert_batch("registro_mensal", registros)
insert_batch("registro-diario", df_registro_diario)

print("Inserção concluída com sucesso!")
