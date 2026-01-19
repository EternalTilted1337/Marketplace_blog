from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


# Токен
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Юзер
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    model_config = {"from_attributes": True}


# Категории
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)


class CategoryRead(CategoryCreate):
    id: int

    model_config = {"from_attributes": True}


# Ариткуль


class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=50)
    content: str
    category_id: int
    image_url: Optional[str] = None
    is_published: bool = False


class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=50)
    content: Optional[str] = None
    category_id: Optional[int] = None
    is_published: Optional[bool] = None


class ArticleRead(BaseModel):
    id: int
    title: str
    content: str
    image_url: Optional[str]
    is_published: bool
    created_at: datetime
    updated_at: datetime
    category_id: int | None
    owner_id: int
    category: Optional[CategoryRead] = None
    owner: Optional[UserRead] = None

    model_config = {"from_attributes": True}


# Комменты
class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class CommentRead(CommentBase):
    id: int
    content: str
    article_id: int
    author_id: int

    model_config = {"from_attributes": True}
