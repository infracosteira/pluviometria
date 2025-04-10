import panel as pn
from .df_import import load_data
from .data_store import DataStore
from .components import municipio_selector


def build_dashboard():
    municipios, postos, registros = load_data()
    store = DataStore(
        municipio_data=municipios,
        posto_data=postos,
        registro_data=registros
    )

    municipio_widget = pn.widgets.Select(
        name="Município",
        options=list(municipios["municipio"]),
        value=municipios["municipio"].iloc[0],
    )

    # vincula valor do widget ao atributo
    bind_municipio = pn.bind(lambda v: setattr(store, "selected_municipio", v), municipio_widget)

    # gera a tabela a partir do método .get_filtered_registro()
    tabela = pn.bind(
    lambda df: pn.widgets.Tabulator(df, height=400, pagination="remote", page_size=10),
    store.get_filtered_registro
)


    return pn.Column(
        "# 🌧️ Painel Pluviométrico",
        municipio_widget,
        bind_municipio,
        tabela
    )
