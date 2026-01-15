from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=50)
    content: str
    is_published: bool = False


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True


class ArticleRead(ArticleCreate):
    id: int
    created_at: datetime
    owner: UserRead | None = None
    model_config = {"from_attributes": True}


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class CommentRead(CommentBase):
    id: int
    content: str
    article_id: int
    author_id: int

    class Config:
        from_attributes = True
