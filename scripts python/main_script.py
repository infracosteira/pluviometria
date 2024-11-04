import zipfile as zipfile
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
                for_concat.append(df)

# Exclude empty or all-NA entries before concatenation
for_concat = [
    df for df in for_concat if not df.empty and not df.isna().all().all()
]

registros_chuvas = pd.concat(for_concat)
registros_chuvas.fillna(0, inplace=True)
registros_chuvas.reset_index(drop=True, inplace=True)

print("\nFiltrando anos completos...")

#pegar apenas os anos completos
registros_chuvas['Anos'] = registros_chuvas['Anos'].astype(int)
registros_chuvas['Meses'] = registros_chuvas['Meses'].astype(int)
ano = dt.datetime.now().year
anos_completos = registros_chuvas
anos_completos = anos_completos.loc[anos_completos['Anos'] < ano]

print("\nVerificando o primeiro e o ultimo ano de registro de cada posto...")

#verificar qual o primeiro ano de registro e o ultimo ano de registro de cada posto
primeiro_e_ultimo_ano = anos_completos.groupby(['Municipios', 'Postos'
                                                ])['Anos'].agg(['min', 'max'])
primeiro_e_ultimo_ano.columns = ['Ano_inicial', 'Ano_final']
anos_completos = anos_completos.merge(primeiro_e_ultimo_ano,
                                      on=['Municipios', 'Postos'])

print("\nVerificando o primeiro mes de registro...")

#encontrar qual foi o primeiro mes registrado para cada posto no ano inicial
ano_inicial_df = anos_completos[anos_completos['Anos'] ==
                                anos_completos['Ano_inicial']]
primeiro_mes_ano_inicial = ano_inicial_df.groupby(
    ['Municipios', 'Postos'])['Meses'].min().reset_index()
primeiro_mes_ano_inicial.rename(columns={'Meses': 'Primeiro_mes'},
                                inplace=True)
anos_completos = anos_completos.merge(primeiro_mes_ano_inicial,
                                      on=['Municipios', 'Postos'],
                                      how='left')
ano_final_df = anos_completos[anos_completos['Anos'] ==
                              anos_completos['Ano_final']]

print("\nVerificando o ultimo mes de registro...")

ano_final_df = anos_completos[anos_completos['Anos'] ==
                              anos_completos['Ano_final']]
ultimo_mes_ano_final = ano_final_df.groupby(['Municipios', 'Postos'
                                             ])['Meses'].max().reset_index()
ultimo_mes_ano_final.rename(columns={'Meses': 'Ultimo_mes'}, inplace=True)

# preencher o dataframe com os meses e anos de falha
print("\nPreenchedo meses e anos faltantes com falhas...")


def criar_mes_falha(ano, mes, posto, municipio, latitude, longitude):
    dias_no_mes = {
        1: 31,
        2: 29,
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31
    }
    data = {
        'Municipios': [municipio],
        'Postos': [posto],
        'Latitude': [latitude],
        'Longitude': [longitude],
        'Anos': [ano],
        'Meses': [mes],
        'Total': [999.0],
        **{
            col: [999.0 if i < dias_no_mes[mes] else 888.0]
            for i, col in enumerate(dias_cols, start=1)
        },
    }
    return pd.DataFrame(data)


def criar_ano_falha(ano, posto, municipio, latitude, longitude):
    falhas = []
    for mes in range(1, 13):
        falhas.append(
            criar_mes_falha(ano, mes, posto, municipio, latitude, longitude))
    return pd.concat(falhas, ignore_index=True)


anos_unicos = anos_completos['Anos'].unique()
postos_unicos = anos_completos['Postos'].unique()
dias_cols = [f'Dia{i}' for i in range(1, 32)]
falhas = []
falhas_anos = []

for posto in postos_unicos:

    df_posto = anos_completos[anos_completos['Postos'] == posto]
    anos_registrados = df_posto['Anos'].unique()
    anos_faltantes = set(range(anos_registrados.min(),
                               2024)) - set(anos_registrados)

    for ano in anos_unicos:

        df_ano_posto = df_posto[df_posto['Anos'] == ano]

        if not df_ano_posto.empty:
            meses_registrados = df_ano_posto['Meses'].unique()
            meses_faltantes = set(range(1, 13)) - set(meses_registrados)

            if meses_faltantes:

                municipio = df_ano_posto['Municipios'].iloc[0]
                latitude = df_ano_posto['Latitude'].iloc[0]
                longitude = df_ano_posto['Longitude'].iloc[0]

                falhas.extend([
                    criar_mes_falha(ano, mes, posto, municipio, latitude,
                                    longitude) for mes in meses_faltantes
                ])
    if anos_faltantes:
        municipio = df_posto['Municipios'].iloc[0]
        latitude = df_posto['Latitude'].iloc[0]
        longitude = df_posto['Longitude'].iloc[0]

        for ano_faltante in anos_faltantes:
            falhas_anos.append(
                criar_ano_falha(ano_faltante, posto, municipio, latitude,
                                longitude))

if falhas:
    df_falhas = pd.concat(falhas, ignore_index=True)
    anos_completos = pd.concat([anos_completos, df_falhas], ignore_index=True)

print("Meses faltantes preenchidos com falhas.")

if falhas_anos:
    df_falhas_anos = pd.concat(falhas_anos, ignore_index=True)
    anos_completos = pd.concat([anos_completos, df_falhas_anos],
                               ignore_index=True)

anos_completos.sort_values(by=['Postos', 'Anos', 'Meses'], inplace=True)
anos_completos.reset_index(drop=True, inplace=True)

print(
    "\nRepreenchendo os novos registros com os meses e anos de primeiro registro"
)

primeiro_e_ultimo_ano = anos_completos.groupby(['Municipios', 'Postos'
                                                ])['Anos'].agg(['min', 'max'])
primeiro_e_ultimo_ano.columns = ['Ano_inicial', 'Ano_final']
anos_completos = anos_completos.merge(primeiro_e_ultimo_ano,
                                      on=['Municipios', 'Postos'])
anos_completos.drop(columns=['Ano_inicial_x', 'Ano_final_x'], inplace=True)

anos_completos = anos_completos.merge(primeiro_mes_ano_inicial,
                                      on=['Municipios', 'Postos'],
                                      how='left')
anos_completos = anos_completos.merge(ultimo_mes_ano_final,
                                      on=['Municipios', 'Postos'],
                                      how='left')
anos_completos.drop(columns=['Primeiro_mes_x'], inplace=True)
anos_completos.rename(columns={
    'Ano_inicial_y': 'Ano_inicial',
    'Ano_final_y': 'Ano_final',
    'Primeiro_mes_y': 'Primeiro_mes'
},
                      inplace=True)

print("\nVerificando quantos meses de falha existem parada cada posto")

df_sem_extras = anos_completos.drop(
    columns=['Primeiro_mes', 'Ultimo_mes', 'Ano_inicial', 'Ano_final'])

# Substituir os valores 888.0 por NaN e depois remover essas colunas
df_sem_extras.replace(888.0, pd.NA, inplace=True)
df_sem_extras.dropna(axis=1, how='all', inplace=True)

# Gerar arquivos CSV para cada posto usando o novo DataFrame
# Ensure the directory exists
output_dir = "./data/postos_solo"
os.makedirs(output_dir, exist_ok=True)

for posto in postos_unicos:
    registros_posto = df_sem_extras[df_sem_extras['Postos'] == posto]
    nome_arquivo = os.path.join(output_dir, f"{posto}.csv")
    registros_posto.to_csv(nome_arquivo, index=False, decimal=',')

print("\nArquivos CSV gerados para cada posto na pasta 'postos_solo'.")

dias_cols = [f'Dia{i}' for i in range(1, 32)]


def verificar_meses_falha(df):

    df['Mes_falha'] = df[dias_cols].apply(lambda row: any(day == 999.0
                                                          for day in row),
                                          axis=1)

    meses_falha_por_posto = df.groupby('Postos')['Mes_falha'].sum()

    return meses_falha_por_posto


meses_falha_por_posto = verificar_meses_falha(anos_completos)
meses_falha_por_posto
anos_completos = anos_completos.merge(
    meses_falha_por_posto.rename('Meses_de_Falha'), on='Postos', how='left')
anos_completos = anos_completos.drop(columns=['Mes_falha'])

print("\nCalculando intervalo de dias,meses e anos totais de falhas por posto...")

from datetime import datetime

def calcular_intervalo_dias(row):
    data_inicial = datetime(row['Ano_inicial'], 1, 1)
    data_final = datetime(row['Ano_final'], 12, 31)
    intervalo = (data_final - data_inicial).days + 1

    for year in range(row['Ano_inicial'], row['Ano_final'] + 1):
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            if year == row['Ano_inicial'] and data_inicial.month > 2:
                continue
            if year == row['Ano_final'] and data_final.month < 2:
                continue
            intervalo += 1

    return intervalo


def contar_dias_falha(row):
    return sum(row[dia] == 999.0 for dia in dias_cols)


anos_completos['Intervalo_dias'] = anos_completos.apply(
    calcular_intervalo_dias, axis=1)
anos_completos['Dias_de_Falha'] = anos_completos.apply(contar_dias_falha,
                                                       axis=1)
total_falhas_por_posto = anos_completos.groupby(
    'Postos')['Dias_de_Falha'].sum().reset_index()
total_falhas_por_posto.rename(columns={'Dias_de_Falha': 'Total_Falhas'},
                              inplace=True)
anos_completos = anos_completos.merge(total_falhas_por_posto,
                                      on='Postos',
                                      how='left')
anos_completos['Intervalo_anos'] = (
    1 + anos_completos['Ano_final']) - anos_completos['Ano_inicial']
anos_completos['Intervalo_meses'] = anos_completos['Intervalo_anos'] * 12

anos_completos.drop(columns=['Dias_de_Falha'], inplace=True)

anos_completos['dias_medidos'] = anos_completos[
    'Intervalo_dias'] - anos_completos['Total_Falhas']

print("\nCalculando a porcentagem de dias de falhas por posto...")

anos_completos['Porcentagem_dias_Falhas'] = (
    anos_completos['Total_Falhas'] / anos_completos['Intervalo_dias']) * 100
anos_completos['Porcentagem_dias_Falhas'] = anos_completos[
    'Porcentagem_dias_Falhas'].round(2)

print("\nVerificando anos de falha por posto...")

#Verificar quantos anos com falha tiveram no intervalo por posto


def contar_anos_falha(df):

    df['Ano_com_falha'] = df[dias_cols].apply(lambda row: any(day == 999.0
                                                              for day in row),
                                              axis=1)

    anos_falha = df.groupby(['Postos',
                             'Anos'])['Ano_com_falha'].any().reset_index()

    anos_falha_por_posto = anos_falha.groupby(
        'Postos')['Ano_com_falha'].sum().reset_index()
    anos_falha_por_posto.rename(columns={'Ano_com_falha': 'Anos_de_Falha'},
                                inplace=True)

    return anos_falha_por_posto


anos_falha_por_posto = contar_anos_falha(anos_completos)
anos_completos = anos_completos.merge(anos_falha_por_posto,
                                      on='Postos',
                                      how='left')
anos_completos.drop(columns=['Ano_com_falha'], inplace=True)

print("\nCalculando anos completos medidos por posto...")

# Agrupar por Município, Posto, Latitude e Longitude para garantir que os dados são do mesmo posto no mesmo município
anos_completos['anos_completos_medidos'] = anos_completos.groupby([
    'Municipios', 'Postos', 'Latitude', 'Longitude'
])['Intervalo_anos'].transform('first') - anos_completos.groupby([
    'Municipios', 'Postos', 'Latitude', 'Longitude'
])['Anos_de_Falha'].transform('first')

anos_completos['Porcentagem_anos_Falhas'] = (
    anos_completos['Anos_de_Falha'] / anos_completos['Intervalo_anos']) * 100
anos_completos['Porcentagem_anos_Falhas'] = anos_completos[
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

df_dados_validos = dados_validos(anos_completos)

# Calcular a média mensal de chuvas por posto
postos_unicos = df_dados_validos['Postos'].unique()

medias_mensais = []

for posto in postos_unicos:
    df_posto = df_dados_validos[df_dados_validos['Postos'] == posto]
    
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
        'Posto': posto,
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
anos_completos = anos_completos.merge(df_medias_mensais, left_on='Postos', right_on='Posto', how='left')
anos_completos.drop(columns=['Posto'], inplace=True)
medias_cols = ['Media_Jan', 'Media_Fev', 'Media_Mar', 'Media_Apr', 'Media_May', 'Media_Jun', 'Media_Jul', 'Media_Aug', 'Media_Sep', 'Media_Oct', 'Media_Nov', 'Media_Dec']
anos_completos[medias_cols] = anos_completos[medias_cols].fillna(999)

print("\nCalculando a média anual de chuvas por posto...")

postos_unicos = anos_completos['Postos'].unique()

anos_completos['Media_Anual'] = 0.0

for posto in postos_unicos:
    df_posto = anos_completos[anos_completos['Postos'] == posto]
    intervalo_anos = df_posto['Intervalo_anos'].iloc[0]
    
    if (df_posto[['Media_Jan', 'Media_Fev', 'Media_Mar', 'Media_Apr', 'Media_May', 'Media_Jun', 'Media_Jul', 'Media_Aug', 'Media_Sep', 'Media_Oct', 'Media_Nov', 'Media_Dec']] == 999).all(axis=None):
        media_anual = 999
    else:
        soma_total_chuvas = df_posto[df_posto['Total'] != 999].groupby('Anos')['Total'].sum().sum()
        media_anual = soma_total_chuvas / intervalo_anos

    anos_completos.loc[anos_completos['Postos'] == posto, 'Media_Anual'] = media_anual

anos_completos['Total_meses_intervalo'] = anos_completos['Intervalo_anos'] * 12

if 'Intervalo_meses' in anos_completos.columns:
    anos_completos.drop(columns=['Intervalo_meses'], inplace=True)

anos_completos['Numero_meses_completos'] = anos_completos['Total_meses_intervalo'] - anos_completos['Meses_de_Falha']

def calcular_percentual_meses_falha(df):
    df['Percentual_meses_falha'] = (df['Meses_de_Falha'] / df['Total_meses_intervalo']) * 100
    df['Percentual_meses_falha'] = df['Percentual_meses_falha'].round(2)
    return df

anos_completos = calcular_percentual_meses_falha(anos_completos)


# Selecionar as colunas necessárias e renomeá-las conforme o formato desejado
colunas_resumo = [
    'Postos', 'Municipios', 'Latitude', 'Longitude', 'Ano_inicial', 'Ano_final',
    'Primeiro_mes', 'Ultimo_mes', 'Intervalo_dias', 'dias_medidos', 'Total_Falhas',
    'Porcentagem_dias_Falhas', 'Total_meses_intervalo', 'Numero_meses_completos',
    'Meses_de_Falha', 'Percentual_meses_falha', 'Intervalo_anos', 'anos_completos_medidos',
    'Anos_de_Falha', 'Porcentagem_anos_Falhas', 'Media_Anual', 'Media_Jan', 'Media_Fev',
    'Media_Mar', 'Media_Apr', 'Media_May', 'Media_Jun', 'Media_Jul', 'Media_Aug',
    'Media_Sep', 'Media_Oct', 'Media_Nov', 'Media_Dec'
]

df_resumo = anos_completos[colunas_resumo].drop_duplicates(subset=['Postos'])
df_resumo.insert(0, 'Chave_ID', df_resumo.index + 1)

# Renomear as colunas conforme o formato desejado
df_resumo.rename(columns={
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
    'anos_completos_medidos': 'Numero_anos_completos',
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

# Arredondar todas as médias e percentuais para 2 casas decimais
colunas_arredondar = [
    'Precipitacao_media_anual', 'Mes_Jan', 'Mes_Fev', 'Mes_Mar', 'Mes_Apr', 'Mes_May',
    'Mes_Jun', 'Mes_Jul', 'Mes_Aug', 'Mes_Sep', 'Mes_Oct', 'Mes_Nov', 'Mes_Dec',
    'Percentual_dias_falhos', 'Percentual_meses_falha', 'Percentual_anos_falha'
]
df_resumo[colunas_arredondar] = df_resumo[colunas_arredondar].round(2)

# Salvar o dataframe em um arquivo CSV
df_resumo.to_csv('./data/resumo_postos_individual.csv', index=False, decimal=',')

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

# Adicionar a coluna 'id' ao dataframe
df_resumo.insert(0, 'id', range(1, len(df_resumo) + 1))

# Converter o dataframe para uma lista de dicionários
dados_formatados_resumo = df_resumo.to_dict(orient='records')

# Salvar a lista de dicionários em um arquivo JSON
with open('../data/dados_formatados_resumo.json', 'w') as f:
    json.dump(dados_formatados_resumo, f, ensure_ascii=False, indent=4)

print("Arquivo JSON gerado com sucesso.")