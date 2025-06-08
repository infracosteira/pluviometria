import panel as pn
from .df_import import load_municipio, load_posto, load_registro
from fastapi import FastAPI
from panel.io.fastapi import add_applications
import folium
from panel.io.state import state
from fastapi.responses import HTMLResponse
from folium import Map
from panel.widgets import Tabulator
import pandas as pd
from folium.plugins import MousePosition
from folium.plugins import BeautifyIcon
from fastapi import FastAPI, Query
from supabase import create_client, Client
import os

pn.extension()

app = FastAPI()

# Carregamento dos dados
municipio = load_municipio()
posto = load_posto()
registro = load_registro()

posto[['Latitude', 'Longitude']] = posto['coordenadas'].str.split(',', expand=True).astype(float)

def gerar_mapa(lat, lon):
    m = folium.Map(location=[lat, lon], zoom_start=5)
    folium.Marker(location=[lat, lon], popup="Posto").add_to(m)
    return pn.pane.HTML(m._repr_html_(), height=500)

pn.extension('tabulator')

app = FastAPI()

# Conectando com Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Endpoint para buscar o posto pluviométrico mais próximo via PostGIS
@app.get("/posto-mais-proximo")
def get_posto_mais_proximo(lat: float = Query(...), lon: float = Query(...)):
    sql = f"""
    SELECT 
        id_posto,
        nome_posto,
        ST_Distance(
            localizacao::geography,
            ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326)::geography
        ) AS distancia
    FROM posto
    WHERE localizacao IS NOT NULL
    ORDER BY localizacao <-> ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326)
    LIMIT 1;
    """

    # Faz a chamada diretamente via REST
    response = supabase.rpc("sql", {"q": sql}).execute()

    if response.get("data"):
        result = response["data"][0]
        return {
            "id_posto": result["id_posto"],
            "nome_posto": result["nome_posto"],
            "distancia_m": round(result["distancia"], 2)
        }
    else:
        return {"erro": "Nenhum posto encontrado."}


def to_uppercase():
    texto_input = pn.widgets.TextInput(name="Digite algo", placeholder="Digite um texto...")
    resultado_output = pn.pane.Markdown("**Aguardando...**")
    botao_converter = pn.widgets.Button(name="Converter para MAIÚSCULAS", button_type="primary")

    def ao_clicar(event):
        texto = texto_input.value
        resultado = texto.upper()
        resultado_output.object = f"**Resultado:** {resultado}"

    botao_converter.on_click(ao_clicar)

    layout = pn.Column(
        pn.pane.Markdown("### 🔠 Conversor para MAIÚSCULAS"),
        texto_input,
        botao_converter,
        resultado_output,
        width=400
    )

    return layout

def view_mapa():
    # Mapa interativo com marcadores dos postos
    def gerar_mapa_interativo():
        m = folium.Map(location=[-5.4984, -39.3206], zoom_start=7, width='50%', height='450px')

        # Adiciona os marcadores dos postos
        for _, row in posto.iterrows():
            lat = row['Latitude']
            lon = row['Longitude']
            nome = row['nome_posto']
            id_posto = row['id_posto']
            info_html = f"""
            <div style="text-align:center;">
                <b>{nome}</b><br>
                ID: {id_posto}<br>
                Latitude: {lat:.6f}<br>
                Longitude: {lon:.6f}<br>
                <button style="margin-top:8px;" onclick="navigator.clipboard.writeText('{id_posto},{lat:.6f},{lon:.6f}')">🔗</button>
            </div>
            """
            folium.Marker(
                location=[lat, lon],
                icon=BeautifyIcon(
                    icon_shape='marker',
                    border_color='#1976d2',
                    text_color='white',
                    background_color='#1976d2',
                    number=id_posto,
                ),
                popup=folium.Popup(info_html, max_width=250),
                tooltip=f"{nome} (ID: {id_posto})",
            ).add_to(m)

        # Adiciona posição do mouse
        MousePosition().add_to(m)

        # Adiciona funcionalidade de clique para mostrar popup com botão de copiar coordenadas
        from folium import MacroElement
        from jinja2 import Template

        class ClickPopup(MacroElement):
            _template = Template("""
                {% macro script(this, kwargs) %}
                function onMapClick(e) {
                    var lat = e.latlng.lat.toFixed(6);
                    var lon = e.latlng.lng.toFixed(6);
                    var popupContent = `
                    <div style="text-align:center;">
                        <b>Latitude:</b> ${lat}<br>
                        <b>Longitude:</b> ${lon}<br><br>
                        <button onclick="navigator.clipboard.writeText('x,' + ${lat} + ',' + ${lon})">
                        🔗
                        </button>
                    </div>
                    `;
                    var popup = L.popup()
                        .setLatLng(e.latlng)
                        .setContent(popupContent)
                        .openOn({{this._parent.get_name()}});
                }
                {{this._parent.get_name()}}.on('click', onMapClick);
                {% endmacro %}
            """)

        m.add_child(ClickPopup())

        # Renderiza no Panel
        mapa_html = m._repr_html_()
        return pn.pane.HTML(mapa_html, height=450, sizing_mode='stretch_width')


    mapa_html = gerar_mapa_interativo()

    # Widgets de entrada (funções)
    data_inicio = pn.widgets.DatePicker(name="Data início", width=250, value=pd.Timestamp("1974-01-01"))
    data_fim = pn.widgets.DatePicker(name="Data fim", width=250)
    granularidade = pn.widgets.RadioButtonGroup(
        name="Granularidade",
        options=['diaria', 'mensal', 'anual'],
        button_type='success',
        value='diaria',
        width=250
    )
    granularidade_label = pn.pane.Markdown("**Granularidade:**")
    caixa_texto = pn.widgets.TextAreaInput(name="id,lat,lon", placeholder="Digite aqui...", height=80)

    # Botões
    gerar_btn = pn.widgets.Button(name="Gerar", button_type="primary", width=120)
    baixar_metadados_btn = pn.widgets.Button(name="Baixar Metadados", button_type="success", width=180, visible=False)
    baixar_serie_btn = pn.widgets.Button(name="Baixar Série Histórica", button_type="success", width=180, visible=False)

    def ao_gerar(event):
        baixar_metadados_btn.visible = True
        baixar_serie_btn.visible = True

    gerar_btn.on_click(ao_gerar)

    painel_lateral = pn.Column(
        pn.pane.Markdown("<h2 style='text-align: center;'>🌧️ Pluviometria 🌧️</h2>"),
        caixa_texto,
        data_inicio,
        data_fim,
        granularidade_label,
        granularidade,
        pn.Spacer(height=10),
        pn.Row(
            gerar_btn,
            align='start',
            sizing_mode='stretch_width'
        ),
        pn.Row(
            baixar_metadados_btn,
            baixar_serie_btn,
            align='start',
            sizing_mode='stretch_width'
        ),
        css_classes=["painel-lateral"],
        sizing_mode='stretch_height',
        width=350,
        margin=(20, 40, 0, 0)  # Adiciona margem superior de 20px
    )

    layout = pn.Row(
        pn.Spacer(width=400),
        painel_lateral,
        pn.Column(
            mapa_html,
            sizing_mode='stretch_both'
        ),
        sizing_mode='stretch_both'
    )

    return layout

# Adicionando ao aplicativo
add_applications(
    {
        '/mapa': view_mapa(),
        '/': to_uppercase(),
    },
    app=app,
)