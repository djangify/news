from pathlib import Path
import os
from dotenv import load_dotenv
import pymysql

load_dotenv()
pymysql.install_as_MySQLdb()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'your-secret-key-here')

DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['news.djangify.com', 'localhost', '127.0.0.1']

# Configure CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'https://news.djangify.com').split(',')


SITE_ID = 1


# Application definition

INSTALLED_APPS = [
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_crontab',
    'feeds',
    'core',
    # django-allauth apps
    'allauth',
    'allauth.account',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'news_aggregator.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'news_aggregator.wsgi.application'


# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'news_aggregator'),
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            "use_unicode": True,
            "connect_timeout": 10,
            "autocommit": True,
        }
    }
}

# Static files configuration
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files configuration
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


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


# Admin Details
ADMIN_SITE_HEADER = "Djangify News Aggregator"
ADMIN_SITE_TITLE = "Djangify News Aggregator Admin Portal"
ADMIN_INDEX_TITLE = "Welcome to the Djangify News Aggregator Admin Portal"

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True
 

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Add Crontab settings
CRONJOBS = [
    ('*/30 * * * *', 'django.core.management.call_command', ['fetch_feeds'])
]

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Cache timeout (15 minutes)
CACHE_TTL = 60 * 15

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default authentication
    'allauth.account.auth_backends.AuthenticationBackend',  # Allauth authentication
]

# Allauth configuration
ACCOUNT_LOGIN_METHODS = {'email', 'username'}
ACCOUNT_RATE_LIMITS = {
    'login_failed': {'rate': '5/300s'}  # 5 attempts in 300 seconds
}
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # or 'optional' or 'none'
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_UNIQUE_EMAIL = True

LOGIN_REDIRECT_URL = '/'  # Redirect after login
LOGOUT_REDIRECT_URL = '/'  # Redirect after logout

LOGS_DIR = os.path.join(BASE_DIR, 'logs')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'news_aggregator': {  
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}