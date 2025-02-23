import param
from panel.viewable import Viewer
from .data_store import DataStore

import panel as pn
from panel.io import hold

pn.extension("tabulator",
             "vega",
             throttled=True,
             defer_load=True,
             loading_indicator=True)


class App(Viewer):
    data_store = param.ClassSelector(class_=DataStore)

    title = param.String()

    views = param.List()

    def __init__(self, **params):
        super().__init__(**params)
        self._views = pn.FlexBox(
            *(view(data_store=self.data_store) for view in self.views),
            loading=self.data_store.filtered.rx.updating())
        self._template = pn.template.BootstrapTemplate(title=self.title)
        self._template.sidebar.append(self.data_store)
        self._template.main.append(self._views)

    def servable(self):
        return self._template.servable()

    def __panel__(self):
        return pn.Row(self.data_store, self._views)
