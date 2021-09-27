import json

from main.helpers.rds_secrets import get_rds_secret

CORS_ALLOWED_ORIGINS = [
    "http://truck.aptcluster.tech",
    "http://api.truck.aptcluster.tech",
    "http://truck.aptcluster.com",
    "http://api.truck.aptcluster.com",
    "http://localhost:1996",
    "http://127.0.0.1:1996",
]

rds_details: dict = json.loads(get_rds_secret())

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": rds_details.get("username"),
        "PASSWORD": rds_details.get("password"),
        "HOST": rds_details.get("host"),
        "PORT": rds_details.get("port"),
    }
}
