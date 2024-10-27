import datetime
import httpx

import pytest
from fastapi.testclient import TestClient
import sqlalchemy
from sqlalchemy import orm as sa_orm

from core import database
from main import app
from models import users, events


DATABASE_URL = "sqlite:///./test_db.sqlite3"
engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sa_orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[database.get_db] = override_get_db
client = TestClient(app)


@pytest.fixture
def test_db():
    db = next(override_get_db())
    database.Base.metadata.create_all(bind=engine)
    yield db
    database.Base.metadata.drop_all(bind=engine)


@pytest.fixture
def registered_user_data():
    data = {
        "username": "testuser",
        "password": "testpassword",
        "name": "Test User",
    }
    response = client.post("/auth/register", json=data)
    user_id = response.json()["id"]
    return {"id": user_id, **data}


@pytest.fixture
def login_data(registered_user_data: dict) -> dict:
    return {
        "username": registered_user_data["username"],
        "password": registered_user_data["password"]
    }


@pytest.fixture
def access_token(login_data: dict) -> str:
    response = client.post("/auth/token", data=login_data)
    data = response.json()
    return data["access_token"]


@pytest.fixture
def request_headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def event_data() -> dict:
    return {
        "title": "Test Event",
        "date_time": "2024-10-27 13:00:00",
        "duration": 60,
        "address": "Test Address"
    }


@pytest.fixture
def create_event_response(event_data: dict, test_db: sa_orm.Session, request_headers: dict) -> httpx.Response:
    response = client.post(
        "/events/create",
        json=event_data,
        headers=request_headers
    )
    return response


def test_create_event(event_data: dict, test_db: sa_orm.Session, create_event_response: httpx.Response):
    assert create_event_response.status_code == 200
    data = create_event_response.json()
    event_id = data["id"]
    event = test_db.query(events.Event).get(event_id)
    assert event.title == event_data["title"]
    assert event.date_time == datetime.datetime.strptime(event_data["date_time"], "%Y-%m-%d %H:%M:%S")
    assert event.duration == datetime.timedelta(minutes=event_data["duration"])
    assert event.address == event_data["address"]


def test_cancel_event(test_db: sa_orm.Session, request_headers: dict):
    event_data = {
        "title": "Test Event",
        "date_time": "2024-10-27 13:00:00",
        "duration": 60,
        "address": "Test Address"
    }
    create_event_response = client.post(
        "/events/create",
        json=event_data,
        headers=request_headers
    )
    event_id = create_event_response.json()["id"]
    event = test_db.query(events.Event).get(event_id)
    cancel_event_response = client.post(
        f"/events/{event_id}/cancel",
        headers=request_headers
    )
    assert cancel_event_response.status_code == 200
    test_db.refresh(event)
    assert event.is_cancelled


def test_join_event(test_db: sa_orm.Session, request_headers: dict, registered_user_data: dict):
    event_data = {
        "title": "Test Event",
        "date_time": "2024-10-27 13:00:00",
        "duration": 60,
        "address": "Test Address"
    }
    create_event_response = client.post(
        "/events/create",
        json=event_data,
        headers=request_headers
    )
    event_id = create_event_response.json()["id"]
    join_event_response = client.post(
        f"/events/{event_id}/join",
        headers=request_headers
    )
    assert join_event_response.status_code == 200
    event_participants = test_db.query(events.EventParticipant).filter(
        events.EventParticipant.event_id == event_id,
        events.EventParticipant.user_id == registered_user_data["id"]
    ).all()
    assert len(event_participants) == 1
