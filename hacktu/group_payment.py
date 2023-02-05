from flask import session, redirect
from pymongo import MongoClient
from .config import *
from .transactions import *
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
    group_members = members.split(',') if members else []
    group_members.insert(0, group_owner)
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

    owner = user_collection.find_one({'_id':group_owner})
    uninit = owner['uninitialized_groups']

    uninit.append(group_code)
    user_collection.update_one({'_id':group_owner}, {'$set':{'uninitialized_groups':uninit}})
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

def initialize_group(group_code):
    group = groups_collection.find_one({'_id':group_code})
    owner = group['group_owner']
    owner = user_collection.find_one({'_id':owner})
    uninit = owner['uninitialized_groups']
    uninit.remove(group_code)
    user_collection.update_one({'_id':owner}, {'$set':{'uninitialized_groups':uninit}})
    for member in group['group_members']:
        mandate_request(member, group_code, group['base_amount']/len(group['group_members']))
 
def finalize_group(group_code):
    pass

def pay_merchant(merchant_id, amount, group_code, members=None):
    group = groups_collection.find_one({'_id':group_code})
    members = group['group_members'] if not members else members
    balance = group['group_balance']
    balance-=int(amount)
    member_balances = group['member_balance']
    for member in members:
        member_balance = member_balances[member]
        member_balance -= int(amount)/len(members)
        member_balances[member] = member_balance

        user = user_collection.find_one({'_id':member})
        user_mandates = user['mandates']
        for mandate in user_mandates:
            if list(mandate.keys())[0] == group_code:
                user_balance = mandate[list(mandate.keys())[0]]
                user_balance-= int(amount)/len(members)
                user_mandates.remove(mandate)
                user_mandates.append({group_code:user_balance})
        user_collection.update_one({'_id':member}, {'$set':{'balance':user['balance']-(int(amount)/len(members)), 'mandates':user_mandates}
                                                            })
    groups_collection.update_one({'_id':group_code}, {'$set':{'member_balance':member_balances, 'group_balance':int(balance)}})


def fetch_user_mandates(user):
    user = user_collection.find_one({'_id':user})
    return user['mandates']

def fetch_user_mandate_requests(user):
    user = user_collection.find_one({'_id':user})
    return user['mandate_requests']

def fetch_user_uninitialized_groups(user):
    user = user_collection.find_one({'_id':user})
    return user['uninitialized_groups']