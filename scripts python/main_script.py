import zipfile as zipfile
import pandas as pd
import datetime as dt

print("\nLendo dados das estações pluviometricas...")

for_concat = []
with zipfile.ZipFile('postos.zip', 'r') as t:
    for arq in t.namelist():
        if arq.endswith('.txt'):
            with t.open(arq) as f:
                df = pd.read_csv(f, delimiter=';')
                for_concat.append(df)

# Exclude empty or all-NA entries before concatenation
for_concat = [df for df in for_concat if not df.empty and not df.isna().all().all()]

registros_chuvas = pd.concat(for_concat)
registros_chuvas.fillna(0, inplace=True)
registros_chuvas.reset_index(drop=True, inplace=True)

print("\nFiltrando anos completos...")

#pegar apenas os anos completos
registros_chuvas['Anos'] = registros_chuvas['Anos'].astype(int)
registros_chuvas['Meses'] = registros_chuvas['Meses'].astype(int)
ano = dt.datetime.now().year
Anos_completos = registros_chuvas
Anos_completos = Anos_completos.loc[Anos_completos['Anos'] < ano]

print("\nVerificando o primeiro e o ultimo ano de registro de cada posto...")

#verificar qual o primeiro ano de registro e o ultimo ano de registro de cada posto
primeiro_e_ultimo_ano = Anos_completos.groupby(['Municipios', 'Postos'
                                                ])['Anos'].agg(['min', 'max'])
primeiro_e_ultimo_ano.columns = ['Ano_inicial', 'Ano_final']
Anos_completos = Anos_completos.merge(primeiro_e_ultimo_ano,
                                      on=['Municipios', 'Postos'])

print("\nVerificando o primeiro mes de registro...")

#encontrar qual foi o primeiro mes registrado para cada posto no ano inicial
ano_inicial_df = Anos_completos[Anos_completos['Anos'] ==
                                Anos_completos['Ano_inicial']]
primeiro_mes_ano_inicial = ano_inicial_df.groupby(
    ['Municipios', 'Postos'])['Meses'].min().reset_index()
primeiro_mes_ano_inicial.rename(columns={'Meses': 'Primeiro_mes'},
                                inplace=True)
Anos_completos = Anos_completos.merge(primeiro_mes_ano_inicial,
                                      on=['Municipios', 'Postos'],
                                      how='left')
ano_final_df = Anos_completos[Anos_completos['Anos'] ==
                              Anos_completos['Ano_final']]

print("\nVerificando o ultimo mes de registro...")

ano_final_df = Anos_completos[Anos_completos['Anos'] ==
                              Anos_completos['Ano_final']]
ultimo_mes_ano_final = ano_final_df.groupby(['Municipios', 'Postos'
                                             ])['Meses'].max().reset_index()
ultimo_mes_ano_final.rename(columns={'Meses': 'Ultimo_mes'}, inplace=True)

# preencher o dataframe com os meses e anos de falha
print("\nPreenchedo meses e anos faltantes com falhas...")



def criar_mes_falha(ano, mes, posto, municipio, latitude, longitude):
    dias_no_mes = {
        1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
        7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
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

anos_unicos = Anos_completos['Anos'].unique()
postos_unicos = Anos_completos['Postos'].unique()
dias_cols = [f'Dia{i}' for i in range(1, 32)]
falhas = []
falhas_anos = []

for posto in postos_unicos:

    df_posto = Anos_completos[Anos_completos['Postos'] == posto]
    anos_registrados = df_posto['Anos'].unique()
    anos_faltantes = set(range(anos_registrados.min(), 2024)) - set(anos_registrados)

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
                    criar_mes_falha(ano, mes, posto, municipio, latitude, longitude)
                    for mes in meses_faltantes
                ])
    if anos_faltantes:
        municipio = df_posto['Municipios'].iloc[0]
        latitude = df_posto['Latitude'].iloc[0]
        longitude = df_posto['Longitude'].iloc[0]

        for ano_faltante in anos_faltantes:
            falhas_anos.append(
                criar_ano_falha(ano_faltante, posto, municipio, latitude, longitude))

if falhas:
    df_falhas = pd.concat(falhas, ignore_index=True)
    Anos_completos = pd.concat([Anos_completos, df_falhas], ignore_index=True)

print("Meses faltantes preenchidos com falhas.")

if falhas_anos:
    df_falhas_anos = pd.concat(falhas_anos, ignore_index=True)
    Anos_completos = pd.concat([Anos_completos, df_falhas_anos], ignore_index=True)

Anos_completos.sort_values(by=['Postos', 'Anos', 'Meses'], inplace=True)
Anos_completos.reset_index(drop=True, inplace=True)

print("\nAnos de falha omitidos preenchidos.")
print("\nRemovendo postos duplicados...")

# Remover duplicatas com base nas colunas 'Municipios', 'Postos', 'Anos' e 'Meses'
#Anos_completos.drop_duplicates(subset=['Municipios', 'Postos', 'Anos', 'Meses'], inplace=True)

print(
    "\nRepreenchendo os novos registros com os meses e anos de primeiro registro"
)

primeiro_e_ultimo_ano = Anos_completos.groupby(['Municipios', 'Postos'
                                                ])['Anos'].agg(['min', 'max'])
primeiro_e_ultimo_ano.columns = ['Ano_inicial', 'Ano_final']
Anos_completos = Anos_completos.merge(primeiro_e_ultimo_ano,
                                      on=['Municipios', 'Postos'])
Anos_completos.drop(columns=['Ano_inicial_x', 'Ano_final_x'], inplace=True)

Anos_completos = Anos_completos.merge(primeiro_mes_ano_inicial,
                                      on=['Municipios', 'Postos'],
                                      how='left')
Anos_completos = Anos_completos.merge(ultimo_mes_ano_final,
                                      on=['Municipios', 'Postos'],
                                      how='left')
Anos_completos.drop(columns=['Primeiro_mes_x'], inplace=True)
Anos_completos.rename(columns={
    'Ano_inicial_y': 'Ano_inicial',
    'Ano_final_y': 'Ano_final',
    'Primeiro_mes_y': 'Primeiro_mes'
},
                      inplace=True)

print("\nVerificando quantos meses de falha existem parada cada posto")

# Verificar quantos meses de falha existem em cada posto

dias_cols = [f'Dia{i}' for i in range(1, 32)]


def verificar_meses_falha(df):

    df['Mes_falha'] = df[dias_cols].apply(lambda row: any(day == 999.0
                                                          for day in row),
                                          axis=1)

    meses_falha_por_posto = df.groupby('Postos')['Mes_falha'].sum()

    return meses_falha_por_posto


meses_falha_por_posto = verificar_meses_falha(Anos_completos)
meses_falha_por_posto
Anos_completos = Anos_completos.merge(
    meses_falha_por_posto.rename('Meses_de_Falha'), on='Postos', how='left')
Anos_completos = Anos_completos.drop(columns=['Mes_falha'])

print(
    "\nCalculando intervalo de dias,meses e anos totais de falhas por posto..."
)

from datetime import datetime


def calcular_intervalo_dias(row):
    data_inicial = datetime(row['Ano_inicial'], 1, 1)
    data_final = datetime(row['Ano_final'], 12,
                          31)  
    intervalo = (data_final - data_inicial).days
    return intervalo


def contar_dias_falha(row):
    return sum(row[dia] == 999.0 for dia in dias_cols)


Anos_completos['Intervalo_dias'] = Anos_completos.apply(
    calcular_intervalo_dias, axis=1)
Anos_completos['Dias_de_Falha'] = Anos_completos.apply(contar_dias_falha,
                                                       axis=1)
total_falhas_por_posto = Anos_completos.groupby(
    'Postos')['Dias_de_Falha'].sum().reset_index()
total_falhas_por_posto.rename(columns={'Dias_de_Falha': 'Total_Falhas'},
                              inplace=True)
Anos_completos = Anos_completos.merge(total_falhas_por_posto,
                                      on='Postos',
                                      how='left')
Anos_completos['Intervalo_anos'] = (
    1 + Anos_completos['Ano_final']) - Anos_completos['Ano_inicial']
Anos_completos['Intervalo_meses'] = Anos_completos['Intervalo_anos'] * 12

Anos_completos.drop(columns=['Dias_de_Falha'], inplace=True)

Anos_completos['dias_medidos'] = Anos_completos[
    'Intervalo_dias'] - Anos_completos['Total_Falhas']

print("\nCalculando a porcentagem de dias de falhas por posto...")

Anos_completos['Porcentagem_dias_Falhas'] = (
    Anos_completos['Total_Falhas'] / Anos_completos['Intervalo_dias']) * 100
Anos_completos['Porcentagem_dias_Falhas'] = Anos_completos['Porcentagem_dias_Falhas'].round(2)

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


anos_falha_por_posto = contar_anos_falha(Anos_completos)
Anos_completos = Anos_completos.merge(anos_falha_por_posto,
                                      on='Postos',
                                      how='left')
Anos_completos.drop(columns=['Ano_com_falha'], inplace=True)

print("\nCalculando anos completos medidos por posto...")

# Agrupar por Município, Posto, Latitude e Longitude para garantir que os dados são do mesmo posto no mesmo município
Anos_completos['Anos_completos_medidos'] = Anos_completos.groupby(
    ['Municipios', 'Postos', 'Latitude', 'Longitude']
)['Intervalo_anos'].transform('first') - Anos_completos.groupby(
    ['Municipios', 'Postos', 'Latitude', 'Longitude']
)['Anos_de_Falha'].transform('first')

Anos_completos['Porcentagem_anos_Falhas'] = (
    Anos_completos['Anos_de_Falha'] / Anos_completos['Intervalo_anos']) * 100
Anos_completos['Porcentagem_anos_Falhas'] = Anos_completos['Porcentagem_anos_Falhas'].round(2)

print("\nCalculando a média mensal de chuvas por posto...")

dados_validos = Anos_completos[Anos_completos['Total'] != 999.0]

medias_mensais = pd.DataFrame()

postos_unicos = dados_validos['Postos'].unique()

for posto in postos_unicos:
    df_posto = dados_validos[dados_validos['Postos'] == posto]
    intervalo_anos = df_posto['Intervalo_anos'].iloc[0]

    medias_posto = {}
    medias_posto['Posto'] = posto

    for mes in range(1, 13):
        total_mes = df_posto[df_posto['Meses'] == mes]['Total'].sum()
        media_mes = total_mes / intervalo_anos
        medias_posto[f'Media_Mes_{mes}'] = media_mes

    medias_mensais = pd.concat(
        [medias_mensais, pd.DataFrame([medias_posto])], ignore_index=True)

Anos_completos = Anos_completos.merge(medias_mensais,
                                      left_on='Postos',
                                      right_on='Posto',
                                      how='left')

Anos_completos.drop(columns=['Posto'], inplace=True)

print("\nCalculando a média anual de chuvas por posto...")

postos_unicos = Anos_completos['Postos'].unique()

Anos_completos['Media_Anual'] = 0.0

for posto in postos_unicos:
    df_posto = Anos_completos[Anos_completos['Postos'] == posto]
    intervalo_anos = df_posto['Intervalo_anos'].iloc[0]

    soma_total_chuvas = df_posto[df_posto['Total'] != 999].groupby(
        'Anos')['Total'].sum().sum()

    media_anual = soma_total_chuvas / intervalo_anos

    Anos_completos.loc[Anos_completos['Postos'] == posto,
                       'Media_Anual'] = media_anual

Anos_completos['Total_meses_intervalo'] = Anos_completos['Intervalo_anos'] * 12

Anos_completos.drop(columns=['Intervalo_meses'], inplace=True)

Anos_completos['Numero_meses_completos'] = Anos_completos[
    'Total_meses_intervalo'] - Anos_completos['Meses_de_Falha']


def calcular_percentual_meses_falha(df):
    df['Percentual_meses_falha'] = (df['Meses_de_Falha'] / df['Total_meses_intervalo']) * 100
    df['Percentual_meses_falha'] = df['Percentual_meses_falha'].round(2)
    return df


Anos_completos = calcular_percentual_meses_falha(Anos_completos)

print("criando um resumo dos postos...")

colunas_resumo = [
    'Municipios', 'Postos', 'Latitude', 'Longitude', 'Ano_inicial',
    'Ano_final', 'Primeiro_mes', 'Ultimo_mes', 'Intervalo_dias',
    'dias_medidos', 'Total_Falhas', 'Porcentagem_dias_Falhas',
    'Total_meses_intervalo', 'Numero_meses_completos', 'Meses_de_Falha',
    'Percentual_meses_falha', 'Intervalo_anos', 'Anos_completos_medidos',
    'Anos_de_Falha', 'Porcentagem_anos_Falhas', 'Media_Anual'
]

# Adicionar as colunas de médias mensais
for mes in range(1, 13):
    colunas_resumo.append(f'Media_Mes_{mes}')

# Criar o DataFrame de resumo
df_resumo = Anos_completos[colunas_resumo].drop_duplicates()

# Adicionar a coluna Chave_ID
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
    'Anos_completos_medidos': 'Numero_anos_completos',
    'Anos_de_Falha': 'Numero_anos_falha',
    'Porcentagem_anos_Falhas': 'Percentual_anos_falha',
    'Media_Anual': 'Precipitacao_media_anual'
},
                 inplace=True)

import json

# Selecionar as colunas necessárias e renomeá-las conforme o formato desejado
df_formatado_resumo = df_resumo.rename(columns={
    'Nome_Municipio': 'Nome_Municipio',
    'Nome_Posto': 'Nome_Posto',
    'Coordenada_Y': 'Coordenada_Y',
    'Coordenada_X': 'Coordenada_X',
    'Ano_Inicio': 'Ano_Inicio',
    'Ano_Fim': 'Ano_Fim',
    'Mes_Inicio': 'Mes_Inicio',
    'Mes_Fim': 'Mes_Fim',
    'Total_dias_intervalo': 'Total_dias_intervalo',
    'Dias_dados_medidos': 'Dias_dados_medidos',
    'Dias_falhos': 'Dias_falhos',
    'Percentual_dias_falhos': 'Percentual_dias_falhos',
    'Total_meses_intervalo': 'Total_meses_intervalo',
    'Numero_meses_completos': 'Numero_meses_completos',
    'Numero_meses_falha': 'Numero_meses_falha',
    'Percentual_meses_falha': 'Percentual_meses_falha',
    'Total_anos_intervalo': 'Total_anos_intervalo',
    'Numero_anos_completos': 'Numero_anos_completos',
    'Numero_anos_falha': 'Numero_anos_falha',
    'Percentual_anos_falha': 'Percentual_anos_falha',
    'Precipitacao_media_anual': 'Precipitacao_media_anual',
    'Media_Mes_1': 'Jan_chuva',
    'Media_Mes_2': 'Fev_chuva',
    'Media_Mes_3': 'Mar_chuva',
    'Media_Mes_4': 'Apr_chuva',
    'Media_Mes_5': 'May_chuva',
    'Media_Mes_6': 'Jun_chuva',
    'Media_Mes_7': 'Jul_chuva',
    'Media_Mes_8': 'Aug_chuva',
    'Media_Mes_9': 'Sep_chuva',
    'Media_Mes_10': 'Oct_chuva',
    'Media_Mes_11': 'Nov_chuva',
    'Media_Mes_12': 'Dec_chuva'
})

# Converter todos os valores numéricos para strings
df_formatado_resumo = df_formatado_resumo.map(lambda x: str(x) if isinstance(x, (int, float)) else x)

import unicodedata

def remover_acentos(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

df_formatado_resumo = df_formatado_resumo.map(
    lambda x: remover_acentos(x) if isinstance(x, str) else x
)

# Converter o dataframe para uma lista de dicionários
dados_formatados_resumo = df_formatado_resumo.to_dict(orient='records')

# Salvar a lista de dicionários em um arquivo JSON
with open('dados_formatados_resumo.json', 'w') as f:
    json.dump(dados_formatados_resumo, f, ensure_ascii=False, indent=4)

print("Arquivo JSON gerado com sucesso.")

df_resumo.to_csv('resumo_postos.csv', index=False)

import os

municipios_unicos = Anos_completos['Municipios'].unique()

mes_renomear = {
    'Media_Mes_1': 'Jan_chuva',
    'Media_Mes_2': 'Fev_chuva',
    'Media_Mes_3': 'Mar_chuva',
    'Media_Mes_4': 'Apr_chuva',
    'Media_Mes_5': 'May_chuva',
    'Media_Mes_6': 'Jun_chuva',
    'Media_Mes_7': 'Jul_chuva',
    'Media_Mes_8': 'Aug_chuva',
    'Media_Mes_9': 'Sep_chuva',
    'Media_Mes_10': 'Oct_chuva',
    'Media_Mes_11': 'Nov_chuva',
    'Media_Mes_12': 'Dec_chuva'
}

Anos_completos.rename(columns=mes_renomear, inplace=True)

for municipio in municipios_unicos:

    registros_municipio = Anos_completos[Anos_completos['Municipios'] ==
                                         municipio]

    nome_arquivo = os.path.join("postos tratados", f"{municipio}.csv")

    registros_municipio.to_csv(nome_arquivo, index=False)

print("\nArquivos CSV gerados para cada município na pasta 'postos tratados'.")
