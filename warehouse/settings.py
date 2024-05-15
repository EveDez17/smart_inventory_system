"""
Django settings for warehouse project.

Generated by 'django-admin startproject' using Django 5.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os

from pathlib import Path
from dotenv import load_dotenv

from environ import Env
env = Env()
Env.read_env()

ENVIRONMENT = env('ENVIRONMENT', default='production')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


env_path = load_dotenv(os.path.join(BASE_DIR, '.env'))
load_dotenv(env_path)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')


# SECURITY WARNING: Don't run with debug turned on in production!
if ENVIRONMENT == 'development':
    DEBUG = True
else:
    DEBUG = False

# List of allowed host/domain names for this site
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'smartinventorysystem.up.railway.app']

CSRF_TRUSTED_ORIGINS = ['https://smartinventorysystem.up.railway.app']


# Enforce HTTP Strict Transport Security (HSTS) for 1 year
SECURE_HSTS_SECONDS = 31536000  # 1 year

# Redirect all HTTP requests to HTTPS
SECURE_SSL_REDIRECT = True

# Use secure-only session cookies
SESSION_COOKIE_SECURE = True

# Use secure-only CSRF cookies
CSRF_COOKIE_SECURE = True

# Include subdomains in HTTP Strict Transport Security (HSTS) header
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Preload your site in the browser's HSTS preload list
SECURE_HSTS_PRELOAD = True




# Application definition

INSTALLED_APPS = [
    'cloudinary_storage',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'warehouse.users.apps.UsersConfig',
    'warehouse.storage',
    'warehouse.inventory.apps.InventoryConfig',
    'warehouse.inbound.apps.InboundConfig',
    'warehouse.outbound',
    'warehouse.dashboard_global.apps.DashboardGlobalConfig',
    'rest_framework',
    'crispy_forms',
    'crispy_bootstrap5',
    'simple_history',
    'channels',
    'cloudinary',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
]

ROOT_URLCONF = 'warehouse.urls'

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

WSGI_APPLICATION = 'warehouse.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases



import os
import dj_database_url

# Default configuration using SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Override with Railway's PostgreSQL in production or if locally testing the Railway database
ENVIRONMENT = os.getenv('ENVIRONMENT_VARIABLE', 'development')
USE_RAILWAY_DB_LOCALLY = os.getenv('USE_RAILWAY_DB_LOCALLY', 'False') == 'False'

if ENVIRONMENT == 'production' or USE_RAILWAY_DB_LOCALLY:
    DATABASES['default'] = dj_database_url.parse(os.getenv('DATABASE_URL'))



# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = "Europe/London"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


load_dotenv()


CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

STATIC_URL = '/static/'
STATICFILES_STORAGE = 'cloudinary_storage.storage.StaticHashedCloudinaryStorage'

MEDIAFILES_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'




REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
}

# Media files
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.RawMediaCloudinaryStorage'

#model_path = os.path.join(settings.MEDIA_ROOT, 'demand_forecast_model.joblib')
#joblib.dump(model, model_path)

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Define allowed template packs for crispy forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

# Set the default template pack for crispy forms
CRISPY_TEMPLATE_PACK = "bootstrap5"

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}



# Celery Settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Using Redis as a broker
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # Using Redis to store task results
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

#Custom User
AUTH_USER_MODEL = 'users.User'

LOGIN_REDIRECT_URL = 'dashboard:dashboard'  # Adjust if namespace:path is different
LOGOUT_REDIRECT_URL = 'users:login'  

#Custom Cookie
CSRF_FAILURE_VIEW = 'warehouse.users.views.csrf_failure'

# Development environment settings
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Emails will be printed to the console
    SITE_DOMAIN = 'localhost'
    EMAIL_PROTOCOL = 'http'
else:
    # Production environment settings
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.your-email-host.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'your-email@example.com'
    EMAIL_HOST_PASSWORD = 'your-email-password'
    DEFAULT_FROM_EMAIL = 'webmaster@example.com'
    SITE_DOMAIN = 'yourdomain.com'
    EMAIL_PROTOCOL = 'https'
    


