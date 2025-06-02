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
from fastapi import Request, Form
from fastapi.responses import HTMLResponse

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

pn.extension(raw_css=[
    """
    .painel-lateral {
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        background-color: #f9f9f9;
        padding: 15px;
        min-width: 380px;
        max-width: 420px;
        height: 100vh;
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    """
])


@app.get("/", response_class=HTMLResponse)
async def show_form():
    return """
    <html>
        <head>
            <title>Caixa de Texto</title>
        </head>
        <body>
            <h2>Digite algo:</h2>
            <form action="/" method="post">
                <input type="text" name="user_input">
                <button type="submit">Enviar</button>
            </form>
        </body>
    </html>
    """

@app.post("/", response_class=HTMLResponse)
async def process_form(user_input: str = Form(...)):
    result = user_input.upper()
    return f"""
    <html>
        <head>
            <title>Resultado</title>
        </head>
        <body>
            <h2>Texto em maiúsculas:</h2>
            <p>{result}</p>
            <a href="/">Voltar</a>
        </body>
    </html>
    """

def view_mapa():
    # Mapa interativo com marcadores dos postos
    def gerar_mapa_interativo():
        m = folium.Map(location=[-5.4984, -39.3206], zoom_start=7, width='50%', height='450px')
        for _, row in posto.iterrows():
            lat = row['Latitude']
            lon = row['Longitude']
            nome = row['nome_posto']
            id_posto = row['id_posto']  # Supondo que a coluna de id se chama 'id'
            # Informações adicionais do posto
            info_html = f"""
            <b>{nome}</b><br>
            ID: {id_posto}<br>
            Latitude: {lat:.6f}<br>
            Longitude: {lon:.6f}<br>
            <button onclick="navigator.clipboard.writeText('{id_posto},{lat:.6f},{lon:.6f}')">🔗</button>
            """
            folium.Marker(
                location=[lat, lon],
                icon=BeautifyIcon(
                    icon_shape='marker',
                    border_color='#1976d2',
                    text_color='white',
                    background_color='#1976d2',
                    number=id_posto,  # Mostra o id do posto no marcador
                ),
                popup=folium.Popup(info_html, max_width=250),
                tooltip=f"{nome} (ID: {id_posto})",
            ).add_to(m)
        MousePosition().add_to(m)
        folium.LatLngPopup().add_to(m)
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
        sizing_mode='stretch_height'
    )

    layout = pn.Row(
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
    },
    app=app,
)