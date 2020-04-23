import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".."
)

SECRET_KEY = '2t0^$qpt@3$^5d!x-jyd7zb)g1)3fhi458g-7$mi(6@loq-(kk'

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CELERY_BROKER_URL = "redis://localhost:6379"
