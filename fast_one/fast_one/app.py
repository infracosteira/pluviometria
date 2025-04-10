import datetime as dt
import pandas as pd
import panel as pn
from fastapi import FastAPI
from panel.io.fastapi import add_applications
from http import HTTPStatus
from .schemas import Message, UserSchema
from .dashboard import build_dashboard
import panel as pn

app = FastAPI()

@app.get("/", response_model=Message)
async def read_root():
    return {"message": "Hello from Pluviometria App!"}

@app.post("/users/", status_code=HTTPStatus.CREATED)
async def create_user(user: UserSchema):
    print(f"Creating user: {user}")
    return user

add_applications(
    {
        "/dashboard": build_dashboard(),
    },
    app=app
)

