import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import exceptions
import sys
import os
from .models import *
#from pyrebase import pyrebase

from django.contrib.staticfiles.storage import staticfiles_storage

cred = credentials.Certificate(staticfiles_storage.path('aerial-reality-357305-68fb6471bf0d.json'))
default_app = firebase_admin.initialize_app(cred)
