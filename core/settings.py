import os
from pathlib import Path

# Only load .env if not on Render deployment
if 'RENDER' not in os.environ:
    from dotenv import load_dotenv
    # Load .env file from project root (where manage.py is)
    BASE_DIR = Path(__file__).resolve().parent.parent
    env_path = BASE_DIR / '.env'
    load_dotenv(env_path)
    print("DEBUG: Loading .env from:", env_path)
    print("DEBUG: SUPABASE_URL:", os.getenv('SUPABASE_URL'))
    print("DEBUG: SUPABASE_DB_HOST:", os.getenv('SUPABASE_DB_HOST'))
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    print("DEBUG: Running on Render - .env loading skipped")

# Use environment variables or defaults
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key-for-dev')
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'data_app',
    'crispy_forms',
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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
        'DIRS': [BASE_DIR / 'templates'],
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

# Database Configuration - SQLite for deployment, PostgreSQL for local
if 'RENDER' in os.environ:
    # Use SQLite on Render (for deployment)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
    print("DEBUG: Using SQLite database for deployment")
else:
    # Use PostgreSQL locally (for development with Supabase)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('SUPABASE_DB_NAME'),
            'USER': os.getenv('SUPABASE_DB_USER'),
            'PASSWORD': os.getenv('SUPABASE_DB_PASSWORD'),
            'HOST': os.getenv('SUPABASE_DB_HOST'),
            'PORT': os.getenv('SUPABASE_DB_PORT', '5432'),
        }
    }
    print("DEBUG: Using PostgreSQL database for local development")

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'