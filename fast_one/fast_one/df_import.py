import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

def load_data():
    municipio = supabase.table("municipio").select("*").execute().data
    posto = supabase.table("posto").select("*").execute().data
    registro = supabase.table("registro").select("*").execute().data

    return (
        pd.DataFrame(municipio),
        pd.DataFrame(posto),
        pd.DataFrame(registro)
    )
