import panel as pn
from .df_import import load_municipio, load_posto, load_registro
from fastapi import FastAPI
from panel.io.fastapi import add_applications

app = FastAPI()

@app.get('/')
def read_root():
    return {'message': 'Hello from Pluviometria App!'}

municipio = load_municipio()
posto = load_posto()
registro = load_registro()


row_slider = pn.widgets.IntSlider(name='Nº linhas', start=1, end=max(len(municipio), len(posto), len(registro)), value=10)


municipio_search = pn.widgets.TextInput(name='Search Municipio', placeholder='Type to search...')
posto_search = pn.widgets.TextInput(name='Search Posto', placeholder='Type to search...')
registro_search = pn.widgets.TextInput(name='Search Registro', placeholder='Type to search...')

posto_column_select = pn.widgets.Select(name='Select Column', options=list(posto.columns))


def get_filtered_dataframe(df, search, rows, column=None):
    if search:
        if column:
            df = df[df[column].astype(str).str.contains(search, case=False, na=False)]
        else:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False, na=False).any(), axis=1)]
    return df.head(rows)


municipio_pane = pn.bind(
    lambda search, rows: pn.pane.DataFrame(get_filtered_dataframe(municipio, search, rows), name='Municipio'),
    municipio_search, row_slider
)
posto_pane = pn.bind(
    lambda search, rows, column: pn.pane.DataFrame(get_filtered_dataframe(posto, search, rows, column), name='Posto'),
    posto_search, row_slider, posto_column_select
)
registro_pane = pn.bind(
    lambda search, rows: pn.pane.DataFrame(get_filtered_dataframe(registro, search, rows), name='Registro'),
    registro_search, row_slider
)

add_applications(
    {
        '/tabelas': pn.Row(
            pn.Column('Municipio', municipio_search, row_slider, municipio_pane),
            pn.Column('Posto', posto_search, posto_column_select, posto_pane),
            pn.Column('Registro', registro_search, registro_pane),
        ),
    },
    app=app,
)
