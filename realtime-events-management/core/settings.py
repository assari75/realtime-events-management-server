from pathlib import Path

from decouple import AutoConfig

BASE_DIR = Path(__name__).resolve().parent
config = AutoConfig(search_path = BASE_DIR)


DATABASE_URL = config('DATABASE_URL', default='sqlite:///db.sqlite3')
SECRET_KEY = config('SECRET_KEY', default='')
ACCESS_TOKEN_EXPIRE_MINUTES = config('ACCESS_TOKEN_EXPIRE_MINUTES', default=60*24, cast=int)
