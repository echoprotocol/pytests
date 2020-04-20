# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
import requests
from lemoncheesecake.matching import require_that, has_length, require_that_in, is_integer, equal_to, is_none, \
    is_true, \
    check_that, is_false, not_equal_to, is_list

from common.base_test import BaseTest

SUITE = {
    "description": "Run tests for JSON PRC interface of ECHO node"
}


# todo: undisabled on github
@lcc.disabled()
@lcc.prop("main", "type")
@lcc.tags("eth_rpc")
@lcc.suite("Check JSON PRC interface")
class EthRPC(BaseTest):

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
        lcc.log_debug("request")
        return payload

    def get_response(self, payload):
        response = requests.post(self.test_rcp_url, json=payload).json()
        lcc.log_debug("response")
        if require_that("eth-rpc response", response, has_length(3)):
            require_that_in(
                response,
                "id", is_integer(),
                "jsonrpc", equal_to("2.0")
            )
            return response

    def transfer(self):
        payload = self.rpc_call("eth_sendRawTransaction",
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
        self.rpcPort = 56454
        self.test_rcp_url = 'http://localhost:' + str(self.rpcPort)
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

    @lcc.test("Check connection to JSON PRC interface")
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

    @lcc.test("Check method 'web3_clientVersion'")
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.main_check")
    def web3_client_version(self):
        result = "ECHO/0.17.0-rc.0/Linux.64-bit"
        payload = self.rpc_call("web3_clientVersion", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to(result))

    @lcc.test("Check method 'eth_chain_id'")
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.main_check")
    def eth_chain_id(self):
        chain_id = "0xc5baa05a82d607bdbd50d3ac1cbca45536e5c09bf2c1e91334131fb3d4f59262"
        payload = self.rpc_call("eth_chainId", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to(chain_id))

    @lcc.test("Check method 'web3_sha3'")
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.main_check")
    def web3_sha3(self):
        payload = self.rpc_call("web3_sha3", [self.SHA3_trx_hash])
        response = self.get_response(payload)
        if not self.type_validator.is_SHA3_256(response["result"]):
            lcc.log_error("Wrong format of 'result', got: '{}'".format(response["result"]))
        else:
            lcc.log_info("'result' has correct format: hex")

    @lcc.test("Check method 'net_version'")
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.main_check")
    def net_version(self):
        echo_devnet = "3"
        payload = self.rpc_call("net_version", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to(echo_devnet))

    @lcc.test("Check method 'net_listening'")
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.main_check")
    def net_listening(self):
        payload = self.rpc_call("net_listening", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], is_true())

    @lcc.test("Check method 'net_peerCount'")
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.main_check")
    def net_peer_count(self):
        p2p_quantity = "0x00"
        payload = self.rpc_call("net_peerCount", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to(p2p_quantity))

    @lcc.test("Check method 'eth_protocolVersion'")
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.main_check")
    def eth_protocol_version(self):
        eth_version = "0x3f"
        payload = self.rpc_call("eth_protocolVersion", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to(eth_version))

    @lcc.test("Check method 'eth_syncing'")
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.main_check")
    def eth_syncing(self):
        payload = self.rpc_call("eth_syncing", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], is_false())

    @lcc.test("Check method 'eth_coinbase'")
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.main_check")
    def eth_coinbase(self):
        payload = self.rpc_call("eth_coinbase", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to(self.account_address))

    @lcc.test("Check method 'eth_gasPrice'")
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.main_check")
    def eth_gas_price(self):
        gas_price = "0x01"
        payload = self.rpc_call("eth_gasPrice", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to(gas_price))

    @lcc.test("Check method 'eth_block_number'")
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.main_check")
    def eth_block_number(self):
        payload = self.rpc_call("eth_blockNumber", [])
        response = self.get_response(payload)
        if not self.type_validator.is_eth_block_number(response["result"]):
            lcc.log_error("Wrong format of 'eth_blockNumber', got: '{}'".format(response["result"]))
        else:
            lcc.log_info("'result' has correct format: eth_blockNumber")

    @lcc.test("Check method 'eth_getBalance'")
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.main_check")
    def eth_get_balance(self):
        payload = self.rpc_call("eth_getBalance", [self.account_address, "latest"])
        response = self.get_response(payload)
        if not self.type_validator.is_eth_balance(response["result"]):
            lcc.log_error("Wrong format of 'eth_balance', got: '{}'".format(response["result"]))
        else:
            lcc.log_info("'result' has correct format: eth_balance")

    @lcc.disabled()
    @lcc.test("Check method 'eth_getStorageAt'")
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.main_check")
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
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.main_check")
    def eth_get_transaction_count(self):
        payload = self.rpc_call("eth_getTransactionCount", [self.account_address, "latest"])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to("0x01"))

    @lcc.test("Check method 'eth_getBlockTransactionCountByHash'")
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.main_check")
    def eth_get_block_transaction_count_by_trx_hash(self):
        self.transfer()
        block_id = self.get_response(self.rpc_call("eth_blockNumber", []))
        block_hash = self.get_response(
            self.rpc_call("eth_getBlockByNumber", [block_id["result"], True]))["result"]["hash"]
        payload = self.rpc_call("eth_getBlockTransactionCountByHash", [block_hash])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to("0x01"))

    @lcc.test("Check method 'eth_getCode'")
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.main_check")
    def eth_get_code(self):
        self.create_contract()
        payload = self.rpc_call("eth_getCode", [self.contract_address, "0x02"])
        response = self.get_response(payload)
        require_that("'result'", response["result"][2:], equal_to(self.contract[166:]))

    # # todo: BUG ECHO-1786. Undisabled
    @lcc.disabled()
    @lcc.test("Check method 'eth_sendRawTransaction'")
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.main_check")
    def eth_send_raw_transaction(self):
        trx_hash = {
            "ref_block_num": 50,
            "ref_block_prefix": 1826023738,
            "expiration": "2020-02-17T12:17:55",
            "operations": [
                [
                    0,
                    {
                        "fee": {
                            "amount": 20,
                            "asset_id": "1.3.0"
                        },
                        "from": "1.2.12",
                        "to": "1.2.13",
                        "amount": {
                            "amount": 7,
                            "asset_id": "1.3.0"
                        },
                        "extensions": []
                    }
                ]
            ],
            "extensions": [],
            "signatures": [
                "3040a09a0fb0bbc7c1263f68c9d46e8dd67c5d32be8d46e8dd67c5d32be8058bb8eb970870f072445675058bb8eb970870f072445675fd1c943e7ece8205cea4165da96b67d9bf2ff4660b5a710264cca70185ffdcf4b7c6cb0095de1df2b9e88de341019f575b1e0c"
            ]
        }
        payload = self.rpc_call("eth_sendRawTransaction", [trx_hash])
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to("0x01"))

    @lcc.test("Check method 'eth_call'")
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.main_check")
    def eth_call(self):
        # cycle for link contract to account's address
        for i in range(5):
            self.create_contract()
        data = "0x"
        payload = self.rpc_call("eth_call",
                                [{
                                    "from": self.new_account_address,
                                    "to": self.account_address
                                }, "latest"]
                                )
        response = self.get_response(payload)
        require_that("'result'", response["result"], equal_to(data))

    @lcc.test("Check method 'eth_estimateGas'")
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.main_check")
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
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.eth_block_number")
    def eth_get_block_by_trx_hash(self):
        self.transfer()
        block_id = self.get_response(self.rpc_call("eth_blockNumber", []))
        block_hash = self.get_response(
            self.rpc_call("eth_getBlockByNumber", [block_id["result"], True]))["result"]["hash"]
        payload = self.rpc_call("eth_getBlockByHash", [block_hash, True])
        result = self.get_response(payload)["result"]
        self.validate_block(result)

    @lcc.test("Check method 'eth_getBlockByNumber'")
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.eth_block_number")
    def eth_get_block_by_number(self):
        self.transfer()
        block_id = self.get_response(self.rpc_call("eth_blockNumber", []))
        payload = self.rpc_call("eth_getBlockByNumber", [block_id["result"], True])
        result = self.get_response(payload)["result"]
        self.validate_block(result)

    # todo: BUG ECHO-1792. Undisabled
    @lcc.disabled()
    @lcc.test("Check method 'eth_getTransactionByHash'")
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.main_check")
    def eth_get_transaction_by_hash(self):
        trx_hash = self.transfer()
        payload = self.rpc_call("eth_getTransactionByHash", [trx_hash])
        result = self.get_response(payload)["result"]
        self.validate_block(result)

    @lcc.test("Check method 'eth_getTransactionByBlockHashAndIndex'")
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.main_check")
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
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.main_check")
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
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.main_check")
    def eth_pending_transactions(self):
        self.create_contract()
        payload = self.rpc_call("eth_pendingTransactions", [])
        response = self.get_response(payload)
        require_that("'result'", response["result"], is_list())

    @lcc.test("Check method 'echo_requestRegistrationTask'")
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.main_check")
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
    @lcc.depends_on("EthRPC.EthRPC.EthRPC.echo_request_registration_task")
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
