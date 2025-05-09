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


# Supondo que a coluna 'coordenadas' esteja no formato "lat,lon"
posto[['Latitude', 'Longitude']] = posto['coordenadas'].str.split(',', expand=True).astype(float)

def gerar_mapa(lat, lon):
    m = folium.Map(location=[lat, lon], zoom_start=5)
    folium.Marker(location=[lat, lon], popup="Posto").add_to(m)
    return pn.pane.HTML(m._repr_html_(), height=500)

# Tabela interativa com botão
import panel as pn
pn.extension()

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



registro = load_registro()

# Widgets
municipio_search = pn.widgets.TextInput(name='Search Municipio', placeholder='Type to search...')
registro_search = pn.widgets.TextInput(name='Search Registro', placeholder='Type to search...')
row_slider = pn.widgets.IntSlider(name='Nº linhas', start=1, end=max(len(municipio), len(posto), len(registro)), value=10)

pn.extension('tabulator')

# 1. Carregar CSV com links diretos (uma única coluna)
df_links = pd.read_csv('./fast_one/links.csv', header=None, names=['link_csv'])

# 2. Extrair o "id_nomeposto" do final da URL
df_links['id_posto'] = df_links['link_csv'].str.extract(r'/([^/]+)\.csv')

# 3. Gerar botão de download formatado como HTML
def gerar_botao(link):
    return f"""
    <a href="{link}" target="_blank">
        <button style="background-color:#1976d2;color:white;border:none;padding:5px 10px;border-radius:4px;cursor:pointer;">
            Baixar CSV
        </button>
    </a>
    """

df_links['Download'] = df_links['link_csv'].apply(gerar_botao)

# 4. Criar tabela interativa com Panel Tabulator
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
        df_copy[col] = df_copy[col].apply(lambda x: f"{x:,.1f}".replace(",", "X").replace(".", ",").replace("X", "."))
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

# Demais painéis
municipio_pane = pn.bind(
    lambda search, rows: pn.pane.DataFrame(get_filtered_dataframe(municipio, search, rows), name='Municipio'),
    municipio_search, row_slider
)

registro_pane = pn.bind(
    lambda search, rows: pn.pane.DataFrame(get_filtered_dataframe(registro, search, rows), name='Registro'),
    registro_search, row_slider
)

# Adicionando ao aplicativo
add_applications(
    {
        '/tabelas': pn.Row(
            pn.Column('Mapa dos Postos', tabela_com_mapa()),
            pn.Column('Dados dos postos resumidos',tabela_posto()),
            #pn.Column('### Municipio', municipio_search, row_slider, municipio_pane),
            #pn.Column('### Registro', registro_search, registro_pane),
            pn.Column('Download CSVs', tabela_download),
            
            
            
        ),
    },
    app=app,
)
