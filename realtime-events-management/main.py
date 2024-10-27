from fastapi import FastAPI
from fastapi.middleware import cors

from api.endpoints import auth, events, websocket
from core import database

database.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    cors.CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(websocket.router, tags=["websocket"])
