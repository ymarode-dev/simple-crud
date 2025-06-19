from pydantic import BaseModel

class LoginData(BaseModel):
    name: str
    password: str

class SignUpData(BaseModel):
    name: str
    email: str
    password: str
