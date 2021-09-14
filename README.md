# bubble-connect

Before starting up the server, you will need to create a copy of the `example.config.json` and rename to `config.json`.

Start by configuring the settings:
```json
{
    "OKTA_KEY": "<Okta app key>",
    "OKTA_SECRET": "<Okta app secret>",
    "OKTA_NONCE": "<Okta exmaple nonce>",
    "TWILIO_SID": "<Twilio account SID>",
    "TWILIO_TOKEN":"<Twilio account token>",
    "OKTA_ORG_URL": "<OIE Preview URL>",
    "APP_URL": "<URL for session managment>",
    "WHATSAPP_NUMBER": "<Twilio WhatsApp number>",
    "FLASK_SECRET": "<Random secret>"
}

```

After configuring all the setting you can run the flask app:

```bash
python main.py
```