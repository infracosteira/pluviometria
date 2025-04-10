import param

class DataStore(param.Parameterized):
    municipio_data = param.DataFrame()
    posto_data = param.DataFrame()
    registro_data = param.DataFrame()
    selected_municipio = param.String(default=None)

    @param.depends("selected_municipio")
    def get_filtered_registro(self):
        if self.selected_municipio:
            postos = self.posto_data[self.posto_data["municipio"] == self.selected_municipio]
            ids = postos["id_posto"].values
            return self.registro_data[self.registro_data["id_posto"].isin(ids)]
        return self.registro_data