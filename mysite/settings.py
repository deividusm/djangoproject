# Reemplaza TODO tu 'mysite/settings.py' con esto:

import os
from pathlib import Path

# Configuración básica
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-!%-0o5quvw%-=m(^!8cnwzsrw1)sy#jom92*ato&0kv9wxnxcf'
DEBUG = True
ALLOWED_HOSTS = []

# Aplicaciones necesarias
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    
    'ranking',  # <-- TU APLICACIÓN PRINCIPAL
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

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

WSGI_APPLICATION = 'mysite.wsgi.application'

# Base de datos (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Archivos estáticos
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"), # Crea una carpeta 'static' en la raíz
]

# --- ARCHIVOS MULTIMEDIA (Imágenes subidas) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') # Crea una carpeta 'media' en la raíz

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- CONFIGURACIÓN MODERNA DE ALLAUTH ---
ACCOUNT_LOGIN_METHODS = ['email']
ACCOUNT_SIGNUP_FIELDS = ['email', 'username','password1']
ACCOUNT_EMAIL_VERIFICATION = 'none' 
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True

LOGIN_REDIRECT_URL = '/' 
LOGOUT_REDIRECT_URL = '/'
SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# ... (El resto de tu config de Google y Email está bien) ...
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['email', 'profile'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
        'APP': {
            'client_id': '645988951106-pgacroisue6cjp47eheqkvc95ch5l0b7.apps.googleusercontent.com',
            'secret': 'GOCSPX-S2uPHMo4BPkKFkMgrGyeK6hSNnA',
            'key': ''
        }
    }
}
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "proyectoinicialgrupo15@gmail.com"
EMAIL_HOST_PASSWORD = "gndt kdoe wahv kw" # (Ojo, pegué el tuyo, asegúrate que sea correcto)