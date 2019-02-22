import json
import os

from bitshares.bitshares import BitShares
import lemoncheesecake.api as lcc

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "..//resources")
ECHO_DEV = json.load(open(os.path.join(RESOURCES_DIR, "urls.json")))["BASE_URL"]
PASS_PHRASE = json.load(open(os.path.join(RESOURCES_DIR, "wallet.json")))["PASS_PHRASE"]
PRIVATE_KEY = json.load(open(os.path.join(RESOURCES_DIR, "wallet.json")))["PRIVATE_KEY"]


class EchoOperations(object):

    def __init__(self):
        self.echo = self.connect_to_network()
        self.wallet = None

    @staticmethod
    def connect_to_network():
        echo = BitShares(
            ECHO_DEV,
            bundle=True,
        )
        return echo

    def create_or_unlock_wallet(self, pass_phrase=PASS_PHRASE, private_key=PRIVATE_KEY):
        if not self.echo.wallet.created():
            self.echo.wallet.create(pass_phrase)
            self.echo.wallet.addPrivateKey(private_key)
        else:
            self.echo.wallet.unlock(pass_phrase)
        return self.echo

    def create_contract(self, code, registrar, value_amount):
        self.wallet = self.create_or_unlock_wallet()
        self.wallet.create_contract(code=code, registrar=registrar, value_amount=value_amount)
        response = self.wallet.broadcast()
        lcc.log_info("Received: \n{}".format(json.dumps(response, indent=4)))
        return response

    def call_contract_method(self, code, registrar, callee):
        self.wallet.call_contract(code=code, registrar=registrar, callee=callee)
        response = self.wallet.broadcast()
        lcc.log_info("Received: \n{}".format(json.dumps(response, indent=4)))
        return response
