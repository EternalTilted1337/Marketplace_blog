from datetime import datetime

from sqlalchemy import Text, String, func, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass


class Articles(Base):
    __tablename__ = 'articles'

    id : Mapped[int] = mapped_column(primary_key = True)
    title : Mapped[str] = mapped_column(String(50))
    content : Mapped[str] = mapped_column(Text)
    created_at : Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    is_published : Mapped[bool | None] = mapped_column(default = False)