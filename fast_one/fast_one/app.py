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
from geopy.distance import geodesic

pn.extension()

app = FastAPI()

@app.get('/', response_class=HTMLResponse)
def read_root():
    ceara_coords = [-5.4984, -39.3206]
    m = folium.Map(location=ceara_coords, zoom_start=7, width='50%', height='100%')
    m.add_child(folium.ClickForMarker(popup="Marcador adicionado!"))
    return m.get_root().render()

# Carregamento dos dados
municipio = load_municipio()
posto = load_posto()
registro = load_registro()

posto[['Latitude', 'Longitude']] = posto['coordenadas'].str.split(',', expand=True).astype(float)

def gerar_mapa(lat, lon):
    m = folium.Map(location=[lat, lon], zoom_start=5)
    folium.Marker(location=[lat, lon], popup="Posto").add_to(m)
    return pn.pane.HTML(m._repr_html_(), height=500)

def tabela_com_mapa():
    mapa_view = pn.pane.HTML(height=500)
    search_input = pn.widgets.TextInput(placeholder="Buscar posto...")
    buttons_column = pn.Column()

    def show_map(row):
        lat, lon = row['Latitude'], row['Longitude']
        mapa_view.object = gerar_mapa(lat, lon).object

    def update_buttons(event=None):
        termo = search_input.value.lower()
        filtrado = posto[posto['nome_posto'].str.lower().str.contains(termo)].head(5)

        buttons = []
        for _, row in filtrado.iterrows():
            button = pn.widgets.Button(name=row['nome_posto'], width=200, button_type="primary")
            button.on_click(lambda event, row=row: show_map(row))
            buttons.append(button)
        
        buttons_column[:] = buttons

    # Atualiza ao digitar
    search_input.param.watch(update_buttons, 'value')
    update_buttons()  # inicializa com os primeiros 5

    return pn.Column(
        pn.pane.Markdown("### Buscar posto para ver no mapa:"),
        search_input,
        buttons_column,
        mapa_view
    )

#municipio_search = pn.widgets.TextInput(name='Search Municipio', placeholder='Type to search...')
#registro_search = pn.widgets.TextInput(name='Search Registro', placeholder='Type to search...')
#row_slider = pn.widgets.IntSlider(name='Nº linhas', start=1, end=max(len(municipio), len(posto), len(registro)), value=10)

pn.extension('tabulator')
df_links = pd.read_csv('./fast_one/links.csv', header=None, names=['link_csv'])
df_links['id_posto'] = df_links['link_csv'].str.extract(r'/([^/]+)\.csv')

def gerar_botao(link):
    return f"""
    <a href="{link}" target="_blank">
        <button style="background-color:#1976d2;color:white;border:none;padding:5px 10px;border-radius:4px;cursor:pointer;">
            Baixar CSV
        </button>
    </a>
    """

df_links['Download'] = df_links['link_csv'].apply(gerar_botao)

tabela_download = pn.widgets.Tabulator(
    df_links[['id_posto', 'Download']],
    pagination='local',
    page_size=15,
    formatters={'Download': {'type': 'html'}},
    editors={'id_nomeposto': None, 'Download': None},
    header_filters={'id_posto': True, 'Download': False},  # Desabilita pesquisa na coluna Download
    show_index=False
)

# Função de filtro
def get_filtered_dataframe(df, search, rows):
    if search:
        df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False, na=False).any(), axis=1)]
    return df.head(rows)

def format_dataframe_brl(df):
    df_copy = df.copy()
    num_cols = df_copy.select_dtypes(include=['float', 'int']).columns
    for col in num_cols:
        if col == 'precipitação media anual':
            df_copy[col] = df_copy[col].apply(lambda x: f"{x:,.1f}".replace(",", "X").replace(".", ",").replace("X", "."))
        else:
            df_copy[col] = df_copy[col].apply(lambda x: f"{int(x):,}".replace(",", ".") if pd.notnull(x) else x)
    return df_copy


def tabela_posto():
    df_formatado = format_dataframe_brl(posto)

    # Ocultar as colunas Latitude e Longitude
    colunas_visiveis = [col for col in df_formatado.columns if col not in ['Latitude', 'Longitude']]

    table = pn.widgets.Tabulator(
        df_formatado[colunas_visiveis],
        pagination="local",
        page_size=15,
        header_filters={
            col: (col in ['id_posto', 'cod_ibge', 'nome_posto']) for col in colunas_visiveis
        },
        editors={col: None for col in colunas_visiveis},  # torna não editável
        show_index=False
    )

    return pn.Column(
        table
    )
def gerar_mapa_interativo():
        m = folium.Map(location=[-5.4984, -39.3206], zoom_start=7)

        # Marcadores dos postos
        for _, row in posto.iterrows():
            folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            radius=3,
            color='blue',
            fill=True,
            fill_color='blue',
            popup=row['nome_posto'],  # Mostra o nome do posto ao clicar
            tooltip=row['nome_posto'],  # Mostra o nome ao passar o mouse
            ).add_to(m)

        # Mostrar posição do mouse
        MousePosition().add_to(m)

        # Ativa clique para gerar marcador (usuário copia coord)
        folium.LatLngPopup().add_to(m)  # <-- Mostra coordenadas ao clicar

        # Corrigido: use m._repr_html_() para garantir renderização correta no Panel
        return pn.pane.HTML(m._repr_html_(), height=500, sizing_mode='stretch_width')

    # Busca por raio
def pontos_proximos(lat_centro, lon_centro, raio_km):
        centro = (lat_centro, lon_centro)
        mask = posto.apply(
            lambda r: geodesic(centro, (r['Latitude'], r['Longitude'])).km <= raio_km, axis=1
        )
        return posto[mask]


def view_mapa():
        mapa_html = pn.pane.HTML(gerar_mapa_interativo().object, height=500, sizing_mode='stretch_width')

        # Mesmo widgets reutilizados
        coord_input = pn.widgets.TextInput(name="Coordenadas (lat,lon)", placeholder="-7.1,-39.68")
        raio_slider = pn.widgets.IntSlider(name="Raio de busca (km)", start=1, end=100, value=20)
        resultado_busca = pn.pane.DataFrame(height=200)
        botao_buscar = pn.widgets.Button(name="Buscar postos próximos", button_type="primary")

        def buscar_pontos(event=None):
            try:
                lat_str, lon_str = coord_input.value.split(',')
                lat, lon = float(lat_str), float(lon_str)
                raio = raio_slider.value
                df = pontos_proximos(lat, lon, raio)
                resultado_busca.object = df[['id_posto', 'nome_posto', 'Latitude', 'Longitude']]
            except Exception as e:
                resultado_busca.object = f"Erro: {e}"

        botao_buscar.on_click(buscar_pontos)

        # Script para copiar coordenadas do clique no mapa e preencher automaticamente
        callback_js = """
        <script>
        setTimeout(() => {
            const mapIframes = document.querySelectorAll('iframe');
            mapIframes.forEach(iframe => {
                iframe.contentWindow.document.addEventListener('click', function(e) {
                    const popup = iframe.contentWindow.document.querySelector('.leaflet-popup-content');
                    if (popup) {
                        const coordText = popup.textContent.trim();
                        const match = coordText.match(/([-\\d\\.]+),\\s*([-\\d\\.]+)/);
                        if (match) {
                            const latlon = `${match[1]},${match[2]}`;
                            const input = parent.document.querySelector('input[type="text"][placeholder="-7.1,-39.68"]');
                            if (input) {
                                input.value = latlon;
                                input.dispatchEvent(new Event('input', { bubbles: true }));
                                const btn = parent.document.querySelector('button:contains("Buscar postos próximos")');
                                if (btn) btn.click();
                            }
                        }
                    }
                });
            });
        }, 2000);
        </script>
        """

        return pn.Column(
            pn.pane.Markdown("## Mapa interativo — clique para buscar postos próximos"),
            mapa_html,
            pn.pane.HTML(callback_js, sizing_mode='stretch_width'),  # Executa script
            coord_input,
            raio_slider,
            botao_buscar,
            pn.pane.Markdown("### Postos encontrados:"),
            resultado_busca
        )


# Adicionando ao aplicativo
add_applications(
    {
        '/tabelas': pn.Row(
            pn.Column('Mapa dos Postos', tabela_com_mapa()),
            pn.Column('Dados dos postos resumidos', tabela_posto()),
            pn.Column('Download CSVs', tabela_download),
        ),
        '/mapa': view_mapa(),  # <-- NOVO ENDPOINT
    },
    app=app,
)

