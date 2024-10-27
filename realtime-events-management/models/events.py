import datetime

import sqlalchemy as sa
from sqlalchemy import orm as sa_orm

from core import database


__all__ = ["Event", "EventParticipant"]


class Event(database.Base):
    __tablename__ = 'events'

    id: sa_orm.Mapped[int] = sa_orm.mapped_column(primary_key=True)
    title: sa_orm.Mapped[str]
    organizer_id = sa_orm.mapped_column(sa.ForeignKey('users.id'))
    date_time: sa_orm.Mapped[datetime.datetime]
    duration: sa_orm.Mapped[datetime.timedelta]
    address: sa_orm.Mapped[str | None]
    is_cancelled: sa_orm.Mapped[bool]

    def __repr__(self) -> str:
        return f"<Event(id={self.id}, title={self.title})>"


class EventParticipant(database.Base):
    __tablename__ = 'event_participants'
    __table_args__ = (
        sa.UniqueConstraint('event_id', 'user_id', name='unique_event_participant'),
    )

    id: sa_orm.Mapped[int] = sa_orm.mapped_column(primary_key=True)
    event_id = sa_orm.mapped_column(sa.ForeignKey('events.id'))
    user_id = sa_orm.mapped_column(sa.ForeignKey('users.id'))

    def __repr__(self) -> str:
        return f"<EventParticipant(id={self.id}, event_id={self.event_id}, user_id={self.user_id})>"
