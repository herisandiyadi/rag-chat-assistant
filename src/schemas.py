from pydantic import BaseModel

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str | None = None
    user_id: int | None = None
    department_id: int | None = None
    role_type: str | None = None
