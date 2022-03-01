"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 3.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os 
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1do2016=xxzvod-k#q%g3hmmt6na)ortj^o2@ln@4vtjc9s#@$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


#django-allauth関係。django.contrib.sitesで使用するSITE_IDを指定する
SITE_ID = 1
#django-allauthログイン時とログアウト時のリダイレクトURL
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'


#################django-allauthでのメール認証設定ここから###################

#djangoallauthでメールでユーザー認証する際に必要になる認証バックエンド
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

#ログイン時の認証方法はemailとパスワードとする
ACCOUNT_AUTHENTICATION_METHOD   = "email"

#ログイン時にユーザー名(ユーザーID)は使用しない
ACCOUNT_USERNAME_REQUIRED       = "False"

#ユーザー登録時に入力したメールアドレスに、確認メールを送信する事を必須(mandatory)とする
ACCOUNT_EMAIL_VARIFICATION  = "mandatory"

#ユーザー登録画面でメールアドレス入力を要求する(True)
ACCOUNT_EMAIL_REQUIRED      = True


#ここにメール送信設定を入力する(Sendgridを使用する場合)
"""
EMAIL_BACKEND       = "sendgrid_backend.SendgridBackend"
DEFAULT_FROM_EMAIL  = "ここにメールアドレスを指定"
SENDGRID_API_KEY    = "ここにAPIキーを指定"
SENDGRID_SANDBOX_MODE_IN_DEBUG = False
"""


#DEBUGがTrueのとき、メールの内容は全て端末に表示させる。開発中はSendgridを使ってメール送信をするのではなく、できるだけターミナルに表示させる
if DEBUG:
    EMAIL_BACKEND   = "django.core.mail.backends.console.EmailBackend"

#CHECK:認証時のメールの本文等の編集は templates/allauth/account/email/ から行うことができる

#################django-allauthでのメール認証設定ここまで###################



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.sites', # ←追加
    'allauth', # ←追加
    'allauth.account', # ←追加
    'allauth.socialaccount', # ←追加

    #カスタムしたユーザーモデルを使う
    'users.apps.UsersConfig',


    #以下2つを追加。
    'cloudinary',
    'cloudinary_storage',


    #DjangoRESTFrameworkをインストールしておく
    # pip install djangorestframework
    'rest_framework',

    #【1/8】TODO:模様を削除する時、自動的に模様の画像も削除してくれる、django_cleanupもインストールしましょう。デフォルトではレコードが削除された時、画像は取り残されます。
    #pip install django-cleanup コマンドでインストールできます。
    "django_cleanup",

    'shop.apps.ShopConfig',
]
#ユーザーモデルとしてusersアプリ内のCustomUserを使用する
AUTH_USER_MODEL = 'users.CustomUser'
#一般ユーザーが新規アカウント登録する時SingupFormを使用する
ACCOUNT_FORMS   = { "signup":"users.forms.SignupForm"}



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ os.path.join(BASE_DIR,"templates"),
                  os.path.join(BASE_DIR,"allauth"),
            ],
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_L10N = True

USE_TZ = True


DEFAULT_AUTO_FIELD='django.db.models.AutoField'



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

#↓追加
if DEBUG:
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]


MEDIA_URL   = "/media/"
MEDIA_ROOT  = os.path.join(BASE_DIR, "media")



#HerokuデプロイとCloudinaryのセット
# https://noauto-nolife.com/post/django-deploy-heroku/
# https://noauto-nolife.com/post/django-deploy-heroku-cloudinary/
if not DEBUG:
    
    # Herokuデプロイ時に必要になるライブラリのインポート
    import django_heroku
    import dj_database_url
    
    # ALLOWED_HOSTSにホスト名)を入力
    ALLOWED_HOSTS = [ 'hogehoge.herokuapp.com' ]
    
    # 静的ファイル配信ミドルウェア、whitenoiseを使用。※順番不一致だと動かないため下記をそのままコピーする。
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ]



    # DBを使用する場合は下記を入力する。
    DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': '',
                'USER': '',
                'PASSWORD': '',
                'HOST': '',
                'PORT': '5432',
                }
            }
    
    db_from_env = dj_database_url.config(conn_max_age=600, ssl_require=True)
    DATABASES['default'].update(db_from_env)
    
    # 静的ファイル(static)の存在場所を指定する。
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')


    import cloudinary
    import cloudinary.uploader
    import cloudinary.api

    CLOUDINARY_STORAGE = { 
            'CLOUD_NAME': "", 
            'API_KEY'   : "", 
            'API_SECRET': "",
            "SECURE"    : True,
            }    

    
    #これは画像だけ(上限20MB)
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    
    #これは動画だけ(上限100MB)
    #DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.VideoMediaCloudinaryStorage'
    
    #これで全てのファイルがアップロード可能(上限20MB。ビュー側でアップロードファイル制限するなら基本これでいい)
    #DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.RawMediaCloudinaryStorage'


