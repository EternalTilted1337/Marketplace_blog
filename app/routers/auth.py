from fastapi import  Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.db import get_db
from app.models import Users
from app.schemas import UserRead, UserCreate, Token

router = APIRouter(
    prefix='/auth',
    tags= ["Authentication"]
)


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя",
)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Создает нового пользователя в базе данных, хэширует пароль и проверяет уникальность email.
    """
    query = select(Users).where(Users.email == user_data.email)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Такой пользователь уже существует")
    new_user = Users(
        email=str(user_data.email), hashed_password=hash_password(user_data.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/token", response_model=Token, summary="Получение токена для авторизации")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    Проверяет учетные данные и выдает JWT токен для авторизации по эндпоинтам
    """
    result = await db.execute(select(Users).where(Users.email == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}