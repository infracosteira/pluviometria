from pydantic import BaseModel, EmailStr


class Message(BaseModel):
    message: str

class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str = None
    disabled: bool = None