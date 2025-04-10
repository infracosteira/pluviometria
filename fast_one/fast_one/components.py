import panel as pn

def municipio_selector(store):
    return pn.widgets.Select(
        name="Município",
        options=list(store.municipio_data["municipio"]),
        value=store.municipio_data["municipio"].iloc[0],
        width=300,
        sizing_mode="fixed",
        **store.param.selected_municipio
    )
