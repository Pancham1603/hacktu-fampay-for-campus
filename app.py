from flask import Flask, render_template, request, jsonify, url_for
from pymongo import MongoClient
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
from hacktu.authorization import *
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bablu@hacktu'
SESSION_COOKIE_SECURE = True
PORT = 5000

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
    # redirect_uri = 'https://e338-223-185-7-171.ngrok.io/callback'
)

@app.route('/', methods=['GET'])
def home_page():
    return render_template('index.html', user = session)

    
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


@app.route("/group")
def group_initiation():
    pass

if __name__ == "__main__":
    app.run(debug=True, port=PORT)