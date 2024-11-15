
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-o9o6$v$ief8yrof4-yg&ode!*5(b4#^k2y58m+7wf0lo8&_8pw'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


CORS_ALLOW_ALL_ORIGINS = True
ALLOWED_HOSTS = ['*']
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://cvo-test.emiit.ru",
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth.registration',
    'corsheaders',
    'storages',
    'users',
    'programs',
]

SITE_ID = 1

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'constructor_vo_server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [BASE_DIR / 'templates'],
        'DIRS': [os.path.join(BASE_DIR, 'constructor_vo_server/templates'),os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'constructor_vo_server.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# пользователь
AUTH_USER_MODEL = 'users.CustomUser'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

REST_AUTH = {
    'USE_JWT': True,
    'REGISTER_SERIALIZER': 'users.serializers.CustomRegisterSerializer',
    'USER_DETAILS_SERIALIZER': 'users.serializers.CustomUserDetailsSerializer',
    'PASSWORD_RESET_SERIALIZER': 'users.serializers.PasswordResetSerializer',
}

AUTH_PASSWORD_VALIDATORS = []


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=365*10),  # Например, сделать токен действительным на 10 лет
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=365*10),
    'ROTATE_REFRESH_TOKENS': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

FRONT_END = os.getenv('FRONT_END')
#  подключаем движок filebased.EmailBackend
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
SERVER_EMAIL = os.getenv('EMAIL_HOST_USER')
DEFAULT_FROM_EMAIL = os.getenv('EMAIL_HOST_USER')


ACCOUNT_EMAIL_VERIFICATION = 'none'

ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False



STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        # "OPTIONS": {
        #     "access_key": "51bbbd2c29d04e0c861c241dc3396a51",
        #     "secret_key": "eb57ca42a781403991969e6c058fb47f",
        #     "bucket_name": "cvotest1",
        #     "region_name": "gis-1",
        #     "endpoint_url": "https://s3.gis-1.storage.selcloud.ru",
        # },
        "OPTIONS": {
            "access_key": os.getenv('AWS_ACCESS_KEY_ID'),
            "secret_key": os.getenv('AWS_SECRET_ACCESS_KEY'),
            "bucket_name": os.getenv('AWS_STORAGE_BUCKET_NAME'),
            "region_name": os.getenv('AWS_REGION_NAME'),
            "endpoint_url": os.getenv('AWS_ENDPOINT_URL'),
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Дополнительные параметры S3
AWS_S3_FILE_OVERWRITE = False  # Чтобы файлы с одинаковыми именами не перезаписывались
# AWS_DEFAULT_ACL = 'public-read'  # Делает файлы публичными

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Конфигурация статических файлов (опционально, если нужно хранить статические файлы на S3)
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# MEDIA_URL = f'https://{AWS_S3_ENDPOINT_URL}/media/'


