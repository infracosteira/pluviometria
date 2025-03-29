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

df_ibge = pd.read_csv('data/municipios.csv', encoding='latin1', sep=';')
df = pd.read_csv('data/maindatabase.csv', encoding='latin1', sep=',')

municipios = df_ibge[['cod_ibge', 'municipio']].drop_duplicates().reset_index(drop=True)
municipios.insert(0, 'id', range(len(municipios)))

postos = df[['ID', 'Nome_Posto', 'Dias_dados_medidos', 'Dias_falhos', 
             'Numero_meses_completos', 'Numero_meses_falha', 'Numero_anos_falha', 
             'Numero_anos_completos', 'Precipitacao_media_anual', 'Coordenada_Y', 'Coordenada_X']].drop_duplicates()

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

registros = df[['Dia1', 'Total', 'Meses', 'Anos', 'ID']].rename(columns={
    'Dia1': 'dia',
    'Total': 'total_dia',
    'Meses': 'mes',
    'Anos': 'ano',
    'ID': 'id_posto'
})

registros.insert(0, 'id', range(len(registros)))

municipios.columns = municipios.columns.str.lower()
postos.columns = postos.columns.str.lower()
registros.columns = registros.columns.str.lower()

batch_size = 5000 

def insert_batch(table_name, data):
    """ Insere os dados em lotes para evitar sobrecarga """
    test_data = data.to_dict(orient='records')
    for i in range(0, len(test_data), batch_size):
        batch = test_data[i:i + batch_size]
        supabase.table(table_name).insert(batch).execute()
        print(f"Inserindo lote na tabela {table_name}... Parte {i//batch_size + 1}")

# Enviar os dados para cada tabela

insert_batch("municipio", municipios)

insert_batch("posto", postos)

insert_batch("registro", registros)

print("Inserção concluída com sucesso!")
