from pymongo import MongoClient
from flask import redirect, url_for
import json

host = 'localhost'
port = 27017

def get_db_connection():
    try:
        return MongoClient(host, port)
    except Exception:
        return redirect(url_for('logout'))
