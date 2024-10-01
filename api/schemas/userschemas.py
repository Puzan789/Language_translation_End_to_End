from pydantic import BaseModel


class Createuserrequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ApiKeyCreate(BaseModel):
    pass

class ApiKeyResponse(BaseModel):
    key: str

    class config:
        orm_mode=True


class TranslateRequest(BaseModel):
    text: str

class TranslateResponse(BaseModel):
    translated_text: str

        

# Use orm_mode=True in Pydantic Models When:

#     Sending Data: You need to serialize ORM objects (like SQLAlchemy models) into JSON responses.

# Do Not Use orm_mode=True in Pydantic Models When:

#     Receiving Data: You’re handling incoming data from clients, which is already in dictionary (JSON) format.