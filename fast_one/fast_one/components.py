import panel as pn

def municipio_selector(store):
    return pn.widgets.Select(
        name="Município",
        options=list(store.municipio_data["municipio"].unique()),
        value=store.municipio_data["municipio"].iloc[0],
    )
