import panel as pn
from .df_import import load_municipio, load_posto, load_registro, load_diario
from fastapi import FastAPI
from panel.io.fastapi import add_applications
import folium
import pandas as pd
from folium.plugins import MousePosition
from folium.plugins import BeautifyIcon
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from supabase import create_client, Client
import os
import io
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
    nome_posto = Column(String)
    anos_medidos = Column(Integer)
    precipitacao_media_anual = Column(Float)
    coordenadas = Column(Geometry(geometry_type="POINT", srid=4326))

DATABASE_URL = f"postgresql://postgres:344gwd5W1MDwZ9up@db.hqnkhorlbswlklcfvoob.supabase.co:6543/postgres"

pn.extension()

app = FastAPI()

# Carregamento dos dados
municipio = load_municipio()
posto = load_posto()
registro = load_registro()
registro_diario = load_diario()

pn.extension('tabulator')

# Conectando com Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def buscar_series_para_multiplos_pontos(entrada_texto, data_inicio, data_fim, n_postos=10):
    session = SessionLocal()

    # Processar entrada
    linhas = [linha.strip() for linha in entrada_texto.strip().splitlines() if linha.strip()]
    pontos = []
    for linha in linhas:
        partes = linha.split(",")
        if len(partes) != 3:
            continue
        id_ponto = partes[0].strip()
        lon = float(partes[1].strip())
        lat = float(partes[2].strip())
        pontos.append({'id': id_ponto, 'lon': lon, 'lat': lat})

    # Criar grade de datas completa no intervalo
    datas = pd.date_range(data_inicio, data_fim, freq="D")
    df_resultado = pd.DataFrame({'data': datas})
    df_postos_usados = pd.DataFrame({'data': datas})

    metadata = MetaData()
    registro_diario = Table("registro-diario", metadata, autoload_with=engine)

    for ponto in pontos:
        ponto_geom = from_shape(Point(ponto['lat'], ponto['lon']), srid=4326)

        # Buscar postos mais próximos
        stmt_postos = (
            select(
                Posto.id_posto,
                Posto.nome_posto,
                func.ST_Distance(Posto.coordenadas, ponto_geom).label("distancia")
            )
            .where(Posto.coordenadas != None)
            .order_by(Posto.coordenadas.op('<->')(ponto_geom))
            .limit(n_postos)
        )
        postos_proximos = session.execute(stmt_postos).fetchall()
        ids_postos = [p[0] for p in postos_proximos]

        # Buscar registros para esses postos
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

        # Pivot para ter posto nas colunas
        df_pivot = df.pivot(index="data", columns="id_posto", values="valor")

        # Reindexar para garantir todas as datas
        df_pivot = df_pivot.reindex(datas)

        # Fallback por ordem dos postos mais próximos
        valores = []
        postos_usados = []
        for data in df_pivot.index:
            valor_data = None
            posto_usado = None
            for id_posto in ids_postos:
                try:
                    valor = df_pivot.loc[data, id_posto]
                except KeyError:
                    valor = None
                if pd.notna(valor) and valor != 999:
                    valor_data = valor
                    posto_usado = id_posto
                    break
            valores.append(valor_data)
            postos_usados.append(posto_usado)

        df_resultado[ponto['id']] = valores
        df_postos_usados[ponto['id']] = postos_usados

    session.close()
    os.makedirs("temp", exist_ok=True)
    df_postos_usados.to_csv("temp/postos_utilizados.csv", index=False, sep=";")
    df_resultado.to_csv("temp/serie_diaria_multipontos.csv", index=False, sep=";")
    # Retorna os dois dataframes: valores e postos usados
    return df_resultado, df_postos_usados

def painel_busca_multiplos_pontos():

    input_coords = pn.widgets.TextAreaInput(
        name="Coordenadas (id,lon,lat)", 
        placeholder="id1,-34.91,-8.13\nid2,-34.85,-8.10", 
        width=400, 
        height=150
    )
    limite = pn.widgets.TextInput(name="LIMITE", placeholder="10")
    data_inicio = pn.widgets.DatePicker(name="Data início", value=pd.Timestamp("1974-01-01"))
    data_fim = pn.widgets.DatePicker(name="Data fim", value=pd.Timestamp("2025-01-01"))
    buscar_btn = pn.widgets.Button(name="Buscar série diária", button_type="primary", width=260)

    resultado_nome = pn.pane.Markdown("", width=600)
    spinner = pn.indicators.LoadingSpinner(value=False, width=40, height=40, color="primary")

    tabela_resultado = pn.widgets.Tabulator(pd.DataFrame(), width=800, height=400, pagination='local', page_size=1000)
    tabela_postos = pn.widgets.Tabulator(pd.DataFrame(), width=800, height=400, pagination='local', page_size=1000)

    # Substitui os botões antigos pelos FileDownload
    def get_serie_csv():
        with open("temp/serie_diaria_multipontos.csv", "rb") as f:
            return io.BytesIO(f.read())

    def get_postos_csv():
        with open("temp/postos_utilizados.csv", "rb") as f:
            return io.BytesIO(f.read())

    btn_download_serie = pn.widgets.FileDownload(
        label="📥 Baixar Série Diária",
        filename="serie_diaria_multipontos.csv",
        callback=get_serie_csv,
        button_type="success",
        visible=False,
        width=200
    )

    btn_download_postos = pn.widgets.FileDownload(
        label="📥 Baixar Postos Utilizados",
        filename="postos_utilizados.csv",
        callback=get_postos_csv,
        button_type="success",
        visible=False,
        width=200
    )

    def buscar(event=None):
        spinner.value = True
        resultado_nome.object = "⏳ Carregando..."
        tabela_resultado.value = pd.DataFrame()
        tabela_postos.value = pd.DataFrame()
        btn_download_serie.visible = False
        btn_download_postos.visible = False

        try:
            texto = input_coords.value
            n_postos = int(limite.value) if limite.value.isdigit() else 10
            di = data_inicio.value
            df = data_fim.value

            if not texto or not di or not df:
                resultado_nome.object = "⚠️ Preencha todas as informações."
                return

            df_result, df_postos_usados = buscar_series_para_multiplos_pontos(texto, di, df, n_postos)

            if not df_result.empty:
                df_result["data"] = pd.to_datetime(df_result["data"]).dt.strftime("%Y-%m-%d")
                df_postos_usados["data"] = pd.to_datetime(df_postos_usados["data"]).dt.strftime("%Y-%m-%d")

                tabela_resultado.value = df_result
                tabela_postos.value = df_postos_usados
                resultado_nome.object = "**✅ Série diária para os pontos informados.**"
                
                os.makedirs("temp", exist_ok=True)
                df_result.to_csv("temp/serie_diaria_multipontos.csv", index=False, sep=";")
                df_postos_usados.to_csv("temp/postos_utilizados.csv", index=False, sep=";")

                btn_download_serie.visible = True
                btn_download_postos.visible = True
            else:
                resultado_nome.object = "⚠️ Nenhum dado encontrado."

        except Exception as e:
            resultado_nome.object = f"❌ Erro: {e}"

        finally:
            spinner.value = False

    buscar_btn.on_click(buscar)

    return pn.Column(
        "# Buscar série diária para múltiplos pontos",
        pn.Row(input_coords, limite, data_inicio, data_fim, buscar_btn, spinner),
        resultado_nome,
        pn.Row(btn_download_serie, btn_download_postos),
        pn.Tabs(
            ("📊 Série diária", tabela_resultado),
            ("📌 Postos utilizados", tabela_postos),
        )
    )

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

# ÚNICO ENDPOINT: inclui funcionalidades de busca e mapa
@app.get("/download/{filename}")
def download_file(filename: str):
    filepath = f"temp/{filename}"
    if os.path.exists(filepath):
        return FileResponse(
            path=filepath,
            media_type="text/csv",
            filename=filename
        )
    return {"erro": "Arquivo não encontrado."}

add_applications(
    {
        '/': pn.Tabs(
            ("🌎 Mapa Interativo", view_mapa()),
            ("🔍 Buscar Série Diária", painel_busca_multiplos_pontos()),
        ),
    },
    app=app,
)
