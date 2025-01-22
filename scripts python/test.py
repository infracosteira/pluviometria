from dotenv import load_dotenv
load_dotenv()
import os
from supabase import create_client, Client


supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

print("Chave e url copiados com sucesso!")
print(f"URL: {supabase_url}, KEY: {supabase_key[:5]}...") 


supabase = create_client(supabase_url, supabase_key)

data = supabase.table("pluviometria_duplicate").select("Nome_Posto,ID").eq("Nome_Posto", "ANTONIO DIOGO").execute()

print(data)