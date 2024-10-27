
import fastapi
from fastapi import status as fastapi_status
from sqlalchemy import orm as sa_orm
from sqlalchemy.sql import expression

from core import database, ws_manager
from models import events as events_models
from models import users as users_models
from schemas import events as events_schemas

from . import deps

router = fastapi.APIRouter()

@router.get("/", response_model=list[events_schemas.BaseEvent])
def get_events(db: sa_orm.Session = fastapi.Depends(database.get_db)):
    return db.query(events_models.Event).all()


@router.post("/create", response_model=events_schemas.BaseEvent)
async def create_event(
    event: events_schemas.EventCreate,
    db: sa_orm.Session = fastapi.Depends(database.get_db),
    current_user: users_models.User = fastapi.Depends(deps.get_current_user)
):
    event = events_models.Event(
        **event.model_dump(),
        organizer_id=current_user.id,
        is_cancelled=False
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    event_data = events_schemas.BaseEvent.model_validate(event).model_dump()
    await ws_manager.manager.broadcast(
        "event_created",
        event_data,
    )
    return event


@router.get("/{event_id}", response_model=events_schemas.EventDetail)
def get_event(event_id: int, db: sa_orm.Session = fastapi.Depends(database.get_db)):
    event_query = expression.select(
        events_models.Event.id,
        events_models.Event.title,
        events_models.Event.date_time,
        events_models.Event.duration,
        events_models.Event.address,
        events_models.Event.is_cancelled,
        users_models.User.id.label("organizer_id"),
        users_models.User.name,
    ).join(users_models.User, events_models.Event.organizer_id == users_models.User.id)\
    .where(events_models.Event.id == event_id)
    event = db.execute(event_query).first()
    if not event:
        raise fastapi.HTTPException(
            status_code=fastapi_status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    participants_query = expression.select(
        users_models.User.id,
        users_models.User.name,
    ).join(events_models.EventParticipant, users_models.User.id == events_models.EventParticipant.user_id)\
    .where(events_models.EventParticipant.event_id == event_id)
    participants = db.execute(participants_query).all()
    event_data = {
        "id": event.id,
        "title": event.title,
        "date_time": event.date_time,
        "duration": event.duration,
        "address": event.address,
        "is_cancelled": event.is_cancelled,
        "organizer": {
            "id": event.organizer_id,
            "name": event.name
        },
        "participants": participants
    }
    return events_schemas.EventDetail.model_validate(event_data)


@router.post("/{event_id}/cancel")
async def cancel_event(
    event_id: int,
    db: sa_orm.Session = fastapi.Depends(database.get_db),
    current_user: users_models.User = fastapi.Depends(deps.get_current_user)
):
    event = verify_event(event_id, db)
    if event.organizer_id != current_user.id:
        raise fastapi.HTTPException(
            status_code=fastapi_status.HTTP_403_FORBIDDEN,
            detail="You are not the organizer of this event"
        )
    event.is_cancelled = True
    db.commit()
    await ws_manager.manager.broadcast(
        "event_canceled",
        {"id": event_id},
    )
    return {"message": "Event cancelled successfully"}


@router.post("/{event_id}/join")
async def join_event(
    event_id: int,
    db: sa_orm.Session = fastapi.Depends(database.get_db),
    current_user: users_models.User = fastapi.Depends(deps.get_current_user)
):
    verify_event(event_id, db)
    exists = db.query(events_models.EventParticipant).filter(
        events_models.EventParticipant.event_id == event_id,
        events_models.EventParticipant.user_id == current_user.id
    ).exists()
    if db.query(exists).scalar():
        raise fastapi.HTTPException(
            status_code=fastapi_status.HTTP_400_BAD_REQUEST,
            detail="You have already joined the event"
        )
    event_participant = events_models.EventParticipant(
        event_id=event_id,
        user_id=current_user.id
    )
    db.add(event_participant)
    db.commit()
    db.refresh(event_participant)
    await ws_manager.manager.broadcast(
        "joined_event",
        {
            "id": event_id,
            "participant": {
                "id": current_user.id,
                "name": current_user.name
            }
        },
    )
    return {"message": "Joined event successfully"}


@router.post("/{event_id}/leave")
async def leave_event(
    event_id: int,
    db: sa_orm.Session = fastapi.Depends(database.get_db),
    current_user: users_models.User = fastapi.Depends(deps.get_current_user)
):
    verify_event(event_id, db)
    exists = db.query(events_models.EventParticipant).filter(
        events_models.EventParticipant.event_id == event_id,
        events_models.EventParticipant.user_id == current_user.id
    ).exists()
    if not db.query(exists).scalar():
        raise fastapi.HTTPException(
            status_code=fastapi_status.HTTP_400_BAD_REQUEST,
            detail="You have not joined the event"
        )
    db.query(events_models.EventParticipant).filter(
        events_models.EventParticipant.event_id == event_id,
        events_models.EventParticipant.user_id == current_user.id
    ).delete()
    db.commit()
    await ws_manager.manager.broadcast(
        "left_event",
        {
            "id": event_id,
            "participant": {
                "id": current_user.id,
                "name": current_user.name
            }
        },
    )
    return {"message": "Left event successfully"}


def verify_event(event_id, db):
    event = db.query(events_models.Event).filter(
        events_models.Event.id == event_id,
        events_models.Event.is_cancelled == False,
    ).first()
    if not event:
        raise fastapi.HTTPException(
            status_code=fastapi_status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event
