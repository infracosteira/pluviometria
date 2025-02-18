import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

print("Chave e URL copiadas com sucesso!")

# Criar cliente Supabase
supabase: Client = create_client(supabase_url, supabase_key)

def upload_dataframe_to_supabase(dataframe: pd.DataFrame, table_name: str):
    
    data = dataframe.to_dict(orient="records")

    try:
        response = supabase.table(table_name).insert(data).execute()
        print(f"Resposta do Supabase: {response}")
        
        if "error" not in response:
            print(f"✅ Dados importados com sucesso para a tabela '{table_name}'")
        else:
            print(f"❌ Erro ao importar dados: {response['error']}")
    except Exception as e:
        print(f"⚠ Ocorreu um erro ao inserir os dados: {e}")

# Ler CSV
df = pd.read_csv('data/maindatabase.csv')
table_name = "pluviometria"

# Importar o DataFrame
upload_dataframe_to_supabase(df, table_name)
