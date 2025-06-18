import panel as pn
from .df_import import load_municipio, load_posto, load_registro, load_diario
from fastapi import FastAPI
from panel.io.fastapi import add_applications
import folium
import pandas as pd
from folium.plugins import MousePosition
from folium.plugins import BeautifyIcon
from fastapi import FastAPI, Query
from supabase import create_client, Client
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import select, func
from shapely.geometry import Point
from geoalchemy2.shape import from_shape
from sqlalchemy import Column, Integer, Float, String
from geoalchemy2 import Geometry
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData, Table

Base = declarative_base()

class Posto(Base):
    __tablename__ = "posto"

    id_posto = Column(Integer, primary_key=True, index=True)
    nome_posto = Column(String)  # Se essa coluna não existir ainda, você pode ignorar
    anos_medidos = Column(Integer)
    precipitacao_media_anual = Column(Float)
    coordenadas = Column(Geometry(geometry_type="POINT", srid=4326))

DATABASE_URL = f"postgresql://postgres:344gwd5W1MDwZ9up@db.hqnkhorlbswlklcfvoob.supabase.co:6543/postgres"

pn.extension()

app = FastAPI()

def buscar_registros_validos_para_ponto(lon, lat, data_inicio, data_fim, n_postos=10):
    session = SessionLocal()
    ponto = from_shape(Point(lat, lon), srid=4326)

    # Buscar os N postos mais próximos
    stmt_postos = (
        select(
            Posto.id_posto,
            Posto.nome_posto,
            func.ST_Distance(Posto.coordenadas, ponto).label("distancia")
        )
        .where(Posto.coordenadas != None)
        .order_by(Posto.coordenadas.op('<->')(ponto))
        .limit(n_postos)
    )
    postos_proximos = session.execute(stmt_postos).fetchall()
    ids_postos = [p[0] for p in postos_proximos]

    # Buscar registros
    metadata = MetaData()
    registro_diario = Table("registro-diario", metadata, autoload_with=engine)

    stmt_registros = (
        select(
            registro_diario.c.id_posto,
            registro_diario.c.data,
            registro_diario.c.valor
        )
        .where(
            registro_diario.c.id_posto.in_(ids_postos),
            registro_diario.c.data >= data_inicio,
            registro_diario.c.data <= data_fim
        )
    )
    registros = session.execute(stmt_registros).fetchall()
    df = pd.DataFrame(registros, columns=["id_posto", "data", "valor"])

    # Criar grade de datas completa no intervalo
    datas = pd.date_range(data_inicio, data_fim, freq="D")

    # Pivot para ter posto nas colunas
    df_pivot = df.pivot(index="data", columns="id_posto", values="valor")

    # Reindexar para garantir todas as datas
    df_pivot = df_pivot.reindex(datas)

    # Fallback por ordem dos postos mais próximos
    resultado = []
    for data in df_pivot.index:
        for id_posto in ids_postos:
            try:
                valor = df_pivot.loc[data, id_posto]
            except KeyError:
                valor = None
            if pd.notna(valor) and valor != 999:
                resultado.append({"data": data, "id_posto": id_posto, "valor": valor})
                break
        else:
            # Nenhum valor encontrado para essa data
            resultado.append({"data": data, "id_posto": None, "valor": None})

    df_final = pd.DataFrame(resultado)
    return df_final

def painel_busca_postgis(condensado=True):
    session = SessionLocal()
    input_coords = pn.widgets.TextInput(name="Coordenadas (lon,lat)", placeholder="-34.91,-8.13")
    limite = pn.widgets.TextInput(name="LIMITE", placeholder="10")
    data_inicio = pn.widgets.DatePicker(name="Data início", value=pd.Timestamp("1974-01-01"))
    data_fim = pn.widgets.DatePicker(name="Data fim")
    buscar_btn = pn.widgets.Button(name="Buscar série diária", button_type="primary", width=260)
    resultado_nome = pn.pane.Markdown("", width=600)
    tabela_resultado = pn.pane.DataFrame(pd.DataFrame(), width=600, height=300)
    
    def buscar(event=None):
        try:
            lon, lat = map(float, input_coords.value.split(","))
            n_postos = int(limite.value) if limite.value.isdigit() else 10
            di = data_inicio.value
            df = data_fim.value
            if not di or not df:
                resultado_nome.object = "Selecione intervalo de datas."
                return
            df_result = buscar_registros_validos_para_ponto(lon, lat, di, df, n_postos)
            if not df_result.empty:
                resultado_nome.object = f"**Série diária para o ponto ({lon:.4f},{lat:.4f})**"
                tabela_resultado.object = df_result[["data", "id_posto", "valor"]]
            else:
                resultado_nome.object = "Nenhum dado encontrado."
                tabela_resultado.object = pd.DataFrame()
        except Exception as e:
            resultado_nome.object = f"Erro: {e}"
            tabela_resultado.object = pd.DataFrame()

    buscar_btn.on_click(buscar)

    return pn.Column(
        "# Buscar série diária para ponto",
        pn.Row(input_coords, limite, data_inicio, data_fim, buscar_btn),
        resultado_nome,
        tabela_resultado
    )

# Carregamento dos dados
municipio = load_municipio()
posto = load_posto()
registro = load_registro()
registro_diario = load_diario()

pn.extension('tabulator')
app = FastAPI()

# Conectando com Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()









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
        from sqlalchemy import Table, MetaData, and_

        class ClickPopup(MacroElement):
            _template = Template("""
                {% macro script(this, kwargs) %}
                if (!window.clickPopupIdCounter) {
                    window.clickPopupIdCounter = 1;
                }
                function onMapClick(e) {
                    var lat = e.latlng.lat.toFixed(6);
                    var lon = e.latlng.lng.toFixed(6);
                    var id = window.clickPopupIdCounter++;
                    var popupContent = `
                    <div style="text-align:center;">
                        <b>Latitude:</b> ${lat}<br>
                        <b>Longitude:</b> ${lon}<br><br>
                        <button onclick="navigator.clipboard.writeText('${id},' + ${lat} + ',' + ${lon})">
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
        '/': painel_busca_postgis(),
    },
    app=app,
)