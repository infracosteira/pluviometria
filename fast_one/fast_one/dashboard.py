import panel as pn
from df_import import load_data
from data_store import DataStore
from .components import municipio_selector

def build_dashboard():
    municipios, postos, registros = load_data()
    store = DataStore(
        municipio_data=municipios,
        posto_data=postos,
        registro_data=registros
    )

    selector = pn.bind(lambda v: setattr(store, "selected_municipio", v), municipio_selector(store))

    tabela = pn.bind(
        lambda df: pn.widgets.Tabulator(df, height=400, pagination="remote", page_size=10),
        store.filtered_registro
    )

    return pn.Column(
        "# 🌧️ Painel de Pluviometria",
        pn.Row(selector),
        "## Registros por Município",
        tabela,
        sizing_mode="stretch_width"
    )
