# core/settings.py

import os
from pathlib import Path
from datetime import timedelta
from algosdk import account, mnemonic

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-wj4ml9onym0^7)knn6h*32idv11ti^rdhup2g418m=jr)6m8l#'
DEBUG = True
ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'userauth',
    'tailoring',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'csp',
    'drf_yasg',
]

# Additional installed apps
INSTALLED_APPS += ['rest_framework_simplejwt.token_blacklist']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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
WSGI_APPLICATION = 'core.wsgi.application'

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

# core/settings.py
SITE_URL = "http://localhost:8000"  # Use the correct base URL for your application

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '10/minute',     
        'anon': '5/minute',
        'login': '3/minute',       
    }
}

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    'https://your-frontend-domain.com',  # Replace with your frontend domain
    'http://localhost:3000',  # For local development
]
CORS_ALLOW_CREDENTIALS = True

# Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'smtp.example.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-email-password'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Security
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# CSP Settings
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", 'https://trusted-scripts.com')
CSP_STYLE_SRC = ("'self'", 'https://trusted-styles.com')

# Algorand Configuration
ALGOD_ADDRESS = 'https://testnet-api.algonode.network'
ALGORAND_CREATOR_ADDRESS = 'T7H3C3BZSX5YS3SKCEFJKJABDXKVY75JMEZSO7FQI7Z4BGOYUGXYLAW6KU'
ALGORAND_CREATOR_PRIVATE_KEY = os.getenv("ALGORAND_CREATOR_PRIVATE_KEY")

# Generate a new Algorand account if no private key is provided
if not ALGORAND_CREATOR_PRIVATE_KEY:
    private_key, address = account.generate_account()
    mnemonic_phrase = mnemonic.from_private_key(private_key)

    # Log the generated account details for secure storage
    print("Generated new Algorand account:")
    print("Address:", address)
    print("Mnemonic Phrase:", mnemonic_phrase)

    # Assign generated credentials for development
    ALGORAND_CREATOR_ADDRESS = address
    ALGORAND_CREATOR_PRIVATE_KEY = private_key

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'WARNING',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        '': {  # Root logger
            'handlers': ['console', 'mail_admins'],
            'level': 'DEBUG',
        },
    },
    'ADMINS': [('Admin', 'admin@example.com')],
}

# Custom User Model
AUTH_USER_MODEL = 'userauth.CustomUser'