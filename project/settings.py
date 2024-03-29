"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 2.1.15.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from django.utils.translation import ugettext_lazy as _
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'gs0nq4+wr2z-&su1mli^qpozv0xu4xs0f36@a-ji7wx7$s5r+0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DEBUG_PROPAGATE_EXCEPTIONS = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'jet.dashboard',
    'jet',
    'rest_framework.authtoken',
    'rest_framework',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'nip',
    'etl',
    'basic_information',
    'authentication',
    'tabbed_admin',
    'channels',
    'bootstrap4',

    'django_plotly_dash.apps.DjangoPlotlyDashConfig',
    'dpd_static_support',
]
TABBED_ADMIN_USE_JQUERY_UI = True
CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django_plotly_dash.middleware.BaseMiddleware',

]

ROOT_URLCONF = 'project.urls'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
X_FRAME_OPTIONS = 'SAMEORIGIN'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Add the templates directory to the DIR option:
        'DIRS': [os.path.join(BASE_DIR, "templates"), ],
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

WSGI_APPLICATION = 'project.wsgi.application'
ASGI_APPLICATION = 'project.routing.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }
from project.db import get_db

DATABASES = get_db()
# DATABASES = {
#     'default': {
#         'NAME': 'nip',
#         'ENGINE': 'sql_server.pyodbc',
#         'HOST': 'TUMS-NIP',
#         'USER': 'sa',
#         'PASSWORD': 'VI?9NHuvpj',
#
#         'OPTIONS': {
#                     'driver': 'SQL Server Native Client 11.0',
#                 }
#     }
# }
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'nip',
#         'USER': 'postgres',
#         'PASSWORD': '1qaz!QAZ',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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

# Celery - prefix with CELERY_
CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_TASK_TRACK_STARTED = True
CELERY_ALWAYS_EAGER = True

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'fa' # 'en_us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'nip', 'static'),
#     ]

# Caching - demo uses redis as this is present due to channels use
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
        # 'rest_framework.permissions.IsAuthenticated',
        # 'rest_framework.permissions.IsAdminUser',
     ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'EXCEPTION_HANDLER': 'api.utils.custom_exception_handler',
    'PAGE_SIZE': 100
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "dpd-demo"
    }
}

# Channels config, to use channel layers

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379), ],
        },
    },
}

# Staticfiles finders for locating dash app assets and related files

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',

    'django_plotly_dash.finders.DashAssetFinder',
    'django_plotly_dash.finders.DashComponentFinder',
    'django_plotly_dash.finders.DashAppDirectoryFinder',
]

# Plotly components containing static content that should
# be handled by the Django staticfiles infrastructure

PLOTLY_COMPONENTS = [
    'dash_core_components',
    'dash_html_components',
    'dash_bootstrap_components',
    'dash_renderer',
    'dpd_components',
    'dpd_static_support',
]

###################### jet settings ##########################

# JET_INDEX_DASHBOARD = 'dashboard.CustomIndexDashboard'
# JET_INDEX_DASHBOARD = 'jet.dashboard.dashboard.DefaultIndexDashboard'
JET_DEFAULT_THEME = 'light-gray'
JET_THEMES = [
    {
        'theme': 'default', # theme folder name
        'color': '#44b78b', # color of the theme's button in user menu
        'title': 'Default' # theme title
    },
    {
        'theme': 'green',
        'color': '#47bac1',
        'title': 'Green'
    },
    {
        'theme': 'light-green',
        'color': '#2faa60',
        'title': 'Light Green'
    },
    {
        'theme': 'light-violet',
        'color': '#a464c4',
        'title': 'Light Violet'
    },
    {
        'theme': 'light-blue',
        'color': '#5EADDE',
        'title': 'Light Blue'
    },
    {
        'theme': 'light-gray',
        'color': '#222',
        'title': 'Light Gray'
    }
]

JET_SIDE_MENU_COMPACT = False
JET_CHANGE_FORM_SIBLING_LINKS = False
# JET_SIDE_MENU_ITEMS = [  # A list of application or custom item dicts
#     {'label': _('General'), 'app_label': 'core', 'items': [
#         {'name': 'help.question'},
#         {'name': 'pages.page', 'label': _('Static page')},
#         {'name': 'city'},
#         {'name': 'validationcode'},
#         {'label': _('Analytics'), 'url': 'http://example.com', 'url_blank': True},
#     ]},
#     {'label': _('Users'), 'items': [
#         {'name': 'core.user'},
#         {'name': 'auth.group'},
#         {'name': 'core.userprofile', 'permissions': ['core.user']},
#     ]},
#     {'app_label': 'banners', 'items': [
#         {'name': 'banner'},
#         {'name': 'bannertype'},
#     ]},
# ]