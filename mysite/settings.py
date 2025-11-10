import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url  # <--- AÑADE ESTO

# Configuración básica
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-!%-0o5quvw%-=m(^!8cnwzsrw1)sy#jom92*ato&0kv9wxnxcf'
DEBUG = True
ALLOWED_HOSTS = []

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))
# Aplicaciones necesarias
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Necesario para django-allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',  # Para habilitar Google Sign-In
]

# Configuración de middleware sirve para autentificacion y desautorizar funciones dentro del programa
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Middleware necesario para django-allauth
    'allauth.account.middleware.AccountMiddleware',  # Asegúrate de que esta línea esté presente
]

# URLs y plantillas
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

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASES = {
    'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
}


# Validación de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Configuración de internacionalización
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Archivos estáticos
STATIC_URL = 'static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# Configuración de claves primarias
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de Google OAuth
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['email', 'profile'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
        'APP': {
            'client_id': '645988951106-pgacroisue6cjp47eheqkvc95ch5l0b7.apps.googleusercontent.com',  # Reemplaza con tu Client ID
            'secret': 'GOCSPX-S2uPHMo4BPkKFkMgrGyeK6hSNnA',  # Reemplaza con tu Client Secret
            'key': ''  # Si es necesario, agrega la clave aquí
        }
    }
}

# Redirección después del login
LOGIN_REDIRECT_URL = '/hub/'
LOGOUT_REDIRECT_URL = '/'

SOCIALACCOUNT_LOGIN_ON_GET = True

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True        # si quieres login solo por email
ACCOUNT_AUTHENTICATION_METHOD = 'email'  # 'username' | 'email' | 'username_email'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "proyectoinicialgrupo15@gmail.com"
EMAIL_HOST_PASSWORD = "gndt kdoe wahv bxkw"







# Agregar configuración de sitios
SITE_ID = 1  # Asegúrate de que el Site con ID 1 esté configurado en la base de datos

# Autenticación y Backend
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)
TEMPLATES[0]['DIRS'] = [os.path.join(BASE_DIR, 'templates')]