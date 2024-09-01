import os

class Config:
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'Arjun@2004'
    MYSQL_DB = 'hotel_management'
    SECRET_KEY = os.urandom(24)
