from os import environ
from .common import *



SECRET_KEY = environ['SECRET_KEY']

DEBUG = False

ALLOWED_HOSTS = []