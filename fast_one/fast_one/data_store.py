import param

class DataStore(param.Parameterized):
    municipio_data = param.DataFrame()
    posto_data = param.DataFrame()
    registro_data = param.DataFrame()
    selected_municipio = param.String(default=None)

    @param.depends("selected_municipio")
    def filtered_registro(self):
        if self.selected_municipio:
            postos_ids = self.posto_data[self.posto_data["municipio"] == self.selected_municipio]["id"]
            return self.registro_data[self.registro_data["posto_id"].isin(postos_ids)]
        return self.registro_data
