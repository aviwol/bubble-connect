import time
import requests
from flask import Flask, request, redirect, session
import asyncio
from okta_jwt_verifier import JWTVerifier
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

app = Flask(__name__)
app.secret_key = 'SECRETTTT'

client = Client(account_sid, auth_token)
loop = asyncio.get_event_loop()
NUMBERS = {}


def is_access_token_valid(token, issuer, client_id):
    jwt_verifier = JWTVerifier(issuer, client_id, 'api://default')
    try:
        loop.run_until_complete(jwt_verifier.verify_access_token(token))
        return True
    except Exception:
        return False


def is_id_token_valid(token, issuer, client_id, nonce):
    jwt_verifier = JWTVerifier(issuer, client_id, 'api://default')
    try:
        loop.run_until_complete(jwt_verifier.verify_id_token(token, nonce=nonce))
        return True
    except Exception:
        return False

@app.route("/authorization-code/callback")
def callback():
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    code = request.args.get("code")
    if not code:
        return "The code was not returned or is not accessible", 403
    query_params = {'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': "https://okta.benchlabs.xyz/authorization-code/callback"
                    }
    query_params = requests.compat.urlencode(query_params)
    exchange = requests.post(
        "https://oie-8225044.oktapreview.com/oauth2/default/v1/token",
        headers=headers,
        data=query_params,
        auth=(KEY, SECRET),
    ).json()

    # Get tokens and validate
    if not exchange.get("token_type"):
        return "Unsupported token type. Should be 'Bearer'.", 403
    access_token = exchange["access_token"]
    id_token = exchange["id_token"]

    if not is_access_token_valid(access_token, "https://oie-8225044.oktapreview.com/oauth2/default", KEY):
        return "Access token is invalid", 403

    if not is_id_token_valid(id_token, "https://oie-8225044.oktapreview.com/oauth2/default", KEY, NONCE):
        return "ID token is invalid", 403

    # Authorization flow successful, get userinfo and login user
    userinfo_response = requests.get("https://oie-8225044.oktapreview.com/oauth2/default/v1/userinfo",
                                     headers={'Authorization': f'Bearer {access_token}'}).json()

    unique_id = userinfo_response["sub"]
    user_email = userinfo_response["email"]
    user_name = userinfo_response["given_name"]

    # user = User(
    #     id_=unique_id, name=user_name, email=user_email
    # )

    # if not User.get(unique_id):
    #     User.create(unique_id, user_name, user_email)

    # login_user(user)
    data = {
        "number": userinfo_response["phone_number"],
        "name": user_name,
        "email": user_email
    }

    requests.post("https://okta.benchlabs.xyz/update_num", data)
    return "If this window did not close, please close the window and go back to the WhatsApp conversation. <script>window.open('','_self').close();</script>"

@app.route("/login")
def login():
    # get request params
    query_params = {'client_id': KEY,
                    'redirect_uri': "https://okta.benchlabs.xyz/authorization-code/callback",
                    'scope': "openid email profile phone",
                    'state': "123345",
                    'nonce': NONCE,
                    'response_type': 'code',
                    'response_mode': 'query'}

    # build request_uri
    request_uri = "{base_url}?{query_params}".format(
        base_url="https://oie-8225044.oktapreview.com/oauth2/default/v1/authorize",
        query_params=requests.compat.urlencode(query_params)
    )

    return redirect(request_uri)

@app.route('/update_num', methods=['POST'])
def update_number():
    number = request.values["number"]
    NUMBERS[number] = {
        "name": request.values["name"],
        "email": request.values["email"]
    }
    welcome_message = "Welcome {}, you are now authenticated and can view your balance. Would you like to view your balance (yes/no)? ".format(NUMBERS[number]["name"])
    message = client.messages.create(
             body=welcome_message,
             from_="whatsapp:+14155238886",
             to="whatsapp:" + number
         )

    return "ok"

@app.route('/bot', methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower()
    number = request.values["From"].split("whatsapp:")[1]
    resp = MessagingResponse()
    msg = resp.message()

    if number not in NUMBERS.keys():
        msg.body("Welcome to our chatbot! Please login to continue: \n https://okta.benchlabs.xyz/login")
        return str(resp)    
    if incoming_msg == "yes":
        welcome_message = "Okay awesome! Your balance is $100."
    else:
        welcome_message = "That's okay. Next time!"
    msg.body(welcome_message)
    return str(resp) 

if __name__ == "__main__":
    app.run(debug=True, port=5000)import time
import requests
from flask import Flask, request, redirect
import asyncio
from okta_jwt_verifier import JWTVerifier

app = Flask(__name__)

KEY = "0oa15q26n4e2Ux28a1d7"
SECRET = "t7iQEMsuNoQmLNL0c55IrtyGW4_rGJIHXEVjbMEs"
NONCE = 'SampleNonce'
loop = asyncio.get_event_loop()

def is_access_token_valid(token, issuer, client_id):
    jwt_verifier = JWTVerifier(issuer, client_id, 'api://default')
    try:
        loop.run_until_complete(jwt_verifier.verify_access_token(token))
        return True
    except Exception:
        return False


def is_id_token_valid(token, issuer, client_id, nonce):
    jwt_verifier = JWTVerifier(issuer, client_id, 'api://default')
    try:
        loop.run_until_complete(jwt_verifier.verify_id_token(token, nonce=nonce))
        return True
    except Exception:
        return False

@app.route("/authorization-code/callback")
def callback():
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    code = request.args.get("code")
    if not code:
        return "The code was not returned or is not accessible", 403
    query_params = {'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': request.base_url
                    }
    query_params = requests.compat.urlencode(query_params)
    exchange = requests.post(
        "https://oie-8225044.oktapreview.com/oauth2/default/v1/token",
        headers=headers,
        data=query_params,
        auth=(KEY, SECRET),
    ).json()
    
    # Get tokens and validate
    if not exchange.get("token_type"):
        return "Unsupported token type. Should be 'Bearer'.", 403
    access_token = exchange["access_token"]
    id_token = exchange["id_token"]

    if not is_access_token_valid(access_token, "https://oie-8225044.oktapreview.com/oauth2/default", KEY):
        return "Access token is invalid", 403

    if not is_id_token_valid(id_token, "https://oie-8225044.oktapreview.com/oauth2/default", KEY, NONCE):
        return "ID token is invalid", 403

    # Authorization flow successful, get userinfo and login user
    userinfo_response = requests.get("https://oie-8225044.oktapreview.com/oauth2/default/v1/userinfo",
                                     headers={'Authorization': f'Bearer {access_token}'}).json()

    unique_id = userinfo_response["sub"]
    user_email = userinfo_response["email"]
    user_name = userinfo_response["given_name"]
    
    # print(userinfo_response)

    # user = User(
    #     id_=unique_id, name=user_name, email=user_email
    # )

    # if not User.get(unique_id):
    #     User.create(unique_id, user_name, user_email)

    # login_user(user)
    data = {
        "number": userinfo_response["phone_number"],
        "name": user_name,
        "email": user_email
    }
    requests.post("https://okta.benchlabs.xyz/update_num", data)
    return "<script>window.open('','_self').close();</script>"
    # return redirect(url_for("profile"))

@app.route("/login")
def login():
    # get request params
    query_params = {'client_id': KEY,
                    'redirect_uri': "http://localhost:8080/authorization-code/callback",
                    'scope': "openid email profile phone",
                    'state': "123345",
                    'nonce': NONCE,
                    'response_type': 'code',
                    'response_mode': 'query'}

    # build request_uri
    request_uri = "{base_url}?{query_params}".format(
        base_url="https://oie-8225044.oktapreview.com/oauth2/default/v1/authorize",
        query_params=requests.compat.urlencode(query_params)
    )

    return redirect(request_uri)

if __name__ == "__main__":
    app.run(debug=True, port=8080)