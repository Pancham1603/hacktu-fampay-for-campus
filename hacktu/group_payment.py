from flask import session, redirect
from pymongo import MongoClient
from config import *
from transactions import *
import random, string

client = MongoClient(DB_STRING)
db = client.hacktu
user_collection = db['users']
groups_collection = db['active_groups']
generated_group_codes = db['generated_group_codes']

def generate_group_code():
    generated_codes = generated_group_codes.find_one({'_id':'codes'})['codes']
    while True:
        code = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6))
        if code not in generated_codes:
            break
    return code

def join_group(group_code, member=None):
    member = session['user'] if not member else member
    group = groups_collection.find_one({'_id':group_code})
    group_members = group['group_members']
    group_members.append(member)
    member_balance = group['member_balance']
    member_balance[member] = 0
    groups_collection.update_one({'_id':group_code}, {'$set':{'group_members':group_members, 'member_balance':member_balance}})

# join_group('J6CbPL', 'pancham1603@gmail.com')
# join_group('J6CbPL', 'pancham160305@gmail.com')

def create_group(group_owner, base_amount, members=None):
    group_code = generate_group_code()
    group_members = [members] if members else []
    group_members.append(group_owner)
    member_balance = {}
    if group_members:
        for member in group_members:
            member_balance[member] = 0
    groups_collection.insert_one({
        '_id': group_code,
        'group_owner': group_owner,
        'base_amount': float(base_amount),
        'group_balance': 0,
        'group_members': [],
        'member_balance':member_balance
    })

    if group_members:
        for member in group_members:
            join_group(group_code, member)
    return group_code

# create_group('pagarwal_be22@thapar.edu', 2000)


def leave_group(group_code, member=None):
    member = session['user'] if not member else member
    group = groups_collection.find_one({'_id':group_code})
    group_members = group['group_members']
    group_members.remove(member)
    groups_collection.update_one({'_id':group_code}, {'$set':{'group_members':group_members}})

    user = user_collection.find_one({'_id':member})
    user_mandates = user['mandates']
    user_mandates.remove(group_code)
    user_collection.update_one({'_id':member}, {'$set': {'mandates':user_mandates}})


# def add_user_in_group(member):
#     group = groups_collection.find_one({'_id':group_code})
#     if session(user) == group['group_owner']:
#         group_members = group['group_members']
#         group_members.append(member)
#         groups_collection.update_one({'_id':group_code}, {'$set':{'group_members':group_members}})
#         return True
#     else:
#         return False


# def remove_user_from_group():
#     group = groups_collection.find_one({'_id':group_code})
#     if session(user) == group['group_owner']:
#         group_members = group['group_members']
#         group_members.remove(member)
#         groups_collection.update_one({'_id':group_code}, {'$set':{'group_members':group_members}})
#         return True
#     else:
#         return False

def initialize_group(group_code):
    group = groups_collection.find_one({'_id':group_code})
    for member in group['group_members']:
        mandate_request(member, group_code, group['base_amount']/len(group['group_members']))

# initialize_group('J6CbPL')

def finalize_group():
    pass

def input_amount():
    pass

def pay_merchant():
    pass

def pay_from_selected_users():
    pass