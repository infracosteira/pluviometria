import httpx

url = "https://hqnkhorlbswlkclcfoob.supabase.co"
try:
    response = httpx.get(url, timeout=10)
    print(response.status_code)
except httpx.HTTPError as e:
    print(f"Erro: {e}")
