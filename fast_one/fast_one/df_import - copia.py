import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client
import re

load_dotenv()
url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

def load_municipio():
    return pd.DataFrame(supabase.table("municipio").select("*").execute().data)

def load_posto():
    df_posto = pd.DataFrame(supabase.table("posto").select("*").execute().data)

    def parse_point_data(point_obj):
        if isinstance(point_obj, dict) and \
           point_obj.get('type') == 'Point' and \
           'coordinates' in point_obj:
            
            longitude = float(point_obj['coordinates'][0])
            latitude = float(point_obj['coordinates'][1])
            return latitude, longitude
        
        elif isinstance(point_obj, str):
            match = re.match(r'POINT\s*\(\s*([-+]?\d+\.?\d*)\s+([-+]?\d+\.?\d*)\s*\)', point_obj.strip(), re.IGNORECASE)
            if match:
                longitude = float(match.group(1))
                latitude = float(match.group(2))
                return latitude, longitude
        
        return None, None

    df_posto[['Latitude', 'Longitude']] = df_posto['coordenadas'].apply(
        lambda x: pd.Series(parse_point_data(x))
    )
    return df_posto

def load_registro():
    return pd.DataFrame(supabase.table("registro_mensal").select("*").execute().data)

def load_diario():
    return pd.DataFrame(supabase.table("registro-diario").select("*").execute().data)