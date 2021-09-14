import asyncio
from okta_jwt_verifier import JWTVerifier

class OktaHelper():

    def __init__(self, settings):
        self.client_id = settings["OKTA_KEY"]    

    def is_access_token_valid(token, issuer):
        jwt_verifier = JWTVerifier(issuer, self.client_id, 'api://default')
        try:
            loop.run_until_complete(jwt_verifier.verify_access_token(token))
            return True
        except Exception:
            return False

    def is_id_token_valid(token, issuer, nonce):
        jwt_verifier = JWTVerifier(issuer, self.client_id, 'api://default')
        try:
            loop.run_until_complete(jwt_verifier.verify_id_token(token, nonce=nonce))
            return True
        except Exception:
            return False