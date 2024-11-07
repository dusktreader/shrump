from __future__ import annotations

from uuid import UUID, uuid4
from typing import Any

from inflection import tableize
from pendulum.datetime import DateTime as PendulumDateTime
from snick import conjoin
from sqlalchemy import ForeignKey, Integer, String, Uuid, DateTime, Enum
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column, relationship, selectinload
from sqlalchemy.dialects.postgresql import JSONB

from api.constants import EventKind


class Base(DeclarativeBase):
    """
    Base class for models.

    References:
        https://docs.sqlalchemy.org/en/20/orm/declarative_mixins.html
    """


class CommonMixin:

    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        return tableize(cls.__name__)

    def _iter_cols(self):
        for col in inspect(self.__class__).columns.keys():
            yield (col, getattr(self, col))

    def __str__(self):
        primary_keys = [pk.name for pk in inspect(self.__class__).primary_key]
        primary_key_str = ", ".join([f"{pk}: {getattr(self, pk)}" for pk in primary_keys])
        return conjoin(
            f"{self.__class__.__name__}: ({primary_key_str})",
            *[f"{k}: {v}" for (k, v) in self._iter_cols() if k not in primary_keys],
            join_str="\n  ",
        )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class Identity(CommonMixin, Base):
    uuid: Mapped[UUID] = mapped_column(Uuid, nullable=False, index=True, default=uuid4)
    owner: Mapped[str] = mapped_column(String, nullable=False, index=True)

    events: Mapped[list[Event]] = relationship(
        "Event",
        back_populates="identity",
        lazy="raise",
        uselist=True,
    )


class Event(CommonMixin, Base):
    identity_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{Identity.__tablename__}.id"), nullable=True)
    kind: Mapped[EventKind] = mapped_column(
        Enum(EventKind, native_enum=False),
        nullable=False,
    )
    data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[PendulumDateTime] = mapped_column(DateTime(timezone=True), nullable=False, default=PendulumDateTime.utcnow)

    identity: Mapped[Identity] = relationship(
        "Identity",
        back_populates="events",
        lazy="raise",
    )
