from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app import db


class Translate(db.Model):
    __tablename__ = 'translate'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scenario: Mapped[str] = mapped_column(String(200))
    number: Mapped[int]
    difficulty: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)


class TranslateResource(db.Model):
    __tablename__ = 'translate_resource'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    translate_id: Mapped[int]
    source: Mapped[str] = mapped_column(String(500))
    target: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)


class TranslateAnalysis(db.Model):
    __tablename__ = 'translate_analysis'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    translate_id: Mapped[int]
    source: Mapped[str] = mapped_column(String(500))
    translate: Mapped[str] = mapped_column(String(500))
    suggestion: Mapped[str] = mapped_column(String(2000))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)