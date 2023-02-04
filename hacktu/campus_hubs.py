from flask import session, redirect
from pymongo import MongoClient
from hacktu.config import DB_STRING
from random import random

client = MongoClient(DB_STRING)
db = client.hacktu
users = db['users']
groups_collection = db['active_groups']