# -*- coding: utf-8 -*-

import json

from common.object_validation import ObjectValidator
from common.type_validation import TypeValidator
from project import WALLET_URL

import lemoncheesecake.api as lcc
from echopy.echoapi.ws.simplewebsocket import SimpleWebsocket


class WalletBaseTest:

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

        lcc.log_info("{}".format(response))
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
