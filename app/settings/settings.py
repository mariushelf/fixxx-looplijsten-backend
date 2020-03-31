import os
from os.path import join
from datetime import timedelta
import json
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from api.planner.const import EXAMPLE_PLANNER_SETTINGS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',

    # Third party apps
    'rest_framework',            # utilities for rest apis
    'rest_framework.authtoken',  # TODO: remove once all user management is done using Grip
    'django_filters',            # for filtering rest endpoints
    'drf_yasg',                  # for generating real Swagger/OpenAPI 2.0 specifications
    'constance',
    'constance.backends.database',  # for dynamic configurations in admin
    'mozilla_django_oidc',       # for authentication

    # Your apps
    'api.users',
    'api.itinerary',
    'api.cases',
    'api.accesslogs',
    'api.planner',
    'api.fraudprediction'
)

# https://docs.djangoproject.com/en/2.0/topics/http/middleware/
MIDDLEWARE = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'mozilla_django_oidc.middleware.SessionRefresh',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'api.accesslogs.middleware.LoggingMiddleware'
)

ROOT_URLCONF = 'api.urls'


SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
WSGI_APPLICATION = 'app.wsgi.application'

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

ADMINS = (
    ('Author', 'p.curet@mail.amsterdam.nl'),
)

# Database
DEFAULT_DATABASE_NAME = 'default'
BWV_DATABASE_NAME = 'bwv'

DATABASES = {
    DEFAULT_DATABASE_NAME: {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST', 'database'),
        'PORT': '5432',
    },
    BWV_DATABASE_NAME: {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('BWV_DB_NAME'),
        'USER': os.environ.get('BWV_DB_USER'),
        'PASSWORD': os.environ.get('BWV_DB_PASSWORD'),
        'HOST': os.environ.get('BWV_DB_HOST', 'bwv_db'),
        'PORT': '5432',
    }
}

# General
APPEND_SLASH = False
TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-us'
# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.normpath(join(os.path.dirname(BASE_DIR), 'static'))

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.normpath(join(os.path.dirname(BASE_DIR), 'media'))

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
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


# Password Validation
# https://docs.djangoproject.com/en/2.0/topics/auth/passwords/#module-django.contrib.auth.password_validation
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

# Custom user app
AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'api.users.auth.OIDCAuthenticationBackend',
)

# Django Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S%z',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

# Mail
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS and allowed hosts
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS').split(',')
CORS_ORIGIN_WHITELIST = os.environ.get('CORS_ORIGIN_WHITELIST').split(',')
CORS_ORIGIN_ALLOW_ALL = False


SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'scheme': 'bearer'
        }
    }
}

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CONSTANCE_ALLOW_DATA_ACCESS_KEY = 'ALLOW_DATA_ACCESS'
CONSTANCE_BRK_AUTHENTICATION_TOKEN_KEY = 'BRK_AUTHENTICATION_TOKEN'
CONSTANCE_BRK_AUTHENTICATION_TOKEN_EXPIRY_KEY = 'BRK_AUTHENTICATION_TOKEN_EXPIRY'
CONSTANCE_MAPS_KEY = 'MAPS_KEY'
CONSTANCE_PLANNER_SETTINGS_KEY = 'PLANNER_SETTINGS'

CONSTANCE_CONFIG = {
    CONSTANCE_ALLOW_DATA_ACCESS_KEY: (True, 'Allow data to be accesible through the API'),
    CONSTANCE_BRK_AUTHENTICATION_TOKEN_KEY: ('', 'Authentication token for accessing BRK API'),
    CONSTANCE_BRK_AUTHENTICATION_TOKEN_EXPIRY_KEY: ('', 'Expiry date for BRK API token'),
    CONSTANCE_MAPS_KEY: ('', 'Maps API Key'),
    CONSTANCE_PLANNER_SETTINGS_KEY: (json.dumps(EXAMPLE_PLANNER_SETTINGS),
                                     'Settings for planning and generating lists')
}

# Error logging through Sentry
sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[DjangoIntegration()]
)

OIDC_RP_CLIENT_ID = os.environ.get('OIDC_RP_CLIENT_ID')
OIDC_RP_CLIENT_SECRET = os.environ.get('OIDC_RP_CLIENT_SECRET')
OIDC_USERNAME_ALGO = 'api.users.utils.generate_username'

ACCEPTANCE_OIDC_REDIRECT_URL = 'https://acc.top.amsterdam.nl/authentication/callback'
PRODUCTION_OIDC_REDIRECT_URL = 'https://top.amsterdam.nl/authentication/callback'

OIDC_REDIRECT_URL = ACCEPTANCE_OIDC_REDIRECT_URL

if ENVIRONMENT == 'production':
    OIDC_REDIRECT_URL = PRODUCTION_OIDC_REDIRECT_URL

OIDC_RP_SIGN_ALGO = 'RS256'

OIDC_RP_SCOPES = 'openid'

OIDC_VERIFY_SSL = True

# https://auth.grip-on-it.com/v2/rjsfm52t/oidc/idp/.well-known/openid-configuration
OIDC_OP_AUTHORIZATION_ENDPOINT = os.getenv('OIDC_OP_AUTHORIZATION_ENDPOINT',
                                           'https://auth.grip-on-it.com/v2/rjsfm52t/oidc/idp/authorize')
OIDC_OP_TOKEN_ENDPOINT = os.getenv('OIDC_OP_TOKEN_ENDPOINT',
                                   'https://auth.grip-on-it.com/v2/rjsfm52t/oidc/idp/token')
OIDC_OP_USER_ENDPOINT = os.getenv('OIDC_OP_USER_ENDPOINT',
                                  'https://auth.grip-on-it.com/v2/rjsfm52t/oidc/idp/userinfo')
OIDC_OP_JWKS_ENDPOINT = os.getenv('OIDC_OP_JWKS_ENDPOINT',
                                  'https://auth.grip-on-it.com/v2/rjsfm52t/oidc/idp/.well-known/jwks.json')

OIDC_USE_NONCE = True


DEBUG_LOG_FILE = os.path.join(BASE_DIR, 'debug.log')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG'
        },
        'applogfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': DEBUG_LOG_FILE,
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
        },
    },
    'loggers': {
        'woonfraude_model': {
            'handlers': ['applogfile', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'api': {
            'handlers': ['applogfile', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'mozilla_django_oidc': {
            'handlers': ['console'],
            'level': 'DEBUG'
        },
    }
}


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=4),
    # We don't refresh tokens yet, so we set refresh lifetime to zero
    'REFRESH_TOKEN_LIFETIME': timedelta(seconds=0),
}

ACCESS_LOG_EXEMPTIONS = (
    '/looplijsten/health',
)

# BRK Access request settings
BRK_ACCESS_CLIENT_ID = os.getenv('BRK_ACCESS_CLIENT_ID')
BRK_ACCESS_CLIENT_SECRET = os.getenv('BRK_ACCESS_CLIENT_SECRET')
BRK_ACCESS_URL = os.getenv('BRK_ACCESS_URL')
BRK_API_OBJECT_EXPAND_URL = os.getenv(
    'BRK_API_OBJECT_EXPAND_URL', 'https://acc.api.data.amsterdam.nl/brk/object-expand/')

BAG_API_SEARCH_URL = 'https://api.data.amsterdam.nl/atlas/search/adres/'

# Settings to improve security
is_secure_environment = True if ENVIRONMENT in ['production', 'acceptance'] else False
# NOTE: this is commented out because currently the internal health check is done over HTTP
# SECURE_SSL_REDIRECT = is_secure_environment
SESSION_COOKIE_SECURE = is_secure_environment
CSRF_COOKIE_SECURE = is_secure_environment
DEBUG = not is_secure_environment
SECURE_HSTS_SECONDS = 60
SECURE_HSTS_INCLUDE_SUBDOMAINS = is_secure_environment
SECURE_HSTS_PRELOAD = is_secure_environment
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

FRAUD_PREDICTION_CACHE_DIR = os.path.normpath(join(os.path.dirname(BASE_DIR), 'fraud_prediction_cache'))
# Secret key for accessing fraud prediction scoring endpoint
FRAUD_PREDICTION_SECRET_KEY = os.environ.get('FRAUD_PREDICTION_SECRET_KEY')

CELERY_BROKER = 'amqp://admin:mypass@rabbit:5672'
