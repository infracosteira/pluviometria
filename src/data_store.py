import param
import panel as pn
import pandas as pd
from panel.viewable import Viewer
from panel.io import hold

CARD_STYLE = """
:host {{
  box-shadow: rgba(50, 50, 93, 0.25) 0px 6px 12px -2px, rgba(0, 0, 0, 0.3) 0px 3px 7px -3px;
  padding: {padding};
}} """

TURBINES_URL = "https://assets.holoviz.org/panel/tutorials/turbines.csv.gz"


@pn.cache(ttl=15 * 60)
def get_turbines():
    return pd.read_csv(TURBINES_URL)


class DataStore(Viewer):
    data = param.DataFrame()
    filters = param.List(constant=True)

    def __init__(self, **params):
        super().__init__(**params)
        self._widgets = self.create_widgets()
        self._update_filtered_data()

    def create_widgets(self):
        """Creates filter widgets based on the data type of each filter column."""
        widgets = []
        for filt in self.filters:
            dtype = self.data.dtypes[filt]
            if dtype.kind == "f":  # Numeric column: use RangeSlider
                min_val = self.data[filt].min()
                max_val = self.data[filt].max()
                widget = pn.widgets.RangeSlider(name=filt,
                                                start=min_val,
                                                end=max_val)
            else:  # Categorical column: use MultiChoice
                options = self.data[filt].unique().tolist()
                widget = pn.widgets.MultiChoice(name=filt, options=options)
            widgets.append(widget)

        return widgets

    @hold()  # Batch updates to prevent WebSocket overload
    def _update_filtered_data(self, event=None):
        """Updates filtered data based on widget values."""
        dfx = self.param.data.rx()
        for widget in self._widgets:
            filt = widget.name
            if isinstance(widget, pn.widgets.RangeSlider):
                condition = dfx[filt].between(*widget.rx())
            else:
                options = self.data[filt].unique().tolist()
                condition = dfx[filt].isin(widget.rx().rx.where(
                    widget, options))

            dfx = dfx[condition]

        # Update reactive properties
        self.filtered = dfx
        self.count = dfx.rx.len()
        self.total_capacity = dfx.t_cap.sum()
        self.avg_capacity = dfx.t_cap.mean()
        self.avg_rotor_diameter = dfx.t_rd.mean()
        self.top_manufacturers = (dfx.groupby(
            "t_manu").p_cap.sum().sort_values().iloc[-10:].index.to_list())

    def filter(self, ):
        return

    def __panel__(self):
        return pn.Column("## Filters",
                         *self._widgets,
                         stylesheets=[CARD_STYLE.format(padding="5px 10px")],
                         margin=10)
