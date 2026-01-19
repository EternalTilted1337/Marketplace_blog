from datetime import datetime
from sqlalchemy import Text, String, func, DateTime, ForeignKey, Integer, Index, Column, Computed
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Articles(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text)

    image_url: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    is_published: Mapped[bool | None] = mapped_column(default=False)

    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("categories.id"))
    owner: Mapped["Users"] = relationship("Users", back_populates="articles")
    category: Mapped["Categories"] = relationship(
        "Categories", back_populates="articles"
    )

    ts_vector = Column(
        "ts_vector",
        TSVECTOR,
        Computed(
            "to_tsvector('russian', title || ' ' || content)",
            persisted=True,
        ),
    )

    __table_args__ = (
        Index('ix_articles_ts_vector', "ts_vector", postgresql_using='gin'),
    )
    comments: Mapped[list["Comments"]] = relationship(
        "Comments",
        back_populates="article",
        cascade="all, delete-orphan",  # 1. Удалит комменты из базы вместе со статьей
        passive_deletes=True  # 2. Позволит базе самой применить ON DELETE CASCADE
    )


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")
    articles: Mapped[list["Articles"]] = relationship(
        "Articles", back_populates="owner"
    )
    comments: Mapped[list["Comments"]] = relationship(back_populates="author")


class Comments(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    article_id: Mapped[int] = mapped_column(Integer,
        ForeignKey("articles.id", ondelete="CASCADE")
    )
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    article: Mapped["Articles"] = relationship(back_populates="comments")
    author: Mapped["Users"] = relationship(back_populates="comments")


class Categories(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    articles: Mapped[list["Articles"]] = relationship(back_populates="category")


class DeleteArticles(Base):
    __tablename__ = "delete_articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(255))

    deleted_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    original_id: Mapped[int] = mapped_column(Integer)
    owner_id: Mapped[int] = mapped_column(Integer)
