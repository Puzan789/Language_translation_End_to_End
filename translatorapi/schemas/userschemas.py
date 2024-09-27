from pydantic import BaseModel


class Createuserrequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str