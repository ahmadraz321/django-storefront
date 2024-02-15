from .common import *

DEBUG = True

SECRET_KEY = 'django-insecure-*!jexz2z04^*p(amq*__)-3usu2s+a$(h##ttveu11i#=e6^*7'




DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'storefront2',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT':5432 
    }
}