import json

from decouple import config
from storages.backends.s3boto3 import S3Boto3Storage

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

# for s3 bucket
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_DEFAULT_ACL = config('AWS_DEFAULT_ACL')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}


# s3 static settings
class StaticStorage(S3Boto3Storage):
    bucket_name = AWS_STORAGE_BUCKET_NAME
    location = 'static'


STATIC_LOCATION = 'static'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'
STATICFILES_STORAGE = "main.settings.production.StaticStorage"


# s3 public media settings
class MediaStorage(S3Boto3Storage):
    bucket_name = AWS_STORAGE_BUCKET_NAME
    location = 'media'


MEDIA_LOCATION = 'media'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIA_LOCATION}/'
DEFAULT_FILE_STORAGE = "main.settings.production.MediaStorage"

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 30
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
