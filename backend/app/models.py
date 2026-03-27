"""SQLAlchemy ORM models for Monster, Map, and MapSpawn."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class Monster(Base):
    __tablename__ = "monsters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=0)
    hp: Mapped[int] = mapped_column(Integer, default=0)
    base_exp: Mapped[int] = mapped_column(Integer, default=0)
    job_exp: Mapped[int] = mapped_column(Integer, default=0)
    atk_min: Mapped[int] = mapped_column(Integer, default=0)
    atk_max: Mapped[int] = mapped_column(Integer, default=0)
    defense: Mapped[int] = mapped_column(Integer, default=0)
    magic_defense: Mapped[int] = mapped_column(Integer, default=0)
    element: Mapped[str] = mapped_column(String(30), default="Neutral1")
    race: Mapped[str] = mapped_column(String(30), default="Formless")
    size: Mapped[str] = mapped_column(String(10), default="Medium")
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    spawns: Mapped[list["MapSpawn"]] = relationship(back_populates="monster")


class Map(Base):
    __tablename__ = "maps"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    spawns: Mapped[list["MapSpawn"]] = relationship(
        back_populates="map", cascade="all, delete-orphan"
    )


class MapSpawn(Base):
    __tablename__ = "map_spawns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    map_id: Mapped[str] = mapped_column(ForeignKey("maps.id"), nullable=False)
    monster_id: Mapped[int] = mapped_column(ForeignKey("monsters.id"), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, default=0)

    map: Mapped["Map"] = relationship(back_populates="spawns")
    monster: Mapped["Monster"] = relationship(back_populates="spawns")
