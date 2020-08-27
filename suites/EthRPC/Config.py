# -*- coding: utf-8 -*-
from echopy import Echo
from project import BASE_URL

import lemoncheesecake.api as lcc
import requests
from lemoncheesecake.matching import require_that, has_length, require_that_in, is_integer, equal_to, is_none, \
    is_true, \
    check_that, is_false, not_equal_to, is_list

from common.base_test import BaseTest
from project import ETHRPC_URL

SUITE = {
    "description": "Run 'config part' tests for JSON PRC interface of ECHO node"
}


@lcc.prop("main", "type")
@lcc.tags("eth_rpc", "eth_rpc_config")
@lcc.suite("Check EthRPC 'config part'")
class Config(BaseTest):

    def __init__(self):
        super().__init__()
        self.passphrase = None
        self.account_address = None
        self.time = None
        self.SHA3_trx_hash = None
        self.contract_address = None
        self.null_trx_hash = None
        self.contract = None
        self.new_account_address = None
        self.value = None

    def rpc_call(self, method, params):
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0,
        }
        return payload

    def get_response(self, payload):
        response = requests.post(ETHRPC_URL, json=payload).json()
        if require_that("eth-rpc response", response, has_length(3)):
            require_that_in(
                response,
                "id", is_integer(),
                "jsonrpc", equal_to("2.0")
            )
            return response

    def create_contract(self):
        payload = self.rpc_call("personal_sendTransaction",
                                [{
                                    "from": self.account_address,
                                    "data": self.contract,
                                }, ""]
                                )
        trx_hash = self.get_response(payload)["result"]
        return trx_hash

    def setup_suite(self):
        self.passphrase = "Account"
        self.null_trx_hash = "0x0000000000000000000000000000000000000000000000000000000000000000"
        self.account_address = "0x0000000000000000000000000000000000000006"
        self.new_account_address = "0x0000000000000000000000000000000000000007"
        self.contract_address = "0x0100000000000000000000000000000000000001"
        self.time = "0xffff"
        self.SHA3_trx_hash = "0x68656c6c6f20776f726c64"
        self.value = "0xffff"
        self.contract = self.get_byte_code("piggy", "code")

    def teardown_suite(self):
        pass

    @lcc.test("Check connection to EthPRC interface")
    def main_check(self):
        message = {'code': -32600, 'message': 'Missing or invalid method'}
        payload = self.rpc_call("", "")
        response = requests.post(ETHRPC_URL, json=payload).json()
        if require_that("json-rpc response", response, has_length(3)):
            require_that_in(
                response,
                "id", is_none(),
                "jsonrpc", equal_to("2.0"),
                "error", equal_to(message)
            )

    @lcc.test("Check method 'web3_clientVersion'")
    @lcc.depends_on("EthRPC.Config.Config.main_check")
    def web3_client_version(self):
        result = "ECHO/0.21-rc.1/Linux.64-bit"
        payload = self.rpc_call("web3_clientVersion", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to(result))

    @lcc.test("Check method 'eth_chain_id'")
    @lcc.depends_on("EthRPC.Config.Config.main_check")
    def eth_chain_id(self):
        chain_id = "0xd93a5bc33bd6c7bd3d5e93f5dff6868abafa83800580a54df55af7fe134cbe38"
        payload = self.rpc_call("eth_chainId", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to(chain_id))

    @lcc.test("Check method 'web3_sha3'")
    @lcc.depends_on("EthRPC.Config.Config.main_check")
    def web3_sha3(self):
        payload = self.rpc_call("web3_sha3", [self.SHA3_trx_hash])
        response = self.get_response(payload)
        if not self.type_validator.is_SHA3_256(response["result"]):
            lcc.log_error("Wrong format of 'result', got: '{}'".format(response["result"]))
        else:
            lcc.log_info("'result' has correct format: hex")

    @lcc.test("Check method 'net_version'")
    @lcc.depends_on("EthRPC.Config.Config.main_check")
    def net_version(self):
        echo_devnet = "3"
        payload = self.rpc_call("net_version", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to(echo_devnet))

    @lcc.test("Check method 'net_listening'")
    @lcc.depends_on("EthRPC.Config.Config.main_check")
    def net_listening(self):
        payload = self.rpc_call("net_listening", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], is_true())

    @lcc.test("Check method 'eth_protocolVersion'")
    @lcc.depends_on("EthRPC.Config.Config.main_check")
    def eth_protocol_version(self):
        payload = self.rpc_call("eth_protocolVersion", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to("0x3f"))

    @lcc.test("Check method 'net_peerCount'")
    @lcc.depends_on("EthRPC.Config.Config.main_check")
    def net_peer_count(self):
        p2p_quantity = "0x00"
        payload = self.rpc_call("net_peerCount", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to(p2p_quantity))

    @lcc.test("Check method 'eth_protocolVersion'")
    @lcc.depends_on("EthRPC.Config.Config.main_check")
    def eth_protocol_version(self):
        eth_version = "0x3f"
        payload = self.rpc_call("eth_protocolVersion", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to(eth_version))

    @lcc.test("Check method 'eth_syncing'")
    @lcc.depends_on("EthRPC.Config.Config.main_check")
    def eth_syncing(self):
        payload = self.rpc_call("eth_syncing", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], is_false())

    @lcc.test("Check method 'eth_coinbase'")
    @lcc.depends_on("EthRPC.Config.Config.main_check")
    def eth_coinbase(self):
        payload = self.rpc_call("eth_coinbase", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to(self.account_address))

    @lcc.test("Check method 'eth_gasPrice'")
    @lcc.depends_on("EthRPC.Config.Config.main_check")
    def eth_gas_price(self):
        gas_price = "0x01"
        payload = self.rpc_call("eth_gasPrice", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to(gas_price))

    @lcc.test("Check method 'eth_block_number'")
    @lcc.depends_on("EthRPC.Config.Config.main_check")
    def eth_block_number(self):
        payload = self.rpc_call("eth_blockNumber", [])
        response = self.get_response(payload)
        echo = Echo()
        echo.connect(BASE_URL)
        head_block_number = echo.api.database.get_dynamic_global_properties()["head_block_number"]
        check_that('block_number', int(response["result"], 16), equal_to(head_block_number))

    @lcc.disabled()
    @lcc.test("Check method 'eth_getStorageAt'")
    @lcc.depends_on("EthRPC.Config.Config.main_check")
    def eth_get_storage_at(self):
        self.create_contract()
        payload = self.rpc_call("eth_getStorageAt", [self.contract_address,
                                                     "0x6661e9d6d8b923d5bbaab1b96e1dd51ff6ea2a93520fdc9eb75d059238b8c5e9",
                                                     "latest"])
        response = self.get_response(payload)
        require_that("'result'", response["result"], not_equal_to(self.null_trx_hash))

    @lcc.test("Check method 'eth_estimateGas'")
    @lcc.depends_on("EthRPC.Config.Config.main_check")
    def eth_estimate_gas(self):
        payload = self.rpc_call("eth_estimateGas",
                                [{
                                    "from": self.account_address,
                                    "data": self.contract,
                                }]
                                )
        response = self.get_response(payload)
        if not self.type_validator.is_eth_balance(response["result"]):
            lcc.log_error("Wrong format of 'gas', got: '{}'".format(response["result"]))
        else:
            lcc.log_info("'result' has correct format: gas")

    @lcc.test("Check method 'eth_pendingTransactions'")
    @lcc.depends_on("EthRPC.Config.Config.main_check")
    def eth_pending_transactions(self):
        payload = self.rpc_call("eth_pendingTransactions", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], is_list())

    @lcc.test("Check method 'echo_requestRegistrationTask'")
    @lcc.depends_on("EthRPC.Config.Config.main_check")
    def echo_request_registration_task(self):
        payload = self.rpc_call("echo_requestRegistrationTask", [])
        response = self.get_response(payload)["result"]
        if not self.type_validator.is_eth_hash(response["blockId"]):
            lcc.log_error("Wrong format of 'blockId', got: '{}'".format(response["blockId"]))
        else:
            lcc.log_info("'blockId' has correct format: eth_hash")
        if not self.type_validator.is_eth_hash(response["randNum"]):
            lcc.log_error("Wrong format of 'randNum', got: '{}'".format(response["randNum"]))
        else:
            lcc.log_info("'randNum' has correct format: eth_hash")
        if not self.type_validator.is_eth_hash(response["difficulty"]):
            lcc.log_error("Wrong format of 'difficulty', got: '{}'".format(response["difficulty"]))
        else:
            lcc.log_info("'difficulty' has correct format: eth_hash")

    @lcc.test("Check method 'echo_submitRegistrationSolution'")
    @lcc.depends_on("EthRPC.Config.Config.echo_request_registration_task")
    def echo_submit_registration_solution(self, get_random_valid_account_name):
        payload = self.rpc_call("echo_requestRegistrationTask", [])
        response = self.get_response(payload)["result"]
        block_id_right160 = response["blockId"][26:]
        rand_num_decimal = int(response["randNum"].lstrip("0x"), 16)
        difficulty = int(response["difficulty"].lstrip("0x"), 16)
        nonce = self.echo.solve_registration_task(block_id_right160, rand_num_decimal, difficulty)
        nonce_hex = hex(nonce)
        evm_address = None
        account_name = get_random_valid_account_name
        active_key = echorand_key = "ECHOHCcqrvESxeg4Kmmpr73FdQSQR6TbusCMsHeuXvx2rM1G"
        rand_num = response["randNum"]
        payload = self.rpc_call("echo_submitRegistrationSolution",
                                [account_name, active_key, echorand_key, evm_address, nonce_hex, rand_num])
        response = self.get_response(payload)
        if not self.type_validator.is_eth_hash(response["result"]):
            lcc.log_error("Wrong format of 'difficulty', got: '{}'".format(response["difficulty"]))
        else:
            lcc.log_info("'difficulty' has correct format: eth_hash")
