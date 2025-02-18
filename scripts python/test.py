from dotenv import load_dotenv
load_dotenv()
import os
from supabase import create_client, Client

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

print("Chave e url copiados com sucesso!")
print(f"URL: {supabase_url}, KEY: {supabase_key[:5]}...") 

supabase = create_client(supabase_url, supabase_key)

print("Cliente Supabase criado com sucesso!")

try:
    response = supabase.table("pluviometria").select("*").limit(1).execute()
    print("Conexão estabelecida! Resposta:", response)
except Exception as e:
    print("Erro na conexão com Supabase:", e)

test_data = {
    "ID": 1,
    "Nome_Municipio": "Abaiara",
    "Nome_Posto": "ABAIARA",
    "Coordenada_Y": -7.36152778,
    "Coordenada_X": -39.0355,
    "Anos": 1981,
    "Meses": 1,
    "Total": 46.2,
    "Dia1": 0,
    "Dia2": 0,
    "Dia3": 0,
    "Dia4": 0,
    "Dia5": 0,
    "Dia6": 0,
    "Dia7": 0,
    "Dia8": 0,
    "Dia9": 9,
    "Dia10": 0.0,
    "Dia11": 0.0,
    "Dia12": 0.0,
    "Dia13": 0.0,
    "Dia14": 0.0,
    "Dia15": 0.0,
    "Dia16": 6.0,
    "Dia17": 0.0,
    "Dia18": 12.2,
    "Dia19": 0.0,
    "Dia20": 0.0,
    "Dia21": 0.0,
    "Dia22": 0.0,
    "Dia23": 0.0,
    "Dia24": 0.0,
    "Dia25": 0.0,
    "Dia26": 7.0,
    "Dia27": 1.0,
    "Dia28": 11.0,
    "Dia29": 0.0,
    "Dia30": 0.0,
    "Dia31": 0.0,
    "Ano_Inicio": 1981,
    "Ano_Fim": 2024,
    "Mes_Inicio": 1,
    "Mes_Fim": 12,
    "Numero_meses_falha": 2,
    "Total_dias_intervalo": 16082,
    "Dias_falhos": 34,
    "Total_anos_intervalo": 44,
    "Dias_dados_medidos": 16048,
    "Percentual_dias_falhos": 0.21,
    "Numero_anos_falha": 2,
    "Numero_anos_completos": 42,
    "Percentual_anos_falha": 4.55,
    "Media_Jan": 148.58,
    "Media_Fev": 177.61,
    "Media_Mar": 251.54,
    "Media_Apr": 165.95,
    "Media_May": 52.81,
    "Media_Jun": 14.25,
    "Media_Jul": 6.2,
    "Media_Aug": 1.0,
    "Media_Sep": 3.58,
    "Media_Oct": 12.05,
    "Media_Nov": 28.54,
    "Media_Dec": 66.19,
    "Precipitacao_media_anual": 930.39,
    "Total_meses_intervalo": 528,
    "Numero_meses_completos": 526,
    "Percentual_meses_falha": 0.38
}

response = supabase.table("pluviometria").insert(test_data).execute()
print(response)