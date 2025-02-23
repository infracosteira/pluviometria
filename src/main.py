from http import HTTPStatus
import panel as pn

from fastapi import FastAPI
from panel.io.fastapi import add_applications

from .data_store import DataStore, get_turbines
from .views import Indicators, Histogram, Table
from .app import App
from .schemas import Message, UserSchema

app = FastAPI()

data = get_turbines()
ds = DataStore(data=data, filters=["p_year", "p_cap", "t_manu"])
panel_app = App(data_store=ds,
                views=[Indicators, Histogram, Table],
                title="Windturbine Explorer")


@app.get("/", response_model=Message)
async def read_root():
    return {"message": "Hello World!"}


@app.post("/users/", status_code=HTTPStatus.CREATED)
async def create_user(user: UserSchema):
    print(f"Creating user: {user}")
    return user


@app.get("/test")
async def test():
    print("Test route works!")
    return {"message": "Test route works!"}


def create_panel_app():
    slider = pn.widgets.IntSlider(name='Slider', start=0, end=10, value=3)
    return slider.rx() * '⭐'


def create_another_panel_app():
    text_input = pn.widgets.TextInput(name='Text Input',
                                      placeholder='Type here...')
    return text_input


add_applications(
    {
        "/panel_app1": create_panel_app,
        "/panel_app2": pn.Column('I am a Panel object!'),
        "/panel_app3": panel_app.servable(),
    },
    app=app)
