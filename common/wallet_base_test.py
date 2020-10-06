# -*- coding: utf-8 -*-

import json
import time

from common.object_validation import ObjectValidator
from common.type_validation import TypeValidator
from project import WALLET_PASSWORD, WALLET_URL

import lemoncheesecake.api as lcc
from echopy.echoapi.ws.simplewebsocket import SimpleWebsocket


class WalletBaseTest:

    request_id = 0

    def __init__(self):
        self.wallet_ws = SimpleWebsocket(WALLET_URL, False)
        self.type_validator = TypeValidator()
        self.object_validator = ObjectValidator()

    @staticmethod
    def get_request(method_name, params=None):
        # Params must be list
        request = [1, method_name]
        if params is None:
            request.append([])
            return request
        request.extend([params])
        return request

    @staticmethod
    def get_positive_result(response, print_log):
        if "result" not in response:
            raise Exception("Need result, but received:\n{}".format(json.dumps(response, indent=4)))
        if print_log:
            lcc.log_info("Received:\n{}".format(json.dumps(response, indent=4)))
        return response

    @staticmethod
    def get_negative_result(response, print_log):
        if print_log:
            lcc.log_warning("Error received:\n{}".format(json.dumps(response, indent=4)))
        return response

    @staticmethod
    def json_rpc_template():
        return {
            "jsonrpc": "2.0",
            "params": "",
            "method": "",
            "id": 0
        }

    def __call_method(self, method, params):
        call_template = self.json_rpc_template()
        call_template["method"] = method
        call_template["params"] = params
        return call_template

    def send_wallet_request(self, method, params=[], negative=False, log_response=False, debug_mode=False):
        payload = self.__call_method(method, params)
        self.wallet_ws.connect()

        response = json.loads(self.wallet_ws.rpcexec(payload=payload))
        if debug_mode:
            lcc.log_debug("Send:\n{}".format(json.dumps(payload, indent=4)))
        self.wallet_ws.disconnect()

        if response.get("jsonrpc") != "2.0":
            lcc.log_error("Wrong data received: {}".format(json.dumps(response, indent=4)))
            raise Exception("Wrong response")
        if negative:
            return self.get_negative_result(response, log_response)
        if response.get("id") != payload["id"]:
            lcc.log_error(
                "Wrong 'id' expected '{}', but received:\n{}".format(payload["id"], json.dumps(response, indent=4))
            )
            raise Exception("Wrong 'id'")
        return self.get_positive_result(response, log_response)

    def get_wallet_notice(self, id_response):
        response = json.loads(self.wallet_ws.ws.recv())
        if id_response is None:
            return response["params"]
        if response.get("params")[0] != id_response:
            lcc.log_error(
                "Wrong 'subscription_id' expected '{}', but received:\n{}".format(
                    id_response, json.dumps(response, indent=4)
                )
            )
            raise Exception("Wrong 'subscription_id'")
        if response.get("method") != "notice":
            lcc.log_error(
                "Wrong response, expected ''method': 'notice'', but received:\n{}".format(
                    json.dumps(response, indent=4)
                )
            )
            raise Exception("Wrong response")

        return response["params"]

    def get_proposal_id_from_next_blocks(self, block):
        proposal_id = None
        stop = False
        no_result_exeption = 0
        while not stop:
            block += 1
            result = self.send_wallet_request("get_block", [block], log_response=False)['result']
            if no_result_exeption >= 5:
                stop = True
                lcc.log_error("No transaction not found in blocks")
                continue
            if result is None:
                no_result_exeption += 1
                time.sleep(5)
                block -= 1
                continue
            elif result['transactions'] != []:
                for transaction in result['transactions']:
                    if self.type_validator.is_proposal_id(transaction['operation_results'][0][1]):
                        proposal_id = transaction['operation_results'][0][1]
                        stop = True
                        break
            else:
                continue
        if proposal_id:
            return proposal_id
        else:
            raise Exception("Wrong response")

    def unlock_wallet(self):
        lcc.set_step("Unlock wallet to register account")
        response = self.send_wallet_request("is_new", [], log_response=False)
        if response['result']:
            self.send_wallet_request("set_password", [WALLET_PASSWORD], log_response=False)
        response = self.send_wallet_request("is_locked", [], log_response=False)
        if response['result']:
            self.send_wallet_request("unlock", [WALLET_PASSWORD], log_response=False)
        lcc.log_info("Wallet unlocked")
