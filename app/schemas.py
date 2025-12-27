from datetime import datetime

from pydantic import BaseModel, Field, EmailStr

class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=50)
    content: str
    is_published : bool = False

class ArticleRead(ArticleCreate):
    id : int
    created_at : datetime
    model_config = {"from_attributes" : True}

class UserBase(BaseModel):
    email : EmailStr
class UserCreate(UserBase):
    password : str
class UserRead(UserBase):
    id : int

    class Config:
        from_attributes = True

