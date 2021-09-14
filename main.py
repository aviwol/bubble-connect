import time
import requests
from flask import Flask, request, redirect, session
import asyncio
from okta_jwt_verifier import JWTVerifier
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

# Internal imports
from settings import Settings
from okta_helpers import OktaHelper

@app.route("/authorization-code/callback")
def callback():
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    code = request.args.get("code")
    if not code:
        return "The code was not returned or is not accessible", 403
    query_params = {'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': settings["APP_URL"] + "authorization-code/callback"
                    }
    query_params = requests.compat.urlencode(query_params)
    exchange = requests.post(
        settings["OKTA_ORG_URL"] + "/v1/token",
        headers=headers,
        data=query_params,
        auth=(KEY, SECRET),
    ).json()

    # Get tokens and validate
    if not exchange.get("token_type"):
        return "Unsupported token type. Should be 'Bearer'.", 403
    access_token = exchange["access_token"]
    id_token = exchange["id_token"]

    if not okta_helper.is_access_token_valid(access_token, settings["OKTA_ORG_URL"]):
        return "Access token is invalid", 403

    if not okta_helper.is_id_token_valid(id_token, settings["OKTA_ORG_URL"], NONCE):
        return "ID token is invalid", 403

    # Authorization flow successful, get userinfo and login user
    userinfo_response = requests.get(settings["OKTA_ORG_URL"] +"/v1/userinfo",
                                     headers={'Authorization': f'Bearer {access_token}'}).json()

    unique_id = userinfo_response["sub"]
    user_email = userinfo_response["email"]
    user_name = userinfo_response["given_name"]

    data = {
        "number": userinfo_response["phone_number"],
        "name": user_name,
        "email": user_email
    }

    requests.post(settings["APP_URL"] + "/update_num", data)
    return "If this window did not close, please close the window and go back to the WhatsApp conversation. <script>window.open('','_self').close();</script>"

@app.route("/login")
def login():
    # get request params
    query_params = {'client_id': KEY,
                    'redirect_uri': settings["APP_URL"] + "/authorization-code/callback",
                    'scope': "openid email profile phone",
                    'state': "123345",
                    'nonce': settings["OKTA_NONCE"],
                    'response_type': 'code',
                    'response_mode': 'query'}

    # build request_uri
    request_uri = "{base_url}?{query_params}".format(
        base_url=settings["OKTA_ORG_URL"] + "/v1/authorize",
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
             from_="whatsapp:" + settings["WHATSAPP_NUMBER"],
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

    # All logic regarding the chatbot goes here. Using Twilio Redirect will make the bot work here
    if incoming_msg == "yes":
        welcome_message = "Okay awesome! Your balance is $100."
    else:
        welcome_message = "That's okay. Next time!"
    msg.body(welcome_message)
    return str(resp) 


if __name__ == "__main__":
    # Flask settings
    app = Flask(__name__)
    settings = Settings()
    app.secret_key = settings["FLASK_SECRET"]

    # Twilio settings
    client = Client(settings["TWILIO_SID"], settings["TWILIO_TOKEN"])

    # Okta Settings
    okta_helper = OktaHelper(settings)
    loop = asyncio.get_event_loop()

    # Local session cache for the numbers recieved
    NUMBERS = {}    
    app.run(debug=True, port=8080)