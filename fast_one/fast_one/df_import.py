import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(url, key)
print("Supabase client created")

def load_municipio():
    return pd.DataFrame(supabase.table("municipio").select("*").execute().data)

def load_posto():
    return pd.DataFrame(supabase.table("posto").select("*").execute().data)

def load_registro():
    return pd.DataFrame(supabase.table("registro").select("*").execute().data)

