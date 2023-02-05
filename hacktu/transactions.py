from flask import session, redirect
from pymongo import MongoClient
from .config import DB_STRING
from random import random

client = MongoClient(DB_STRING)
db = client.hacktu
user_collection = db['users']
groups_collection = db['active_groups']


def mandate_request(source, destination, amount):
    user = user_collection.find_one({'_id':source})
    user_mandate_requests = user['mandate_requests']
    user_mandate_requests.append({destination:amount})
    user_collection.update_one({'_id':source}, {'$set':{'mandate_requests':user_mandate_requests}})

def approve_mandate(destination):
    user = user_collection.find_one({'_id':session['user']})
    user_mandate_requests = user['mandate_requests']
    user_mandates = user['mandates']
    user_balance = user['balance']
    for request in user_mandate_requests:

        if list(request.keys())[0] == destination:
            user_mandates.append(request)
            user_mandate_requests.remove(request)
            user_balance -= request[list(request.keys())[0]]
            amount = request[list(request.keys())[0]]
    user_collection.update_one({'_id':session['user']}, {'$set':{'mandate_requests':user_mandate_requests, 'mandates':user_mandates, 'balance':user_balance}})

    group = groups_collection.find_one({'_id':destination})
    group_balance = group['group_balance']
    group_balance+=amount
    member_balance = group['member_balance']
    member_balance[session['user']] += amount
    groups_collection.update_one({'_id':destination}, {'$set':{'group_balance':group_balance, 'member_balance':member_balance}})


def release_mandate(member, group_code, amount):
    user = user_collection.find_one({'_id':member})
    user_mandates = user['mandates']
    balance = user['balance'] + amount
    uninitialized_mandates = user['uninitialized_groups']
    for mandate in user_mandates:
        if list(mandate.keys())[0] == group_code:
            user_mandates.remove(mandate)
    if group_code in uninitialized_mandates:
        uninitialized_mandates.remove(group_code)
    user_collection.update_one({'_id':member}, {'$set':{'balance':balance, 'mandates':user_mandates, 'uninitialized_groups':uninitialized_mandates}})

