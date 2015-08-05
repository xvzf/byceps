from datetime import timedelta
from pathlib import Path


DEBUG = False
MAX_CONTENT_LENGTH = 4000000
PERMANENT_SESSION_LIFETIME = timedelta(14)
PROPAGATE_EXCEPTIONS = True
SECRET_KEY = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
SESSION_COOKIE_SECURE = True

LOCALE = 'de_DE.UTF-8'
LOCALES_FORMS = ['de']

SQLALCHEMY_DATABASE_URI = 'postgresql+pg8000://byceps:boioioing@127.0.0.1/byceps'
SQLALCHEMY_ECHO = False

REDIS_URL = 'unix:///var/run/redis/redis.sock?db=0'

PATH_DATA = Path('./data')
PATH_USER_AVATAR_IMAGES = PATH_DATA / 'users/avatars'

MODE = 'public'
PARTY = 'example-party-1'

BOARD_TOPICS_PER_PAGE = 10
BOARD_POSTINGS_PER_PAGE = 10

MAIL_DEBUG = False
MAIL_DEFAULT_SENDER = 'BYCEPS <noreply@example.com>'
MAIL_SUPPRESS_SEND = False
