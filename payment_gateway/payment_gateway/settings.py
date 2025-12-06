from pathlib import Path
import os
import dj_database_url  # Required for Render DB
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load local .env file (if it exists)
load_dotenv(BASE_DIR / '.env')

# ============================
# 🔐 SECURITY
# ============================
SECRET_KEY = os.getenv('SECRET_KEY', "django-insecure-default-key-change-in-production")

# Default to False in production if variable is missing
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.onrender.com',  # Allows all render subdomains
]

# Add any specific hosts from env
allowed_hosts_env = os.getenv('ALLOWED_HOSTS', '')
if allowed_hosts_env:
    ALLOWED_HOSTS.extend([host.strip() for host in allowed_hosts_env.split(',') if host.strip()])


# ============================
# 📦 INSTALLED APPS
# ============================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "accounts",
    "payments",
]

# ============================
# ⚙️ MIDDLEWARE
# ============================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "payment_gateway.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "payment_gateway.wsgi.application"


# ============================
# 🗄️ DATABASE CONFIGURATION (HYBRID)
# ============================

# 1. Default to Local PostgreSQL settings
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv('DB_NAME', 'payment_gateway_db'),
        "USER": os.getenv('DB_USER', 'postgres'),
        "PASSWORD": os.getenv('DB_PASSWORD', ''),
        "HOST": os.getenv('DB_HOST', 'localhost'),
        "PORT": os.getenv('DB_PORT', '5432'),
    }
}

# 2. If running on Render (DATABASE_URL exists), override with Render DB
# This handles the connection automatically using dj_database_url
if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        ssl_require=True
    )


# ============================
# 🔐 PASSWORDS & I18N
# ============================
AUTH_PASSWORD_VALIDATORS = [] # Add validators if needed for production

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ============================
# 🎨 STATIC FILES (Whitenoise Config)
# ============================
STATIC_URL = "static/"
# This is where collectstatic will put files for Render to serve
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 

# Enable Whitenoise compression and caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = []


# ============================
# 🚪 LOGIN SETTINGS
# ============================
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================
# 💳 PAYMENT & API KEYS
# ============================
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '')
FRONTEND_URL = os.getenv('FRONTEND_URI', 'http://localhost:5173')


# ============================
# 🔐 CSRF & COOKIE CONFIGURATION
# ============================

# CSRF cookie configuration
# For local development (HTTP), use 'Lax'. For production (HTTPS), use 'None'
if DEBUG:
    CSRF_COOKIE_SAMESITE = 'Lax'  # Works with HTTP in local dev
    CSRF_COOKIE_SECURE = False
else:
    CSRF_COOKIE_SAMESITE = 'None'  # Required for cross-origin in production
    CSRF_COOKIE_SECURE = True  # Required when SameSite=None

CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'
CSRF_COOKIE_DOMAIN = None  # Allow cross-domain cookies

CSRF_TRUSTED_ORIGINS = [
    FRONTEND_URL,
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'https://*.razorpay.com',
    'https://*.onrender.com',
    'https://payment-gateway-integration-ni9i4kmro.vercel.app',
    'https://payment-gateway-integration-zeta.vercel.app',
    'https://payment-gateway-integration-ashen.vercel.app',
]

# For local development use 'Lax' For production (HTTPS), use 'None'
if DEBUG:
    SESSION_COOKIE_SAMESITE = 'Lax'  # Works with HTTP in local dev
    SESSION_COOKIE_SECURE = False
else:
    SESSION_COOKIE_SAMESITE = 'None' 
    SESSION_COOKIE_SECURE = True 

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_DOMAIN = None
SESSION_COOKIE_AGE = 1209600
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

CORS_ALLOWED_ORIGINS = [
    FRONTEND_URL,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://payment-gateway-integration-ni9i4kmro.vercel.app",
    "https://payment-gateway-integration-zeta.vercel.app",
    "https://payment-gateway-integration-ashen.vercel.app",
]

CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = ['Content-Type', 'X-CSRFToken']
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'payment_gateway.authentication.CsrfExemptSessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}