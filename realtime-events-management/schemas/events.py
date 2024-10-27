import datetime
import pydantic

from schemas import users as users_schemas


class BaseEvent(pydantic.BaseModel):
    id: int
    title: str
    date_time: datetime.datetime
    duration: datetime.timedelta
    address: str
    is_cancelled: bool

    @pydantic.field_serializer('duration')
    def serialize_duration(self, duration: datetime.timedelta):
        total_minutes = int(duration.total_seconds() / 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        if minutes == 0:
            return f"{hours} hours"
        elif hours == 0:
            return f"{minutes} minutes"
        else:
            return f"{hours}:{minutes:02d} hours"

    @pydantic.field_serializer('date_time')
    def serialize_datetime(self, dt: datetime):
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    class Config:
        from_attributes = True


class EventDetail(BaseEvent):
    organizer: users_schemas.User
    participants: list[users_schemas.User]


class EventCreate(pydantic.BaseModel):
    title: str
    date_time: str
    duration: int
    address: str

    @pydantic.field_validator('date_time')
    @classmethod
    def validate_date_time(cls, value: str):
        try:
            return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValueError("Invalid date time format")

    @pydantic.field_validator('duration')
    @classmethod
    def validate_duration(cls, value: int):
        return datetime.timedelta(minutes=value)
