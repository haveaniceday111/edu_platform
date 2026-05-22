import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# 从环境变量读取 SECRET_KEY
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-本地开发密钥')

# 从环境变量读取 DEBUG，默认为 True（本地开发）
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# 从环境变量读取 ALLOWED_HOSTS
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# 应用注册
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',  # 核心应用
    'crispy_forms',  # 表单美化
    'cloudinary_storage',  # Cloudinary 存储
    'cloudinary',  # Cloudinary SDK
    'whitenoise.runserver_nostatic',  # WhiteNoise 静态文件服务
]

# 权限认证配置
AUTH_USER_MODEL = 'core.User'  # 自定义用户模型
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# 表单美化配置
CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise 静态文件中间件
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'edu_platform.urls'

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

WSGI_APPLICATION = 'edu_platform.wsgi.application'

# 数据库配置
if os.environ.get('DATABASE_URL'):
    # 生产环境：使用 Render 的 PostgreSQL
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600)
    }
else:
    # 本地开发：使用 SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# 密码验证
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==================== 安全设置 ====================

# CSRF Cookie 设置
CSRF_COOKIE_SECURE = False  # 开发环境使用False，生产环境如果使用HTTPS则设为True
CSRF_COOKIE_HTTPONLY = True  # 防止JavaScript访问CSRF Cookie
CSRF_COOKIE_SAMESITE = 'Lax'  # 防止CSRF攻击

# Session Cookie 设置
SESSION_COOKIE_SECURE = False  # 开发环境使用False，生产环境如果使用HTTPS则设为True
SESSION_COOKIE_HTTPONLY = True  # 防止JavaScript访问Session Cookie
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # 关闭浏览器时Session过期

# 安全中间件设置（已包含在MIDDLEWARE中）
# SecurityMiddleware 已启用，提供以下保护：
# - X-Content-Type-Options: nosniff
# - X-Frame-Options: DENY
# - X-XSS-Protection

# 点击劫持保护
X_FRAME_OPTIONS = 'DENY'

# 内容安全策略（可选，根据需要启用）
# CSP_DEFAULT_SRC = ("'self'",)
# CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'", 
#                   "https://cdn.jsdelivr.net",)
# CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net",)
# CSP_FONT_SRC = ("'self'", "https://cdn.jsdelivr.net",)

# ==================== Cloudinary 存储配置 ====================
import cloudinary

if os.environ.get('CLOUDINARY_URL'):
    # 生产环境：使用 Cloudinary
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
    import cloudinary
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET')
    )
    
    # 媒体文件通过 Cloudinary 访问
    MEDIA_URL = os.environ.get('MEDIA_URL', '/media/')
else:
    # 本地开发：使用本地文件系统
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    
    # 本地媒体文件配置
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 静态文件配置
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# 安全设置（生产环境）
if not DEBUG:
    # HTTPS 相关设置
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    # 本地开发设置
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False