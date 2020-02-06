# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
import requests
from lemoncheesecake.matching import require_that, has_length, require_that_in, is_integer, equal_to, is_none, is_true

from common.base_test import BaseTest

SUITE = {
    "description": "Run ECHO test node and check TestPRC methods"
}


@lcc.prop("main", "type")
@lcc.tags("test_rpc")
@lcc.suite("Check TestPRC methods of ECHO test node")
class TestRPC(BaseTest):

    def __init__(self):
        super().__init__()
        self.rpcPort = None
        self.test_rcp_url = None

    def rpc_call(self, method, params):
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0,
        }
        return payload

    def get_response(self, payload):
        response = requests.post(self.test_rcp_url, json=payload).json()
        print(response)
        if require_that("json-rpc response", response, has_length(3)):
            require_that_in(
                response,
                "id", is_integer(),
                "jsonrpc", equal_to("2.0")
            )
            return response

    def setup_suite(self):
        self.rpcPort = 19999
        self.test_rcp_url = 'http://localhost:' + str(self.rpcPort)

    def teardown_suite(self):
        pass

    @lcc.test("Check connection to ECHO test node")
    def main_check(self):
        message = {'code': -32600, 'message': 'Missing or invalid method'}
        payload = self.rpc_call("", "")
        response = requests.post(self.test_rcp_url, json=payload).json()
        if require_that("json-rpc response", response, has_length(3)):
            require_that_in(
                response,
                "id", is_none(),
                "jsonrpc", equal_to("2.0"),
                "error", equal_to(message)
            )

    @lcc.test("Check method 'eth_mining'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def eth_mining(self):
        payload = self.rpc_call("eth_mining", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], is_true())

    @lcc.test("Check method 'miner_stop'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def miner_stop(self):
        payload = self.rpc_call("miner_stop", ["0x0"])
        response = self.get_response(payload)
        require_that("'result'", response["result"], is_none())

    @lcc.test("Check method 'miner_start'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.miner_stop")
    def miner_start(self):
        payload = self.rpc_call("miner_stop", ["0x0"])
        response = self.get_response(payload)
        require_that("'result'", response["result"], is_none())

    @lcc.test("Check method 'personal_newAccount'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def personal_new_account(self):
        payload = self.rpc_call("personal_newAccount", ["Account"])
        response = self.get_response(payload)
        if not self.type_validator.is_eth_address(response["result"]):
            lcc.log_error("Wrong format of 'result', got: {}".format(response["result"]))
        else:
            lcc.log_info("'result' has correct format: address")

    @lcc.test("Check method 'personal_listAccounts'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def personal_list_accounts(self):
        payload = self.rpc_call("personal_listAccounts", [])
        results = self.get_response(payload)["result"]
        for result in results:
            if not self.type_validator.is_eth_address(result):
                lcc.log_error("Wrong format of 'result', got: {}".format(result))
            else:
                lcc.log_info("'result' has correct format: address")

    @lcc.test("Check method 'personal_listRawAccounts'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def personal_list_accounts(self):
        payload = self.rpc_call("personal_listAccounts", [])
        results = self.get_response(payload)["result"]
        for result in results:
            if not self.type_validator.is_eth_address(result):
                lcc.log_error("Wrong format of 'result', got: {}".format(result))
            else:
                lcc.log_info("'result' has correct format: address")







