# -*- coding: utf-8 -*-
import os

class Config:
    # Прямая строка подключения без посредников
    SQLALCHEMY_DATABASE_URI = 'DATABASE_URL'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'SECRET_KEY'