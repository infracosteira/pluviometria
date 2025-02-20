from dotenv import load_dotenv
load_dotenv()
import os
from supabase import create_client, Client
import pandas as pd

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

print("Chave e url copiados com sucesso!")
print(f"URL: {supabase_url}, KEY: {supabase_key[:5]}...") 

supabase = create_client(supabase_url, supabase_key)

print("Cliente Supabase criado com sucesso!")

df = pd.read_csv('data/maindatabase.csv')
table_name = "pluviometria"

test_data = df.to_dict(orient='records')

batch_size = 1000  
for i in range(0, len(test_data), batch_size):
    batch = test_data[i:i + batch_size]
    response = supabase.table("pluviometria").insert(batch).execute()
    print(f"Lote {i // batch_size + 1} inserido com sucesso! Resposta:", response)
