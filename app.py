from flask import Flask, render_template, request, jsonify, url_for
from pymongo import MongoClient
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
from hacktu.authorization import *
from hacktu.group_payment import *
import os
import re

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bablu@hacktu'
SESSION_COOKIE_SECURE = True
PORT = 5000

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)

@app.route('/', methods=['GET'])
def home_page():
    try:
        user_data = get_user_data(session['user'])
        name = user_data['name']
        return render_template('index.html', user = session['user'], name = name, mandates=fetch_user_mandates(session['user']), mandate_requests=fetch_user_mandate_requests(session['user']),
        uninitialized_groups=fetch_user_uninitialized_groups(session['user']),balance=user_data['balance'])
    except:
        return redirect('/login')

    
@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    try:
        if not session["state"] == request.args["state"]:
            pass
            # return render_template('notification.html', message='Error') # State does not match!
        credentials = flow.credentials
    except KeyError:
        credentials = flow.credentials
    return login_user(get_token(), credentials)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/group/create", methods=['GET', 'POST'])
def group_initiation():
    if request.method == 'POST':
        dataGet = request.get_json(force=True)
        members = None if not dataGet['members'] else dataGet['members']
        create_group(session['user'], dataGet['base_amount'], members=members)
        return jsonify(True) 
    return render_template('add_group.html')


@app.route("/group/join", methods=['GET', 'POST'])
def group_join():
    if request.method == 'POST':
        dataGet = request.get_json(force=True)
        join_group(dataGet['group_code'], session['user'])
        return jsonify(True) 
    return render_template('join_group.html')

@app.route("/group/approve", methods=['POST'])
def approve_user_mandate():
    dataGet = request.get_json(force=True)
    approve_mandate(dataGet['group_code'])
    return jsonify(True)

@app.route("/group/pay", methods=['GET', 'POST'])
def group_payment_portal():
    if request.method == 'POST':
        dataGet = request.get_json(force=True)
        temp_mem = []
        for mem in dataGet['members'].split():
            temp_mem.append(mem.replace(',',''))
        members = None if (len(dataGet['members'].split()) == 0) else temp_mem
        pay_merchant(dataGet['upi'], dataGet['amount'], dataGet['group_code'], members)
        return jsonify(True)
    user = get_user_data(session['user'])
    return render_template('payment.html', mandates = user['mandates'])


@app.route("/group/initialize", methods = ['GET','POST'])
def group_initialize_fnc():
    if request.method == 'POST':
        dataGet = request.get_json(force=True)
        initialize_group(dataGet['group_code'])
        return jsonify(True)
    return render_template('initialize_group.html')

if __name__ == "__main__":
    app.run(debug=True, port=PORT)

    