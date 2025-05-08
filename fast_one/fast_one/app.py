# main.py
import panel as pn
import param
import pandas as pd
from fastapi import FastAPI, Query
from panel.io.fastapi import add_applications
from fastapi.responses import HTMLResponse
import folium
from geopy.distance import geodesic

from .df_import import load_municipio, load_posto, load_registro

pn.extension('tabulator')  # ou 'widgets', conforme preferir

# FastAPI
app = FastAPI()

# Dados
municipio = load_municipio()
posto = load_posto()
registro = load_registro()

# Widgets
municipio_search = pn.widgets.TextInput(name='Search Municipio', placeholder='Type to search...')
registro_search = pn.widgets.TextInput(name='Search Registro', placeholder='Type to search...')
row_slider = pn.widgets.IntSlider(name='Nº linhas', start=1, end=max(len(municipio), len(posto), len(registro)), value=10)

# ====================
# 1. CLASSE COM PARAM
# ====================
class PostoFilter(param.Parameterized):
    search = param.String(default='')
    column = param.String(default='')
    rows = param.Integer(default=10, bounds=(1, len(posto)))
    latitude = param.Number(default=None)
    longitude = param.Number(default=None)

    def __init__(self, posto_df, **params):
        super().__init__(**params)
        self._original_df = posto_df
        self.filtered_df = posto_df.copy()

    @param.depends('search', 'column', 'rows', 'latitude', 'longitude', watch=True)
    def update_filtered(self):
        df = self._original_df.copy()

        # Filtro por distância
        if self.latitude is not None and self.longitude is not None:
            def parse_coords(coord_str):
                try:
                    x, y = map(float, coord_str.split(','))
                    return (y, x)
                except:
                    return None

            df['coord'] = df['coordenadas'].apply(parse_coords)
            df = df.dropna(subset=['coord'])
            centro = (self.latitude, self.longitude)
            df['distancia_km'] = df['coord'].apply(lambda c: geodesic(centro, c).km)
            df = df[df['distancia_km'] <= 5]
            df = df.drop(columns=['coord', 'distancia_km'])

        # Filtro por texto
        if self.search:
            if self.column:
                df = df[df[self.column].astype(str).str.contains(self.search, case=False, na=False)]
            else:
                df = df[df.apply(lambda row: row.astype(str).str.contains(self.search, case=False, na=False).any(), axis=1)]

        self.filtered_df = df.head(self.rows)

# Instância da classe
posto_filter = PostoFilter(posto)

# Widgets conectados
posto_search = pn.widgets.TextInput(name='Search Posto', placeholder='Type to search...')
posto_column_select = pn.widgets.Select(name='Select Column', options=list(posto.columns))

posto_search.link(posto_filter, value='search')
posto_column_select.link(posto_filter, value='column')
row_slider.link(posto_filter, value='rows')

# Panes
municipio_pane = pn.bind(
    lambda search, rows: pn.pane.DataFrame(get_filtered_dataframe(municipio, search, rows), name='Municipio'),
    municipio_search, row_slider  # Passe os widgets, não os valores
)




registro_pane = pn.bind(
    lambda search, rows: pn.pane.DataFrame(
        registro[registro.apply(lambda row: row.astype(str).str.contains(search, case=False, na=False).any(), axis=1)].head(rows),
        name='Registro'),
    registro_search, row_slider
)

posto_pane = pn.bind(
    lambda: pn.pane.DataFrame(posto_filter.filtered_df, name='Posto'),
    watch=True
)

# ====================
# 2. ROTA DO MAPA
# ====================
@app.get('/', response_class=HTMLResponse)
def read_root():
    ceara_coords = [-5.4984, -39.3206]
    m = folium.Map(location=ceara_coords, zoom_start=7)

    # Botões de navegação fixos
    folium.map.CustomPane('fixed-button').add_to(m)
    m.get_root().html.add_child(folium.Element('''
        <style>
            .fixed-button {
                position: fixed;
                top: 10px;
                right: 10px;
                z-index: 1000;
            }
        </style>
        <div class="fixed-button">
            <button onclick="window.location.href='/'">Página Inicial</button>
            <button onclick="window.location.href='/tabelas'">Tabelas</button>
        </div>
    '''))

    # Script para captura de clique no mapa
    
    m.get_root().html.add_child(folium.Element('''
    <script>
        var map = document.querySelector('.folium-map').closest('.leaflet-container')._leaflet_map;
        map.on('click', function(e) {
            var lat = e.latlng.lat;
            var lng = e.latlng.lng;
            window.location.href = `/filtrar_postos?lat=${lat}&lng=${lng}`;
        });
    </script>
    '''))

    return m.get_root().render()

# ====================
# 3. ENDPOINT FILTRO
# ====================
@app.get('/filtrar_postos')
def filtrar_postos(lat: float = Query(...), lng: float = Query(...)):
    posto_filter.latitude = lat
    posto_filter.longitude = lng
    posto_filter.update_filtered()
    return {'status': 'ok', 'n_postos': len(posto_filter.filtered_df)}

# ====================
# 4. PANEL NA ROTA /tabelas
# ====================
add_applications(
    {
        '/tabelas': pn.Row(
            pn.Column('## Municipio', municipio_search, row_slider, municipio_pane),
            pn.Column('## Posto', posto_search, posto_column_select, row_slider, posto_pane),
            pn.Column('## Registro', registro_search, registro_pane),
        )
    },
    app=app,
)
