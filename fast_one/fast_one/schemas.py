from pydantic import BaseModel

class Message(BaseModel):
    message: str

class UserSchema(BaseModel):
    name: str
    email: str
