import os
import io

import pandas as pd
import panel as pn
import folium
from folium.plugins import MousePosition, BeautifyIcon
from folium import MacroElement
from jinja2 import Template
from shapely.geometry import Point

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from panel.io.fastapi import add_applications

from sqlalchemy import (
    create_engine, select, func, Column, Integer, Float, String, MetaData, Table
)
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape

from supabase import create_client, Client

from .df_import import load_municipio, load_posto, load_registro, load_diario

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

def buscar_series_para_multiplos_pontos(entrada_texto, data_inicio, data_fim, n_postos=10, progresso_callback=None):
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

    datas = pd.date_range(data_inicio, data_fim, freq="D")
    df_resultado = pd.DataFrame({'data': datas})
    df_postos_usados = pd.DataFrame({'data': datas})

    metadata = MetaData()
    registro_diario = Table("registro-diario", metadata, autoload_with=engine)

    total_pontos = len(pontos)
    for idx, ponto in enumerate(pontos):
        ponto_geom = from_shape(Point(ponto['lat'], ponto['lon']), srid=4326)

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
        df_pivot = df.pivot(index="data", columns="id_posto", values="valor")
        df_pivot = df_pivot.reindex(datas)

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

        if progresso_callback is not None:
            progresso_callback(int(20 + 60 * (idx + 1) / total_pontos))

    session.close()
    os.makedirs("temp", exist_ok=True)
    df_postos_usados.to_csv("temp/postos_utilizados.csv", index=False, sep=";")
    df_resultado.to_csv("temp/serie_diaria_multipontos.csv", index=False, sep=";")
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

    granularidade = pn.widgets.RadioButtonGroup(
        name="Granularidade",
        options=['diaria', 'mensal', 'anual'],
        button_type='success',
        value='diaria',
        width=200
    )

    buscar_btn = pn.widgets.Button(name="Buscar série", button_type="primary", width=260)
    resultado_nome = pn.pane.Markdown("", width=600)

    progresso = pn.indicators.Progress(name='Progresso', value=0, width=260, bar_color='primary')

    tabela_resultado = pn.widgets.Tabulator(pd.DataFrame(), width=800, height=400, pagination='local', page_size=1000)
    tabela_postos = pn.widgets.Tabulator(pd.DataFrame(), width=800, height=400, pagination='local', page_size=1000)

    btn_download_serie = pn.widgets.FileDownload(
        label="📥 Baixar Série",
        filename="serie_multipontos.csv",
        callback=lambda: io.BytesIO(b""),
        button_type="success",
        visible=False,
        width=200
    )

    btn_download_postos = pn.widgets.FileDownload(
        label="📥 Baixar Postos Utilizados",
        filename="postos_utilizados.csv",
        callback=lambda: io.BytesIO(b""),
        button_type="success",
        visible=False,
        width=200
    )

    def agrupar_postos(df_postos, periodo):
        df_postos = df_postos.copy()
        df_postos["data"] = pd.to_datetime(df_postos["data"])
        df_postos["periodo"] = df_postos["data"].dt.to_period(periodo)

        colunas_ids = [col for col in df_postos.columns if col not in ["data", "periodo"]]
        df_agg = {"data": df_postos.groupby("periodo")["data"].min()}

        for col in colunas_ids:
            df_agg[col] = df_postos.groupby("periodo")[col].agg(
                lambda x: x.mode().iloc[0] if not x.mode().empty else None
            )

        df_postos_agregado = pd.concat(df_agg.values(), axis=1)
        df_postos_agregado.columns = ["data"] + colunas_ids
        return df_postos_agregado.reset_index(drop=True)

    import asyncio

    async def buscar_async(event=None):
        def update_progress(value, color='primary'):
            progresso.value = value
            progresso.bar_color = color

        update_progress(5, 'primary')
        resultado_nome.object = "⏳ Carregando..."
        tabela_resultado.value = pd.DataFrame()
        tabela_postos.value = pd.DataFrame()
        btn_download_serie.visible = False
        btn_download_postos.visible = False
        await asyncio.sleep(0.1)

        try:
            texto = input_coords.value
            n_postos = int(limite.value) if limite.value.isdigit() else 74
            di = data_inicio.value
            df = data_fim.value
            gran = granularidade.value

            if not texto or not di or not df:
                resultado_nome.object = "⚠️ Preencha todas as informações."
                update_progress(100, 'danger')
                return

            update_progress(20, 'info')
            await asyncio.sleep(0.1)

            def progresso_callback(v):
                update_progress(v, 'warning')
                pn.state.curdoc.add_next_tick_callback(lambda: None)

            df_result, df_postos_usados = buscar_series_para_multiplos_pontos(
                texto, di, df, n_postos, progresso_callback=progresso_callback
            )

            update_progress(80, 'warning')
            await asyncio.sleep(0.1)

            if not df_result.empty:
                df_result["data"] = pd.to_datetime(df_result["data"])
                df_postos_usados["data"] = pd.to_datetime(df_postos_usados["data"])

                if gran == "mensal":
                    df_result = df_result.groupby(df_result["data"].dt.to_period("M")).sum(numeric_only=True).round(1).reset_index()
                    df_result["data"] = df_result["data"].dt.to_timestamp()
                    df_postos_usados = agrupar_postos(df_postos_usados, "M")
                    for col in df_postos_usados.columns:
                        if col != "data":
                            df_postos_usados[col] = df_postos_usados[col].astype("Int64")

                elif gran == "anual":
                    df_result = df_result.groupby(df_result["data"].dt.to_period("Y")).sum(numeric_only=True).round(1).reset_index()
                    df_result["data"] = df_result["data"].dt.to_timestamp()
                    df_postos_usados = agrupar_postos(df_postos_usados, "Y")
                    for col in df_postos_usados.columns:
                        if col != "data":
                            df_postos_usados[col] = df_postos_usados[col].astype("Int64")

                update_progress(90, 'success')
                await asyncio.sleep(0.1)

                df_result["data"] = df_result["data"].dt.strftime("%d-%m-%Y")
                df_postos_usados["data"] = df_postos_usados["data"].dt.strftime("%d-%m-%Y")

                tabela_resultado.value = df_result
                tabela_postos.value = df_postos_usados
                resultado_nome.object = f"**✅ Série {gran} gerada com sucesso.**"

                os.makedirs("temp", exist_ok=True)

                nome_serie = f"serie_{gran}_multipontos.csv"
                df_result.to_csv(f"temp/{nome_serie}", index=False, sep=";")
                df_postos_usados.to_csv("temp/postos_utilizados.csv", index=False, sep=";")

                btn_download_serie.callback = lambda: io.BytesIO(open(f"temp/{nome_serie}", "rb").read())
                btn_download_serie.filename = nome_serie
                btn_download_postos.callback = lambda: io.BytesIO(open("temp/postos_utilizados.csv", "rb").read())

                btn_download_serie.visible = True
                btn_download_postos.visible = True
            else:
                resultado_nome.object = "⚠️ Nenhum dado encontrado."
                update_progress(100, 'warning')

        except Exception as e:
            resultado_nome.object = f"❌ Erro: {e}"
            update_progress(100, 'danger')

        finally:
            update_progress(100, 'success')

    buscar_btn.on_click(lambda event: asyncio.ensure_future(buscar_async(event)))

    def gerar_mapa_interativo():
        m = folium.Map(location=[-5.4984, -39.3206], zoom_start=7, width='50%', height='450px')

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

        MousePosition().add_to(m)

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
                        <button onclick="navigator.clipboard.writeText('${id},' + ${lat} + ',' + ${lon})">🔗</button>
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
        return pn.pane.HTML(m._repr_html_(), height=450, sizing_mode='stretch_width')

    return pn.Column(
        pn.pane.Markdown("## 🔍 Buscar série para múltiplos pontos"),
        pn.Row(
            pn.Column(
                input_coords,
                pn.Row(data_inicio, data_fim),
                granularidade,
                pn.Row(buscar_btn, progresso),
                sizing_mode="stretch_width",
            ),
            pn.Column(
                pn.pane.Markdown("### 🗺️ Mapa 🗺️"),
                gerar_mapa_interativo(),
                sizing_mode="stretch_width",
            ),
            sizing_mode="stretch_width",
        ),
        resultado_nome,
        pn.Row(btn_download_serie, btn_download_postos, sizing_mode="stretch_width"),
        sizing_mode="stretch_width",
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

# Adicionando ao aplicativo
add_applications(
    {
        '/': painel_busca_multiplos_pontos(),
    },
    app=app,
)