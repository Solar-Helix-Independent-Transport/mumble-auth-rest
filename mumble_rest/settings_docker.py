import os
from .base import *

SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = False

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost").split(",")
CSRF_TRUSTED_ORIGINS = ["http://localhost", "https://localhost"] + [o for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if o]

ICE_HOST_HOST = os.environ.get("MURMUR_ICE_HOST", "mumble")
ICE_HOST_PORT = os.environ.get("MURMUR_ICE_PORT", "6502")
ICE_HOST = f"Meta:tcp -h {ICE_HOST_HOST} -p {ICE_HOST_PORT} -t 1000"
ICE_SECRET = os.environ.get("ICE_SECRET", "")
ICE_MESSAGESIZE = int(os.environ.get("ICE_MESSAGESIZE", "1024"))

MUMBLE_ROOT = os.path.dirname(os.path.abspath(__file__))
SLICE_FILE = "MumbleServer.ice"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("DB_PATH", str(BASE_DIR / "db.sqlite3")),
    }
}
