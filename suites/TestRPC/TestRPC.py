# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
import requests
from lemoncheesecake.matching import require_that, has_length, require_that_in, is_integer, equal_to, is_none, \
    is_true, \
    check_that, is_false

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
        self.passphrase = None
        self.account_address = None
        self.time = None
        self.SHA3_hash = None

    def rpc_call(self, method, params):
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0,
        }
        lcc.log_debug("request")
        lcc.log_debug(str(payload))
        return payload

    def get_response(self, payload):
        response = requests.post(self.test_rcp_url, json=payload).json()
        lcc.log_debug("response")
        lcc.log_debug(str(response))
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
        self.passphrase = "Account"
        self.account_address = "0x0000000000000000000000000000000000000006"
        self.time = "0xf"
        self.SHA3_hash = "0x68656c6c6f20776f726c64"

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
        payload = self.rpc_call("personal_newAccount", [self.passphrase])
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
    def personal_list_raw_accounts(self):
        payload = self.rpc_call("personal_listRawAccounts", [])
        results = self.get_response(payload)["result"]
        result = results[0]
        if not self.type_validator.is_eth_address(result["address"]):
            lcc.log_error("Wrong format of 'address', got: {}".format(result["address"]))
        else:
            lcc.log_info("'result' has correct format: address")
        if not self.type_validator.is_privkey(result["privkey"]):
            lcc.log_error("Wrong format of 'privkey', got: {}".format(result["privkey"]))
        else:
            lcc.log_info("'result' has correct format: privkey")
        check_that("passphrase", result["passphrase"], equal_to(""))
        for result in results[1:]:
            if not self.type_validator.is_eth_address(result["address"]):
                lcc.log_error("Wrong format of 'address', got: {}".format(result["address"]))
            else:
                lcc.log_info("'result' has correct format: address")
            if not self.type_validator.is_privkey(result["privkey"]):
                lcc.log_error("Wrong format of 'privkey', got: {}".format(result["privkey"]))
            else:
                lcc.log_info("'result' has correct format: privkey")
            check_that("passphrase", result["passphrase"], equal_to(self.passphrase))

    @lcc.test("Check method 'personal_lockAccount'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def personal_lock_account(self):
        payload = self.rpc_call("personal_lockAccount", [self.account_address])
        response = self.get_response(payload)
        require_that("'result'", response["result"], is_true())

    @lcc.test("Check method 'personal_lockAccount'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def personal_lock_account(self):
        payload = self.rpc_call("personal_lockAccount", [self.account_address])
        response = self.get_response(payload)
        require_that("'result'", response["result"], is_true())

    @lcc.test("Check method 'personal_unlockAccount'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.personal_lock_account")
    def personal_unlock_account(self):
        payload = self.rpc_call("personal_unlockAccount", [self.account_address, self.passphrase, self.time])
        response = self.get_response(payload)
        require_that("'result'", response["result"], is_false())

    # todo: BUG ECHO-1774. Undisabled
    @lcc.disabled()
    @lcc.test("Check method 'eth_sign'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def eth_sign(self):
        payload = self.rpc_call("eth_sign", [self.account_address, "0xdeadbeaf"])
        response = self.get_response(payload)
        if not self.type_validator.is_hex(response["result"]):
            lcc.log_error("Wrong format of 'result', got: '{}'".format(response["result"]))
        else:
            lcc.log_info("'result' has correct format: hex")

    @lcc.test("Check method 'eth_sendTransaction'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def eth_send_transaction(self):
        payload = self.rpc_call("eth_sendTransaction",
                                [{
                                    "from": "0x0000000000000000000000000000000000000006",
                                    "to": "0x0000000000000000000000000000000000000007",
                                }]
                                )
        response = self.get_response(payload)
        if not self.type_validator.is_hex(response["result"]):
            lcc.log_error("Wrong format of 'result', got: '{}'".format(response["result"]))
        else:
            lcc.log_info("'result' has correct format: hex")

    @lcc.test("Check method 'personal_sendTransaction'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def personal_send_transaction(self):
        payload = self.rpc_call("personal_sendTransaction",
                                [{'from': '0x0000000000000000000000000000000000000006',
                                  'to': '0x0000000000000000000000000000000000000007',
                                  "value": "0xf"},
                                 "Account", ]
                                )
        response = self.get_response(payload)
        if not self.type_validator.is_hex(response["result"]):
            lcc.log_error("Wrong format of 'result', got: '{}'".format(response["result"]))
        else:
            lcc.log_info("'result' has correct format: hex")

    @lcc.test("Check method 'web3_clientVersion'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def web3_client_version(self):
        result = "ECHO/0.16.0-rc.2-1-g08e87ae9/Linux.64-bit"
        payload = self.rpc_call("web3_clientVersion", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to(result))

    @lcc.test("Check method 'web3_sha3'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def web3_sha3(self):
        payload = self.rpc_call("web3_sha3", [self.SHA3_hash])
        response = self.get_response(payload)
        if not self.type_validator.is_SHA3_256(response["result"]):
            lcc.log_error("Wrong format of 'result', got: '{}'".format(response["result"]))
        else:
            lcc.log_info("'result' has correct format: hex")

    @lcc.test("Check method 'net_version'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def net_version(self):
        echo_devnet = "3"
        payload = self.rpc_call("net_version", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to(echo_devnet))

    @lcc.test("Check method 'net_listening'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def net_listening(self):
        payload = self.rpc_call("net_listening", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], is_true())

    @lcc.test("Check method 'net_peerCount'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def net_peer_count(self):
        payload = self.rpc_call("net_peerCount", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to("0x00"))



