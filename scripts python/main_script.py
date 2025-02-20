import zipfile
import pandas as pd
import datetime as dt
import os
import unicodedata
import json

print("\nLendo dados das estações pluviometricas...")

for_concat = []
with zipfile.ZipFile('./data/postos.zip', 'r') as t:
    for arq in t.namelist():
        if arq.endswith('.txt'):
            with t.open(arq) as f:
                df = pd.read_csv(f, delimiter=';')
                # Extrair o ID do nome do arquivo e adicionar como uma nova coluna
                df['id'] = arq.split('.')[0]
                for_concat.append(df)

# Exclude empty or all-NA entries before concatenation
for_concat = [
    df for df in for_concat if not df.empty and not df.isna().all().all()
]

registros_chuvas = pd.concat(for_concat)
registros_chuvas.fillna(0, inplace=True)
registros_chuvas.reset_index(drop=True, inplace=True)

# Reordenar as colunas para que 'id' seja a primeira
cols = ['id'] + [col for col in registros_chuvas.columns if col != 'id']
registros_chuvas = registros_chuvas[cols]

print("\nFiltrando anos completos...")

#pegar apenas os anos completos
registros_chuvas['Anos'] = registros_chuvas['Anos'].astype(int)
registros_chuvas['Meses'] = registros_chuvas['Meses'].astype(int)
ano = dt.datetime.now().year
Anos_completos = registros_chuvas[registros_chuvas['Anos'] < ano]

print("\nVerificando o primeiro e o ultimo ano de registro de cada posto...")

# Verificar qual o primeiro ano de registro e o ultimo ano de registro de cada posto
primeiro_e_ultimo_ano = Anos_completos.groupby('id')['Anos'].agg(['min', 'max']).rename(columns={'min': 'Ano_inicial', 'max': 'Ano_final'})
Anos_completos = Anos_completos.merge(primeiro_e_ultimo_ano, on='id')

# Encontrar qual foi o primeiro mês registrado para cada posto no ano inicial
primeiro_mes_ano_inicial = Anos_completos[Anos_completos['Anos'] == Anos_completos['Ano_inicial']].groupby('id')['Meses'].min().reset_index().rename(columns={'Meses': 'Primeiro_mes'})
Anos_completos = Anos_completos.merge(primeiro_mes_ano_inicial, on='id', how='left')

# Encontrar qual foi o último mês registrado para cada posto no ano final
ultimo_mes_ano_final = Anos_completos[Anos_completos['Anos'] == Anos_completos['Ano_final']].groupby('id')['Meses'].max().reset_index().rename(columns={'Meses': 'Ultimo_mes'})


from datetime import datetime


def preencher_anos_faltantes(df):
    postos_unicos = df[['id', 'Postos', 'Municipios']].drop_duplicates()
    anos_faltantes = []
    ano_atual = datetime.now().year  # Obtém o ano atual

    for _, row in postos_unicos.iterrows():
        posto_id = row['id']
        posto = row['Postos']
        municipio = row['Municipios']

        # Seleciona apenas os registros do posto específico
        df_posto = df[(df['id'] == posto_id) & (df['Postos'] == posto) & (df['Municipios'] == municipio)]
        
        # Identifica o primeiro ano registrado, preenchendo se for NaN
        if df_posto['Anos'].notna().any():
            ano_inicial = int(df_posto['Anos'].min())
        else:
            print(f"Aviso: Nenhum ano encontrado para o posto ID {posto_id} - {posto}, município {municipio}. Preenchendo com 999.")
            ano_inicial = ano_atual  # Usar o ano atual como referência mínima
        
        # Determina o intervalo de anos
        anos_completos = set(range(ano_inicial, ano_atual))
        anos_registrados = set(df_posto['Anos'].dropna().unique())
        
        # Determina os anos que estão faltando
        anos_faltantes_posto = anos_completos - anos_registrados

        # Preenche os anos faltantes com os meses e dias como 999.0
        for ano in anos_faltantes_posto:
            for mes in range(1, 13):
                falha = {
                    'id': posto_id,
                    'Municipios': municipio,
                    'Postos': posto,
                    'Latitude': df_posto['Latitude'].iloc[0] if not df_posto.empty else 999.0,
                    'Longitude': df_posto['Longitude'].iloc[0] if not df_posto.empty else 999.0,
                    'Anos': ano,
                    'Meses': mes,
                    'Total': 999.0,
                    **{f'Dia{i}': 999.0 for i in range(1, 32)}
                }
                anos_faltantes.append(falha)

    # Cria um DataFrame com os anos faltantes e concatena ao original
    df_faltantes = pd.DataFrame(anos_faltantes)
    df = pd.concat([df, df_faltantes], ignore_index=True)
    df.sort_values(by=['id', 'Postos', 'Municipios', 'Anos', 'Meses'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def preencher_meses_faltantes(df):
    postos_unicos = df[['id', 'Postos', 'Municipios']].drop_duplicates()
    meses_faltantes = []

    for _, row in postos_unicos.iterrows():
        posto_id = row['id']
        posto = row['Postos']
        municipio = row['Municipios']

        # Seleciona apenas os registros do posto específico
        df_posto = df[(df['id'] == posto_id) & (df['Postos'] == posto) & (df['Municipios'] == municipio)]
        
        anos_registrados = df_posto['Anos'].dropna().unique()

        for ano in anos_registrados:
            df_ano = df_posto[df_posto['Anos'] == ano]
            meses_registrados = set(df_ano['Meses'].dropna().unique())
            meses_completos = set(range(1, 13))
            
            # Determina os meses que estão faltando no ano
            meses_faltantes_ano = meses_completos - meses_registrados

            for mes in meses_faltantes_ano:
                falha = {
                    'id': posto_id,
                    'Municipios': municipio,
                    'Postos': posto,
                    'Latitude': df_posto['Latitude'].iloc[0] if not df_posto.empty else 999.0,
                    'Longitude': df_posto['Longitude'].iloc[0] if not df_posto.empty else 999.0,
                    'Anos': ano,
                    'Meses': mes,
                    'Total': 999.0,
                    **{f'Dia{i}': 999.0 for i in range(1, 32)}
                }
                meses_faltantes.append(falha)

    # Cria um DataFrame com os meses faltantes e concatena ao original
    df_faltantes = pd.DataFrame(meses_faltantes)
    df = pd.concat([df, df_faltantes], ignore_index=True)
    df.sort_values(by=['id', 'Postos', 'Municipios', 'Anos', 'Meses'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

# Preencher anos e meses faltantes
Anos_completos = preencher_anos_faltantes(Anos_completos)
Anos_completos = preencher_meses_faltantes(Anos_completos)

# Converter colunas numéricas de string para float
numeric_cols = ['Total'] + [f'Dia{i}' for i in range(1, 32)]
for col in numeric_cols:
    Anos_completos[col] = Anos_completos[col].astype(str).str.replace(',', '.').astype(float)

output_dir = "../data/postos_solo"
os.makedirs(output_dir, exist_ok=True)

def remover_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

for posto_id in Anos_completos['id'].unique():
    registros_posto = Anos_completos[Anos_completos['id'] == posto_id]
    nome_posto = registros_posto['Postos'].iloc[0].replace(' ', '_')
    nome_posto = remover_acentos(nome_posto)  # Remover acentos
    nome_arquivo = os.path.join(output_dir, f"{posto_id}_{nome_posto}.csv")
    registros_posto.to_csv(nome_arquivo, index=False, decimal=',')

print("\nArquivos CSV gerados para cada posto na pasta 'postos_solo'.")

print("\nRepreenchendo os novos registros com os meses e anos de primeiro registro")

primeiro_e_ultimo_ano = Anos_completos.groupby('id')['Anos'].agg(['min', 'max']).rename(columns={'min': 'Ano_inicial', 'max': 'Ano_final'})
Anos_completos = Anos_completos.merge(primeiro_e_ultimo_ano, on='id')

Anos_completos = Anos_completos.merge(primeiro_mes_ano_inicial, on='id', how='left')
Anos_completos = Anos_completos.merge(ultimo_mes_ano_final, on='id', how='left')

Anos_completos.rename(columns={
    'Ano_inicial_y': 'Ano_inicial',
    'Ano_final_y': 'Ano_final',
    'Primeiro_mes_y': 'Primeiro_mes'
}, inplace=True)


print("\nVerificando quantos meses de falha existem parada cada posto")

df_sem_extras = Anos_completos.drop(
    columns=['Primeiro_mes', 'Ultimo_mes', 'Ano_inicial', 'Ano_final'])

# Substituir os valores 888.0 por NaN e depois remover essas colunas
df_sem_extras.replace(888.0, pd.NA, inplace=True)
df_sem_extras.dropna(axis=1, how='all', inplace=True)


print("\nVerificando quantos meses de falha existem para cada posto")
dias_cols = [f'Dia{i}' for i in range(1, 32)]

def verificar_meses_falha(df):
    df['Mes_falha'] = df[dias_cols].apply(lambda row: any(day == 999.0 for day in row), axis=1)
    meses_falha_por_posto = df.groupby('id')['Mes_falha'].sum()
    return meses_falha_por_posto

meses_falha_por_posto = verificar_meses_falha(Anos_completos)
Anos_completos = Anos_completos.merge(meses_falha_por_posto.rename('Meses_de_Falha'), on='id', how='left')
Anos_completos = Anos_completos.drop(columns=['Mes_falha'])

print(
    "\nCalculando intervalo de dias, meses e anos totais de falhas por posto..."
)

from datetime import datetime

def calcular_intervalo_dias(row):
    ano_inicial = int(row['Ano_inicial'])
    ano_final = int(row['Ano_final'])
    data_inicial = datetime(ano_inicial, 1, 1)
    data_final = datetime(ano_final, 12, 31)

    intervalo = (data_final - data_inicial).days + 1
    
    for year in range(ano_inicial, ano_final + 1):
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            if year == ano_inicial and data_inicial.month > 2:
                continue
            if year == ano_final and data_final.month < 2:
                continue
            intervalo += 1

    return intervalo

def contar_dias_falha(row):
    return sum(row[dia] == 999.0 for dia in dias_cols)

Anos_completos['Ano_inicial'] = Anos_completos['Ano_inicial'].astype(int)
Anos_completos['Ano_final'] = Anos_completos['Ano_final'].astype(int)

Anos_completos['Intervalo_dias'] = Anos_completos.apply(calcular_intervalo_dias, axis=1)
Anos_completos['Dias_de_Falha'] = Anos_completos.apply(contar_dias_falha, axis=1)

total_falhas_por_posto = Anos_completos.groupby('id')['Dias_de_Falha'].sum().reset_index()
total_falhas_por_posto.rename(columns={'Dias_de_Falha': 'Total_Falhas'}, inplace=True)

Anos_completos = Anos_completos.merge(total_falhas_por_posto, on='id', how='left')
Anos_completos['Intervalo_anos'] = (Anos_completos['Ano_final'].astype(int) - Anos_completos['Ano_inicial'].astype(int)) + 1
Anos_completos['Intervalo_meses'] = Anos_completos['Intervalo_anos'] * 12

Anos_completos.drop(columns=['Dias_de_Falha'], inplace=True)
Anos_completos['dias_medidos'] = Anos_completos['Intervalo_dias'] - Anos_completos['Total_Falhas']


print("\nCalculando a porcentagem de dias de falhas por posto...")

Anos_completos['Porcentagem_dias_Falhas'] = (
    Anos_completos['Total_Falhas'] / Anos_completos['Intervalo_dias']) * 100
Anos_completos['Porcentagem_dias_Falhas'] = Anos_completos[
    'Porcentagem_dias_Falhas'].round(2)

print("\nVerificando anos de falha por posto...")

# Verificar quantos anos com falha tiveram no intervalo por posto
def contar_anos_falha(df):
    df['Ano_com_falha'] = df[dias_cols].apply(lambda row: any(day == 999.0 for day in row), axis=1)
    anos_falha = df.groupby(['id', 'Anos'])['Ano_com_falha'].any().reset_index()
    anos_falha_por_posto = anos_falha.groupby('id')['Ano_com_falha'].sum().reset_index()
    anos_falha_por_posto.rename(columns={'Ano_com_falha': 'Anos_de_Falha'}, inplace=True)
    return anos_falha_por_posto

anos_falha_por_posto = contar_anos_falha(Anos_completos)
Anos_completos = Anos_completos.merge(anos_falha_por_posto, on='id', how='left')
Anos_completos.drop(columns=['Ano_com_falha'], inplace=True)

print("\nCalculando anos completos medidos por posto...")

# Agrupar por id para garantir que os dados são do mesmo posto
Anos_completos['Anos_completos_medidos'] = Anos_completos.groupby('id')['Intervalo_anos'].transform('first') - Anos_completos.groupby('id')['Anos_de_Falha'].transform('first')

Anos_completos['Porcentagem_anos_Falhas'] = (
    Anos_completos['Anos_de_Falha'] / Anos_completos['Intervalo_anos']) * 100
Anos_completos['Porcentagem_anos_Falhas'] = Anos_completos[
    'Porcentagem_anos_Falhas'].round(2)

print("\nCalculando a média mensal de chuvas por posto...")

def dados_validos(df):
    # Verificar se todos os dias do mês não são 999.0
    df['Mes_valido'] = df[dias_cols].apply(lambda row: all(day != 999.0 for day in row), axis=1)
    
    # Filtrar apenas os meses válidos
    df_validos = df[df['Mes_valido']].copy()
    
    # Remover a coluna auxiliar 'Mes_valido'
    df_validos.drop(columns=['Mes_valido'], inplace=True)
    
    return df_validos

df_dados_validos = dados_validos(Anos_completos)

# Calcular a média mensal de chuvas por posto
ids_unicos = df_dados_validos['id'].unique()

medias_mensais = []

for posto_id in ids_unicos:
    df_posto = df_dados_validos[df_dados_validos['id'] == posto_id]
    
    # Inicializar variáveis para somar os totais e contadores para cada mês
    jan_total = fev_total = mar_total = apr_total = may_total = jun_total = 0
    jul_total = aug_total = sep_total = oct_total = nov_total = dec_total = 0
    
    jan_count = fev_count = mar_count = apr_count = may_count = jun_count = 0
    jul_count = aug_count = sep_count = oct_count = nov_count = dec_count = 0
    
    for _, row in df_posto.iterrows():
        if row['Meses'] == 1:
            jan_total += row['Total']
            jan_count += 1
        elif row['Meses'] == 2:
            fev_total += row['Total']
            fev_count += 1
        elif row['Meses'] == 3:
            mar_total += row['Total']
            mar_count += 1
        elif row['Meses'] == 4:
            apr_total += row['Total']
            apr_count += 1
        elif row['Meses'] == 5:
            may_total += row['Total']
            may_count += 1
        elif row['Meses'] == 6:
            jun_total += row['Total']
            jun_count += 1
        elif row['Meses'] == 7:
            jul_total += row['Total']
            jul_count += 1
        elif row['Meses'] == 8:
            aug_total += row['Total']
            aug_count += 1
        elif row['Meses'] == 9:
            sep_total += row['Total']
            sep_count += 1
        elif row['Meses'] == 10:
            oct_total += row['Total']
            oct_count += 1
        elif row['Meses'] == 11:
            nov_total += row['Total']
            nov_count += 1
        elif row['Meses'] == 12:
            dec_total += row['Total']
            dec_count += 1
    
    medias_mensais.append({
        'id': posto_id,
        'Media_Jan': jan_total / jan_count if jan_count else 999,
        'Media_Fev': fev_total / fev_count if fev_count else 999,
        'Media_Mar': mar_total / mar_count if mar_count else 999,
        'Media_Apr': apr_total / apr_count if apr_count else 999,
        'Media_May': may_total / may_count if may_count else 999,
        'Media_Jun': jun_total / jun_count if jun_count else 999,
        'Media_Jul': jul_total / jul_count if jul_count else 999,
        'Media_Aug': aug_total / aug_count if aug_count else 999,
        'Media_Sep': sep_total / sep_count if sep_count else 999,
        'Media_Oct': oct_total / oct_count if oct_count else 999,
        'Media_Nov': nov_total / nov_count if nov_count else 999,
        'Media_Dec': dec_total / dec_count if dec_count else 999
    })

df_medias_mensais = pd.DataFrame(medias_mensais)
Anos_completos = Anos_completos.merge(df_medias_mensais, on='id', how='left')
# Preencher médias vazias com 999

medias_cols = ['Media_Jan', 'Media_Fev', 'Media_Mar', 'Media_Apr', 'Media_May', 'Media_Jun', 'Media_Jul', 'Media_Aug', 'Media_Sep', 'Media_Oct', 'Media_Nov', 'Media_Dec']
Anos_completos[medias_cols] = Anos_completos[medias_cols].fillna(999)

print("\nCalculando a média anual de chuvas por posto...")

postos_unicos = Anos_completos['id'].unique()

Anos_completos['Media_Anual'] = 0.0

for posto_id in postos_unicos:
    df_posto = Anos_completos[Anos_completos['id'] == posto_id]
    intervalo_anos = df_posto['Intervalo_anos'].iloc[0]

    # Check if all monthly averages are 999
    if (df_posto[['Media_Jan', 'Media_Fev', 'Media_Mar', 'Media_Apr', 'Media_May', 'Media_Jun', 'Media_Jul', 'Media_Aug', 'Media_Sep', 'Media_Oct', 'Media_Nov', 'Media_Dec']] == 999).all(axis=None):
        media_anual = 999
    else:
        soma_total_chuvas = df_posto[df_posto['Total'] != 999].groupby('Anos')['Total'].sum().sum()
        media_anual = soma_total_chuvas / intervalo_anos

    Anos_completos.loc[Anos_completos['id'] == posto_id, 'Media_Anual'] = media_anual

Anos_completos['Total_meses_intervalo'] = Anos_completos['Intervalo_anos'] * 12

if 'Intervalo_meses' in Anos_completos.columns:
    Anos_completos.drop(columns=['Intervalo_meses'], inplace=True)

Anos_completos['Numero_meses_completos'] = Anos_completos['Total_meses_intervalo'] - Anos_completos['Meses_de_Falha']

def calcular_percentual_meses_falha(df):
    df['Percentual_meses_falha'] = (df['Meses_de_Falha'] / df['Total_meses_intervalo']) * 100
    df['Percentual_meses_falha'] = df['Percentual_meses_falha'].round(2)
    return df

Anos_completos = calcular_percentual_meses_falha(Anos_completos)

colunas_resumo1 = [
    'id','link_csv', 'Postos', 'Municipios', 'Latitude', 'Longitude', 'Ano_inicial', 'Ano_final',
    'Primeiro_mes', 'Ultimo_mes', 'Intervalo_dias', 'dias_medidos', 'Total_Falhas',
    'Porcentagem_dias_Falhas', 'Total_meses_intervalo', 'Numero_meses_completos',
    'Meses_de_Falha', 'Percentual_meses_falha', 'Intervalo_anos', 'Anos_completos_medidos',
    'Anos_de_Falha', 'Porcentagem_anos_Falhas', 'Media_Anual', 'Media_Jan', 'Media_Fev',
    'Media_Mar', 'Media_Apr', 'Media_May', 'Media_Jun', 'Media_Jul', 'Media_Aug',
    'Media_Sep', 'Media_Oct', 'Media_Nov', 'Media_Dec'
    , 'Dia1', 'Dia2', 'Dia3', 'Dia4', 'Dia5', 'Dia6', 'Dia7', 'Dia8', 'Dia9', 'Dia10', 'Dia11', 'Dia12', 'Dia13', 'Dia14', 'Dia15', 'Dia16', 'Dia17', 'Dia18', 'Dia19', 'Dia20', 'Dia21', 'Dia22', 'Dia23', 'Dia24', 'Dia25', 'Dia26', 'Dia27', 'Dia28', 'Dia29', 'Dia30', 'Dia31'
]

database = Anos_completos.copy()

database.drop(columns=['Mes_valido'], inplace=True)

database.rename(columns={
    'id': 'ID',
    'Postos': 'Nome_Posto',
    'Municipios': 'Nome_Municipio',
    'Latitude': 'Coordenada_Y',
    'Longitude': 'Coordenada_X',
    'Ano_inicial': 'Ano_Inicio',
    'Ano_final': 'Ano_Fim',
    'Primeiro_mes': 'Mes_Inicio',
    'Ultimo_mes': 'Mes_Fim',
    'Intervalo_dias': 'Total_dias_intervalo',
    'dias_medidos': 'Dias_dados_medidos',
    'Total_Falhas': 'Dias_falhos',
    'Porcentagem_dias_Falhas': 'Percentual_dias_falhos',
    'Total_meses_intervalo': 'Total_meses_intervalo',
    'Numero_meses_completos': 'Numero_meses_completos',
    'Meses_de_Falha': 'Numero_meses_falha',
    'Percentual_meses_falha': 'Percentual_meses_falha',
    'Intervalo_anos': 'Total_anos_intervalo',
    'Anos_completos_medidos': 'Numero_anos_completos',
    'Anos_de_Falha': 'Numero_anos_falha',
    'Porcentagem_anos_Falhas': 'Percentual_anos_falha',
    'Media_Anual': 'Precipitacao_media_anual',
}, inplace=True)

# Arredondar as colunas selecionadas para 2 casas decimais
colunas_para_arredondar = [col for col in database.columns if col not in ['Coordenada_X', 'Coordenada_Y']]
database[colunas_para_arredondar] = database[colunas_para_arredondar].round(2)
database['Coordenada_X'] = database['Coordenada_X'].round(8)
database['Coordenada_Y'] = database['Coordenada_Y'].round(8)

# Geração do DATAFRAME que será inserido no banco de dados
database.to_csv('../data/maindatabase.csv', index=False, decimal='.')

print ("Geração do dataframe usado na tabela no site.") 

#print(Anos_completos.columns)

colunas_resumo = [
    'id','link_csv', 'Postos', 'Municipios', 'Latitude', 'Longitude', 'Ano_inicial', 'Ano_final',
    'Primeiro_mes', 'Ultimo_mes', 'Intervalo_dias', 'dias_medidos', 'Total_Falhas',
    'Porcentagem_dias_Falhas', 'Total_meses_intervalo', 'Numero_meses_completos',
    'Meses_de_Falha', 'Percentual_meses_falha', 'Intervalo_anos', 'Anos_completos_medidos',
    'Anos_de_Falha', 'Porcentagem_anos_Falhas', 'Media_Anual', 'Media_Jan', 'Media_Fev',
    'Media_Mar', 'Media_Apr', 'Media_May', 'Media_Jun', 'Media_Jul', 'Media_Aug',
    'Media_Sep', 'Media_Oct', 'Media_Nov', 'Media_Dec'
]

links_df = pd.read_csv('./data/links.csv', header=None, names=['id', 'link_csv'], encoding='latin1')

Anos_completos['id'] = Anos_completos['id'].astype(str)

links_df['id'] = links_df['id'].astype(str)

Anos_completos = Anos_completos.merge(links_df, on='id', how='left')

df_resumo = Anos_completos[colunas_resumo].copy()

df_resumo = df_resumo.groupby('id').first().reset_index()

# Renomear as colunas conforme o formato desejado
df_resumo.rename(columns={
    'id': 'ID',
    'Postos': 'Nome_Posto',
    'Municipios': 'Nome_Municipio',
    'Latitude': 'Coordenada_Y',
    'Longitude': 'Coordenada_X',
    'Ano_inicial': 'Ano_Inicio',
    'Ano_final': 'Ano_Fim',
    'Primeiro_mes': 'Mes_Inicio',
    'Ultimo_mes': 'Mes_Fim',
    'Intervalo_dias': 'Total_dias_intervalo',
    'dias_medidos': 'Dias_dados_medidos',
    'Total_Falhas': 'Dias_falhos',
    'Porcentagem_dias_Falhas': 'Percentual_dias_falhos',
    'Total_meses_intervalo': 'Total_meses_intervalo',
    'Numero_meses_completos': 'Numero_meses_completos',
    'Meses_de_Falha': 'Numero_meses_falha',
    'Percentual_meses_falha': 'Percentual_meses_falha',
    'Intervalo_anos': 'Total_anos_intervalo',
    'Anos_completos_medidos': 'Numero_anos_completos',
    'Anos_de_Falha': 'Numero_anos_falha',
    'Porcentagem_anos_Falhas': 'Percentual_anos_falha',
    'Media_Anual': 'Precipitacao_media_anual',
    'Media_Jan': 'Mes_Jan',
    'Media_Fev': 'Mes_Fev',
    'Media_Mar': 'Mes_Mar',
    'Media_Apr': 'Mes_Apr',
    'Media_May': 'Mes_May',
    'Media_Jun': 'Mes_Jun',
    'Media_Jul': 'Mes_Jul',
    'Media_Aug': 'Mes_Aug',
    'Media_Sep': 'Mes_Sep',
    'Media_Oct': 'Mes_Oct',
    'Media_Nov': 'Mes_Nov',
    'Media_Dec': 'Mes_Dec'
}, inplace=True)

# Converter a coluna 'ID' para numérica para evitar problemas de ordenação
df_resumo['ID'] = pd.to_numeric(df_resumo['ID'], errors='coerce')

# Remover linhas com valores NaN na coluna 'ID' (se houver)
df_resumo.dropna(subset=['ID'], inplace=True)

# Ordenar com base na coluna 'ID'
df_resumo.sort_values(by='ID', inplace=True)

# Arredondar todas as médias e percentuais para 2 casas decimais
colunas_arredondar = [
    'Precipitacao_media_anual', 'Mes_Jan', 'Mes_Fev', 'Mes_Mar', 'Mes_Apr', 'Mes_May',
    'Mes_Jun', 'Mes_Jul', 'Mes_Aug', 'Mes_Sep', 'Mes_Oct', 'Mes_Nov', 'Mes_Dec',
    'Percentual_dias_falhos', 'Percentual_meses_falha', 'Percentual_anos_falha'
]
df_resumo[colunas_arredondar] = df_resumo[colunas_arredondar].round(2)

# Salvar o DataFrame em um arquivo CSV
df_resumo.to_csv('./data/resumo_postos_individual.csv', index=False, decimal=',')

# Diagnóstico para verificar duplicados ou valores nulos na coluna 'ID'
duplicados = df_resumo['ID'].duplicated().sum()
valores_nulos = df_resumo['ID'].isnull().sum()


# Converter todos os valores numéricos para strings
df_resumo = df_resumo.map(
    lambda x: str(x) if isinstance(x, (int, float)) else x)

def remover_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto)
                   if unicodedata.category(c) != 'Mn')

df_resumo = df_resumo.map(lambda x: remover_acentos(x)
                                              if isinstance(x, str) else x)

# Converter o dataframe para uma lista de dicionários
dados_formatados_resumo = df_resumo.to_dict(orient='records')

# Ler o arquivo links.csv com encoding 'latin1'
links_df = pd.read_csv('./data/links.csv', header=None, names=['link_csv'], encoding='latin1')

# Verificar se a coluna 'link_csv' existe
if 'link_csv' not in links_df.columns:
    raise ValueError("A coluna 'link_csv' não foi encontrada no arquivo links.csv")

# Verificar se o comprimento de links_df e df_resumo são iguais
if len(links_df) != len(df_resumo):
    raise ValueError(f"O comprimento de links_df ({len(links_df)}) não corresponde ao comprimento de df_resumo ({len(df_resumo)})")

# Adicionar a coluna link_csv ao dataframe df_resumo
df_resumo['link_csv'] = links_df['link_csv'].values

colunas = list(df_resumo.columns)  # Obtém a lista de colunas
colunas.insert(1, colunas.pop(colunas.index('link_csv')))  # Move 'link_csv' para a segunda posição
df_resumo = df_resumo[colunas]  # Reorganiza o DataFrame com a nova ordem de colunas

with open('./data/dados_formatados_resumo.json', 'w', encoding='utf-8') as f:
    json.dump(dados_formatados_resumo, f, ensure_ascii=False, indent=4)

print("Arquivo JSON gerado com sucesso.")