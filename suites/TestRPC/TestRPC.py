# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
import requests
from lemoncheesecake.matching import require_that, has_length, require_that_in, is_integer, equal_to, is_none, \
    is_true, \
    check_that, is_false, not_equal_to, is_list

from common.base_test import BaseTest

SUITE = {
    "description": "Run ECHO test node and check TestPRC methods"
}


#  todo: undisabled, when TestRPC will be public
@lcc.disabled()
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
        response = requests.post(self.test_rcp_url, json=payload).json()
        if require_that("json-rpc response", response, has_length(3)):
            require_that_in(
                response,
                "id", is_integer(),
                "jsonrpc", equal_to("2.0")
            )
            return response

    def transfer(self):
        payload = self.rpc_call("personal_sendTransaction",
                                [{"from": self.account_address, "to": self.new_account_address, "value": self.value},
                                 ""])
        trx_hash = self.get_response(payload)["result"]
        return trx_hash

    def create_contract(self):
        payload = self.rpc_call("personal_sendTransaction",
                                [{
                                    "from": self.account_address,
                                    "data": self.contract,
                                }, ""]
                                )
        trx_hash = self.get_response(payload)["result"]
        return trx_hash

    def validate_transaction(self, transaction):
        if require_that("transactions", transaction, has_length(14)):
            if not self.type_validator.is_SHA3_256(transaction["blockHash"]):
                lcc.log_error("Wrong format of 'blockHash', got: '{}'".format(transaction["blockHash"]))
            else:
                lcc.log_info("'result' has correct format: eth_hash")
            if not self.type_validator.is_eth_hash(transaction["blockNumber"]):
                lcc.log_error("Wrong format of 'blockNumber', got: '{}'".format(transaction["blockNumber"]))
            else:
                lcc.log_info("'result' has correct format: eth_hash")
            if not self.type_validator.is_eth_hash(transaction["gas"]):
                lcc.log_error("Wrong format of 'gas', got: '{}'".format(transaction["gas"]))
            else:
                lcc.log_info("'result' has correct format: eth_hash")
            if not self.type_validator.is_eth_hash(transaction["gasPrice"]):
                lcc.log_error("Wrong format of 'gasPrice', got: '{}'".format(transaction["gasPrice"]))
            else:
                lcc.log_info("'result' has correct format: eth_hash")
            if not self.type_validator.is_SHA3_256(transaction["hash"]):
                lcc.log_error("Wrong format of 'hash', got: '{}'".format(transaction["hash"]))
            else:
                lcc.log_info("'result' has correct format: eth_hash")
            if not self.type_validator.is_eth_hash(transaction["nonce"]):
                lcc.log_error("Wrong format of 'nonce', got: '{}'".format(transaction["nonce"]))
            else:
                lcc.log_info("'result' has correct format: eth_hash")
            if not self.type_validator.is_eth_hash(transaction["to"]):
                lcc.log_error("Wrong format of 'to', got: '{}'".format(transaction["to"]))
            else:
                lcc.log_info("'result' has correct format: eth_hash")
            if not self.type_validator.is_eth_hash(transaction["transactionIndex"]):
                lcc.log_error(
                    "Wrong format of 'transactionIndex', got: '{}'".format(transaction["transactionIndex"]))
            else:
                lcc.log_info("'result' has correct format: eth_hash")
            check_that("value", transaction["value"], equal_to(self.value))
            if not self.type_validator.is_eth_hash(transaction["v"]):
                lcc.log_error(
                    "Wrong format of 'v', got: '{}'".format(transaction["v"]))
            else:
                lcc.log_info("'result' has correct format: eth_hash")
            if not self.type_validator.is_eth_hash(transaction["r"]):
                lcc.log_error(
                    "Wrong format of 'r', got: '{}'".format(transaction["r"]))
            else:
                lcc.log_info("'r' has correct format: eth_hash")
            if not self.type_validator.is_eth_hash(transaction["s"]):
                lcc.log_error(
                    "Wrong format of 's', got: '{}'".format(transaction["s"]))
            else:
                lcc.log_info("'s' has correct format: eth_hash")

    def validate_block(self, result):
        if require_that("'result'", result, has_length(19)):
            if not self.type_validator.is_eth_hash(result["number"]):
                lcc.log_error("Wrong format of 'number', got: '{}'".format(result["number"]))
            else:
                lcc.log_info("'result' has correct format: number")
            if not self.type_validator.is_eth_hash(result["hash"]):
                lcc.log_error("Wrong format of 'number', got: '{}'".format(result["number"]))
            else:
                lcc.log_info("'result' has correct format: hash")
            if not self.type_validator.is_eth_hash(result["hash"]):
                lcc.log_error("Wrong format of 'number', got: '{}'".format(result["number"]))
            else:
                lcc.log_info("'result' has correct format: hash")
            if not self.type_validator.is_eth_hash(result["parentHash"]):
                lcc.log_error("Wrong format of 'parentHash', got: '{}'".format(result["parentHash"]))
            else:
                lcc.log_info("'result' has correct format: parentHash")
            if not self.type_validator.is_eth_hash(result["nonce"]):
                lcc.log_error("Wrong format of 'nonce', got: '{}'".format(result["nonce"]))
            else:
                lcc.log_info("'result' has correct format: nonce")
            if not self.type_validator.is_eth_hash(result["nonce"]):
                lcc.log_error("Wrong format of 'nonce', got: '{}'".format(result["nonce"]))
            else:
                lcc.log_info("'result' has correct format: nonce")
            if not self.type_validator.is_eth_hash(result["sha3Uncles"]):
                lcc.log_error("Wrong format of 'sha3Uncles', got: '{}'".format(result["sha3Uncles"]))
            else:
                lcc.log_info("'result' has correct format: sha3Uncles")
            if not self.type_validator.is_eth_hash(result["logsBloom"]):
                lcc.log_error("Wrong format of 'logsBloom', got: '{}'".format(result["logsBloom"]))
            else:
                lcc.log_info("'result' has correct format: logsBloom")
            if not self.type_validator.is_eth_hash(result["transactionsRoot"]):
                lcc.log_error("Wrong format of 'transactionsRoot', got: '{}'".format(result["transactionsRoot"]))
            else:
                lcc.log_info("'result' has correct format: transactionsRoot")
            if not self.type_validator.is_eth_hash(result["stateRoot"]):
                lcc.log_error("Wrong format of 'stateRoot', got: '{}'".format(result["stateRoot"]))
            else:
                lcc.log_info("'result' has correct format: stateRoot")
            if not self.type_validator.is_eth_hash(result["receiptsRoot"]):
                lcc.log_error("Wrong format of 'receiptsRoot', got: '{}'".format(result["receiptsRoot"]))
            else:
                lcc.log_info("'result' has correct format: receiptsRoot")
            if not self.type_validator.is_eth_hash(result["miner"]):
                lcc.log_error("Wrong format of 'receiptsRoot', got: '{}'".format(result["miner"]))
            else:
                lcc.log_info("'result' has correct format: miner")
            if not self.type_validator.is_eth_hash(result["difficulty"]):
                lcc.log_error("Wrong format of 'difficulty', got: '{}'".format(result["difficulty"]))
            else:
                lcc.log_info("'result' has correct format: difficulty")
            if not self.type_validator.is_eth_hash(result["totalDifficulty"]):
                lcc.log_error("Wrong format of 'totalDifficulty', got: '{}'".format(result["totalDifficulty"]))
            else:
                lcc.log_info("'result' has correct format: totalDifficulty")
            if not self.type_validator.is_eth_hash(result["extraData"]):
                lcc.log_error("Wrong format of 'extraData', got: '{}'".format(result["extraData"]))
            else:
                lcc.log_info("'result' has correct format: extraData")
            if not self.type_validator.is_eth_hash(result["size"]):
                lcc.log_error("Wrong format of 'size', got: '{}'".format(result["size"]))
            else:
                lcc.log_info("'result' has correct format: size")
            if not self.type_validator.is_eth_hash(result["gasLimit"]):
                lcc.log_error("Wrong format of 'gasLimit', got: '{}'".format(result["gasLimit"]))
            else:
                lcc.log_info("'result' has correct format: gasLimit")
            if not self.type_validator.is_eth_hash(result["gasUsed"]):
                lcc.log_error("Wrong format of 'gasUsed', got: '{}'".format(result["gasUsed"]))
            else:
                lcc.log_info("'result' has correct format: gasUsed")
            if not self.type_validator.is_eth_hash(result["timestamp"]):
                lcc.log_error("Wrong format of 'timestamp', got: '{}'".format(result["timestamp"]))
            else:
                lcc.log_info("'result' has correct format: timestamp")
            if check_that("uncles", result["uncles"], is_list()):
                if len(result["transactions"]) > 0:
                    for transaction in result["transactions"]:
                        self.validate_transaction(transaction)

    def setup_suite(self):
        self.rpcPort = 56453
        self.test_rcp_url = 'http://localhost:' + str(self.rpcPort)
        self.passphrase = "Account"
        self.null_trx_hash = "0x0000000000000000000000000000000000000000000000000000000000000000"
        self.account_address = "0x0000000000000000000000000000000000000006"
        self.contract_address = "0x0100000000000000000000000000000000000001"
        self.time = "0xffff"
        self.SHA3_trx_hash = "0x68656c6c6f20776f726c64"
        self.value = "0xffff"
        self.contract = self.get_byte_code("piggy", "code")

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

    @lcc.test("Check method 'miner_stop'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def miner_stop(self):
        payload = self.rpc_call("miner_stop", ["0x0"])
        response = self.get_response(payload)
        require_that("'result'", response["result"], is_none())

    @lcc.test("Check method 'miner_start'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.miner_stop")
    def miner_start(self):
        payload = self.rpc_call("miner_start", ["0x0"])
        response = self.get_response(payload)
        require_that("'result'", response["result"], is_none())

    @lcc.test("Check method 'eth_mining'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.miner_start")
    def eth_mining(self):
        payload = self.rpc_call("eth_mining", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], is_true())

    @lcc.test("Check method 'personal_newAccount'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def personal_new_account(self):
        payload = self.rpc_call("personal_newAccount", [self.passphrase])
        response = self.get_response(payload)
        if not self.type_validator.is_eth_address(response["result"]):
            lcc.log_error("Wrong format of 'result', got: {}".format(response["result"]))
        else:
            lcc.log_info("'result' has correct format: address")
            self.new_account_address = response["result"]
            return self.new_account_address

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
        lcc.set_step("Check initialized accounts")
        for result in results[:2]:
            if not self.type_validator.is_eth_address(result["address"]):
                lcc.log_error("Wrong format of 'address', got: {}".format(result["address"]))
            else:
                lcc.log_info("'result' has correct format: address")
            if not self.type_validator.is_privkey(result["privkey"]):
                lcc.log_error("Wrong format of 'privkey', got: {}".format(result["privkey"]))
            else:
                lcc.log_info("'result' has correct format: privkey")
            check_that("passphrase", result["passphrase"], equal_to(""))
        lcc.set_step("Check created accounts")
        for result in results[2:]:
            if not self.type_validator.is_eth_address(result["address"]):
                lcc.log_error("Wrong format of 'address', got: {}".format(result["address"]))
            else:
                lcc.log_info("'result' has correct format: address")
            if not self.type_validator.is_privkey(result["privkey"]):
                lcc.log_error("Wrong format of 'privkey', got: {}".format(result["privkey"]))
            else:
                lcc.log_info("'result' has correct format: privkey")
            check_that("passphrase", result["passphrase"], equal_to(self.passphrase))

    @lcc.test("Check method 'eth_accounts'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def eth_accounts(self):
        payload = self.rpc_call("eth_accounts", [])
        results = self.get_response(payload)["result"]
        for account_address in results:
            if not self.type_validator.is_eth_address(account_address):
                lcc.log_error("Wrong format of 'address', got: {}".format(account_address))
            else:
                lcc.log_info("'result' has correct format: address")

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

    @lcc.test("Check method 'personal_sendTransaction'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.personal_new_account")
    def personal_send_transaction(self):
        payload = self.rpc_call("personal_sendTransaction",
                                [{"from": self.account_address, "to": self.new_account_address, "value": self.value},
                                 "Account"]
                                )
        response = self.get_response(payload)
        if not self.type_validator.is_hex(response["result"]):
            lcc.log_error("Wrong format of 'result', got: '{}'".format(response["result"]))
        else:
            lcc.log_info("'result' has correct format: hex")

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

    # todo: BUG ECHO-1764. Undisabled
    @lcc.disabled()
    @lcc.test("Check method 'eth_sendTransaction'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def eth_send_transaction(self):
        payload = self.rpc_call("eth_sendTransaction",
                                [{
                                    "from": "0x0000000000000000000000000000000000000006",
                                    "to": "0x0000000000000000000000000000000000000007",
                                    "value": "0xfff"
                                }]
                                )
        response = self.get_response(payload)
        require_that("'result'", response["result"], not_equal_to(self.null_trx_hash))
        if not self.type_validator.is_hex(response["result"]):
            lcc.log_error("Wrong format of 'result', got: '{}'".format(response["result"]))
        else:
            lcc.log_info("'result' has correct format: hex")

    @lcc.test("Check method 'web3_clientVersion'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def web3_client_version(self):
        result = "ECHO/0.17.0-rc.1/Linux.64-bit"
        payload = self.rpc_call("web3_clientVersion", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to(result))

    @lcc.test("Check method 'web3_sha3'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def web3_sha3(self):
        payload = self.rpc_call("web3_sha3", [self.SHA3_trx_hash])
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
        p2p_quantity = "0x00"
        payload = self.rpc_call("net_peerCount", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to(p2p_quantity))

    @lcc.test("Check method 'eth_protocolVersion'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def eth_protocol_version(self):
        eth_version = "0x3f"
        payload = self.rpc_call("eth_protocolVersion", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to(eth_version))

    @lcc.test("Check method 'eth_syncing'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def eth_syncing(self):
        payload = self.rpc_call("eth_syncing", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], is_false())

    # todo: BUG ECHO-1784. Undisabled
    @lcc.disabled()
    @lcc.test("Check method 'eth_coinbase'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def eth_coinbase(self):
        payload = self.rpc_call("eth_coinbase", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to(self.account_address))

    @lcc.test("Check method 'eth_gasPrice'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def eth_gas_price(self):
        gas_price = "0x01"
        payload = self.rpc_call("eth_gasPrice", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to(gas_price))

    @lcc.test("Check method 'eth_block_number'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def eth_block_number(self):
        payload = self.rpc_call("eth_blockNumber", [])
        response = self.get_response(payload)
        if not self.type_validator.is_eth_block_number(response["result"]):
            lcc.log_error("Wrong format of 'eth_blockNumber', got: '{}'".format(response["result"]))
        else:
            lcc.log_info("'result' has correct format: eth_blockNumber")

    @lcc.test("Check method 'eth_getBalance'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def eth_get_balance(self):
        payload = self.rpc_call("eth_getBalance", [self.account_address, "latest"])
        response = self.get_response(payload)
        if not self.type_validator.is_eth_balance(response["result"]):
            lcc.log_error("Wrong format of 'eth_balance', got: '{}'".format(response["result"]))
        else:
            lcc.log_info("'result' has correct format: eth_balance")

    @lcc.disabled()
    @lcc.test("Check method 'eth_getStorageAt'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.personal_send_transaction")
    def eth_get_storage_at(self):
        self.create_contract()
        payload = self.rpc_call("eth_getStorageAt", [self.contract_address,
                                                     "0x6661e9d6d8b923d5bbaab1b96e1dd51ff6ea2a93520fdc9eb75d059238b8c5e9",
                                                     "latest"])
        response = self.get_response(payload)
        require_that("'result'", response["result"], not_equal_to(self.null_trx_hash))

    # todo: BUG ECHO-1781. Undisabled
    @lcc.disabled()
    @lcc.test("Check method 'eth_getTransactionCount'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def eth_get_transaction_count(self):
        payload = self.rpc_call("eth_getTransactionCount", [self.account_address, "latest"])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to("0x01"))

    @lcc.test("Check method 'eth_getBlockTransactionCountByHash'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def eth_get_block_transaction_count_by_trx_hash(self):
        self.transfer()
        block_id = self.get_response(self.rpc_call("eth_blockNumber", []))
        block_hash = self.get_response(
            self.rpc_call("eth_getBlockByNumber", [block_id["result"], True]))["result"]["hash"]
        payload = self.rpc_call("eth_getBlockTransactionCountByHash", [block_hash])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to("0x01"))

    @lcc.test("Check method 'eth_getCode'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def eth_get_code(self):
        self.create_contract()
        self.create_contract()
        payload = self.rpc_call("eth_getCode", [self.contract_address, "0x02"])
        response = self.get_response(payload)
        require_that("'result'", response["result"][2:], equal_to(self.contract[166:]))

    # todo: BUG ECHO-1786. Undisabled
    @lcc.disabled()
    @lcc.test("Check method 'eth_sendRawTransaction'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def eth_send_raw_transaction(self):
        trx_hash = self.create_contract()
        payload = self.rpc_call("eth_sendRawTransaction", [trx_hash])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to("0x01"))

    @lcc.test("Check method 'eth_call'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.personal_new_account")
    def eth_call(self):
        # cycle for link contract to account's address
        for i in range(5):
            self.create_contract()
        data = "0x"
        payload = self.rpc_call("eth_call",
                                [{
                                    "from": self.new_account_address,
                                    "to": self.account_address
                                }]
                                )
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to(data))

    @lcc.test("Check method 'eth_estimateGas'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
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

    @lcc.test("Check method 'eth_getBlockByHash'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.eth_block_number")
    def eth_get_block_by_trx_hash(self):
        self.transfer()
        block_id = self.get_response(self.rpc_call("eth_blockNumber", []))
        block_hash = self.get_response(
            self.rpc_call("eth_getBlockByNumber", [block_id["result"], True]))["result"]["hash"]
        payload = self.rpc_call("eth_getBlockByHash", [block_hash, True])
        result = self.get_response(payload)["result"]
        self.validate_block(result)

    @lcc.test("Check method 'eth_getBlockByNumber'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.eth_block_number")
    def eth_get_block_by_number(self):
        self.transfer()
        block_id = self.get_response(self.rpc_call("eth_blockNumber", []))
        payload = self.rpc_call("eth_getBlockByNumber", [block_id["result"], True])
        result = self.get_response(payload)["result"]
        self.validate_block(result)

    # todo: BUG ECHO-1792. Undisabled
    @lcc.disabled()
    @lcc.test("Check method 'eth_getTransactionByHash'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def eth_get_transaction_by_hash(self):
        trx_hash = self.transfer()
        payload = self.rpc_call("eth_getTransactionByHash", [trx_hash])
        result = self.get_response(payload)["result"]
        self.validate_block(result)

    @lcc.test("Check method 'eth_getTransactionByBlockHashAndIndex'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def eth_get_transaction_by_hash_and_index(self):
        self.transfer()
        block_id = self.get_response(self.rpc_call("eth_blockNumber", []))
        block_hash = self.get_response(
            self.rpc_call("eth_getBlockByNumber", [block_id["result"], True]))["result"]["hash"]
        payload = self.rpc_call("eth_getTransactionByBlockHashAndIndex", [block_hash, "0x00"])
        result = self.get_response(payload)["result"]
        self.validate_transaction(result)

    # todo: BUG ECHO-1788. Undisabled
    @lcc.disabled()
    @lcc.test("Check method 'eth_getTransactionReceipt'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def eth_get_transaction_receipt(self):
        # todo: BUG ECHO-1788. Uncomment and delete pending trx getting process
        # trx_hash = self.create_contract()
        self.transfer()
        block_id = self.get_response(self.rpc_call("eth_blockNumber", []))
        trx_hash = self.get_response(
            self.rpc_call("eth_getBlockByNumber", [block_id["result"], True]))["result"]["transactions"][0]["hash"]
        payload = self.rpc_call("eth_getTransactionReceipt", [trx_hash])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to("ggg"))

    @lcc.test("Check method 'eth_pendingTransactions'")
    @lcc.depends_on("TestRPC.TestRPC.TestRPC.main_check")
    def eth_pending_transactions(self):
        self.create_contract()
        payload = self.rpc_call("eth_pendingTransactions", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], is_list())
