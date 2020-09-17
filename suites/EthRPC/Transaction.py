# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from project import ETHRPC_URL

import lemoncheesecake.api as lcc
import requests
from lemoncheesecake.matching import (
    check_that, equal_to, has_length, is_integer, is_list, is_none, require_that, require_that_in
)

SUITE = {
    "description": "Run 'transaction part' tests for JSON PRC interface of ECHO node"
}


@lcc.prop("main", "type")
@lcc.tags("eth_rpc", "eth_rpc_transaction")
@lcc.suite("Check EthRPC 'transaction part'")
class Transaction(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None
        self.account_address = None
        self.contract = self.get_byte_code("piggy", "code")

    def rpc_call(self, method, params):
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0,
        }
        return payload

    def get_ethrpc_response(self, payload):
        response = requests.post(ETHRPC_URL, json=payload).json()
        if require_that("eth-rpc response", response, has_length(3)):
            require_that_in(response, "id", is_integer(), "jsonrpc", equal_to("2.0"))
            return response

    def transfer(self):
        transfer_operation = self.echo_ops.get_transfer_operation(
            echo=self.echo, from_account_id=self.echo_acc0, to_account_id=self.echo_acc1, amount=1
        )
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        signed_tx = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, ethrpc_broadcast=True)
        signatures = signed_tx["signatures"]
        signatures_hex = bytes(signatures).hex()[2:]
        del signed_tx["signatures"]
        signed_tx_hex = bytes(signed_tx).hex()
        params = [signed_tx_hex + "01" + signatures_hex + "00"]
        payload = self.rpc_call("eth_sendRawTransaction", params)
        trx_hash = self.get_ethrpc_response(payload)["result"]
        return trx_hash

    def create_contract(self):
        operation = self.echo_ops.get_contract_create_operation(
            echo=self.echo,
            registrar=self.echo_acc0,
            bytecode=self.contract,
            value_amount=1,
            value_asset_id=self.echo_asset
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_id = self.get_contract_id(contract_result)
        contract_address = self.contract_address[:-1] + hex(int(contract_id.split(".")[-1]))[-1]
        lcc.log_info("Created contract address: {}".format(contract_address))
        return contract_address

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier
            )
        )
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        self.echo_acc1 = self.get_account_id(
            self.accounts[1], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

        self.account_address = "0x0000000000000000000000000000000000000060"
        self.contract_address = "0x0100000000000000000000000000000000000000"

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Check connection to EthPRC interface.")
    def main_check(self):
        message = {
            'code': -32600,
            'message': 'Missing or invalid method'
        }
        payload = self.rpc_call("", "")
        response = requests.post(ETHRPC_URL, json=payload).json()
        if require_that("json-rpc response", response, has_length(3)):
            require_that_in(response, "id", is_none(), "jsonrpc", equal_to("2.0"), "error", equal_to(message))

    @lcc.test("Check method 'eth_getBlockTransactionCountByHash'")
    @lcc.depends_on("EthRPC.Transaction.Transaction.main_check")
    def eth_get_block_transaction_count_by_trx_hash(self):
        self.transfer()
        block_id = self.get_ethrpc_response(self.rpc_call("eth_blockNumber", []))
        block_hash = self.get_ethrpc_response(self.rpc_call("eth_getBlockByNumber",
                                                            [block_id["result"], True]))["result"]["hash"]
        payload = self.rpc_call("eth_getBlockTransactionCountByHash", [block_hash])
        response = self.get_ethrpc_response(payload)
        require_that("'result'", response["result"], equal_to("0x01"))

    @lcc.test("Check method 'eth_getBalance'")
    @lcc.depends_on("EthRPC.Transaction.Transaction.main_check")
    def eth_get_balance(self):
        payload = self.rpc_call("eth_getBalance", [self.account_address, "latest"])
        response = self.get_ethrpc_response(payload)
        balance = self.echo.api.database.get_account_balances("1.2.60", ["1.3.0"])[0]["amount"]
        require_that('account balance', int(response["result"], 16), equal_to(int(balance)))

    @lcc.test("Check method 'eth_getTransactionCount'")
    @lcc.depends_on("EthRPC.Transaction.Transaction.main_check")
    def eth_get_transaction_count(self):
        payload = self.rpc_call("eth_getTransactionCount", [self.account_address, "latest"])
        response = self.get_ethrpc_response(payload)
        account_ops = self.echo.api.history.get_account_history("1.2.60", "1.6.0", 100, "1.6.0")
        require_that('account balance', int(response["result"], 16), equal_to(len(account_ops)))

    @lcc.test("Check method 'eth_getBlockTransactionCountByNumber'")
    @lcc.depends_on("EthRPC.Transaction.Transaction.main_check")
    def eth_get_block_transaction_count_by_number(self):
        block_id = self.get_ethrpc_response(self.rpc_call("eth_blockNumber", []))["result"]
        payload = self.rpc_call("eth_getBlockTransactionCountByNumber", [int(block_id, 16)])
        response = self.get_ethrpc_response(payload)
        require_that('block transaction count', response["result"], equal_to("0x01"))

    @lcc.test("Check method 'eth_getCode'")
    @lcc.depends_on("EthRPC.Transaction.Transaction.main_check")
    def eth_get_code(self):
        contract_address = self.create_contract()
        payload = self.rpc_call("eth_getCode", [contract_address, ''])
        response = self.get_ethrpc_response(payload)
        require_that("'result'", response["result"][2:], equal_to(self.contract[166:]))

    @lcc.test("Check method 'eth_sendRawTransaction'")
    @lcc.depends_on("EthRPC.Transaction.Transaction.main_check")
    def eth_send_raw_transaction(self):
        transfer_operation = self.echo_ops.get_transfer_operation(
            echo=self.echo, from_account_id=self.echo_acc0, to_account_id=self.echo_acc1, amount=1
        )
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        signed_tx = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, ethrpc_broadcast=True)
        signatures = signed_tx["signatures"]
        signatures_hex = bytes(signatures).hex()[2:]
        del signed_tx["signatures"]
        signed_tx_hex = bytes(signed_tx).hex()
        params = [signed_tx_hex + "01" + signatures_hex + "00"]
        payload = self.rpc_call("eth_sendRawTransaction", params)
        trx_hash = self.get_ethrpc_response(payload)
        if not self.type_validator.is_eth_hash(trx_hash["result"]):
            lcc.log_error("Wrong format of 'trx_hash', got: '{}'".format(trx_hash["result"]))
        else:
            lcc.log_info("'result' has correct format: eth_hash")

    @lcc.test("Check method 'eth_call'")
    @lcc.depends_on("EthRPC.Transaction.Transaction.main_check")
    def eth_call(self):
        data = "0x"
        payload = self.rpc_call(
            "eth_call", [{
                "from": "0x0100000000000000000000000000000000000006",
                "to": "0x0100000000000000000000000000000000000000"
            }, "latest"]
        )
        response = self.get_ethrpc_response(payload)
        require_that("'result'", response["result"], equal_to(data))

    @lcc.test("Check method 'eth_getBlockByHash'")
    @lcc.depends_on("EthRPC.Config.Config.eth_block_number")
    def eth_get_block_by_trx_hash(self):
        self.transfer()
        block_id = self.get_ethrpc_response(self.rpc_call("eth_blockNumber", []))
        block_hash = self.get_ethrpc_response(self.rpc_call("eth_getBlockByNumber",
                                                            [block_id["result"], True]))["result"]["hash"]
        payload = self.rpc_call("eth_getBlockByHash", [block_hash, True])
        result = self.get_ethrpc_response(payload)["result"]
        self.object_validator.validate_ethrpc_block(result)

    @lcc.test("Check method 'eth_getBlockByNumber'")
    @lcc.depends_on("EthRPC.Config.Config.eth_block_number")
    def eth_get_block_by_number(self):
        self.transfer()
        block_id = self.get_ethrpc_response(self.rpc_call("eth_blockNumber", []))
        payload = self.rpc_call("eth_getBlockByNumber", [block_id["result"], True])
        result = self.get_ethrpc_response(payload)["result"]
        self.object_validator.validate_ethrpc_block(result)

    @lcc.test("Check method 'eth_getTransactionByHash'")
    @lcc.depends_on("EthRPC.Transaction.Transaction.main_check")
    def eth_get_transaction_by_hash(self):
        trx_hash = self.transfer()
        payload = self.rpc_call("eth_getTransactionByHash", [trx_hash])
        result = self.get_ethrpc_response(payload)["result"]
        self.object_validator.validate_ethrpc_transaction(result)

    @lcc.test("Check method 'eth_getTransactionByBlockHashAndIndex'")
    @lcc.depends_on("EthRPC.Transaction.Transaction.main_check")
    def eth_get_transaction_by_hash_and_index(self):
        self.transfer()
        block_id = self.get_ethrpc_response(self.rpc_call("eth_blockNumber", []))
        block_hash = self.get_ethrpc_response(self.rpc_call("eth_getBlockByNumber",
                                                            [block_id["result"], True]))["result"]["hash"]
        payload = self.rpc_call("eth_getTransactionByBlockHashAndIndex", [block_hash, "0x00"])
        result = self.get_ethrpc_response(payload)["result"]
        self.object_validator.validate_ethrpc_transaction(result)

    @lcc.test("Check method 'eth_getTransactionReceipt'")
    @lcc.depends_on("EthRPC.Transaction.Transaction.main_check")
    def eth_get_transaction_receipt(self):
        params = self.transfer()
        payload = self.rpc_call("eth_getTransactionReceipt", [params])
        receipt = self.get_ethrpc_response(payload)["result"]
        check_that("transactionHash", receipt["transactionHash"], equal_to(params))
        check_that("transactionIndex", receipt["transactionIndex"], equal_to("0x00"))
        block_id = self.get_ethrpc_response(self.rpc_call("eth_blockNumber", []))["result"]
        block_hash = self.get_ethrpc_response(self.rpc_call("eth_getBlockByNumber", [block_id, True]))["result"]["hash"]
        check_that("blockHash", receipt["blockHash"], equal_to(block_hash))
        check_that("blockNumber", receipt["blockNumber"], equal_to(block_id))
        check_that("from", receipt["from"], equal_to("0x000000000000000000000000000000000000000c"))
        check_that("to", receipt["to"], equal_to("0x000000000000000000000000000000000000000d"))
        # todo: bug ECHO-2324
        # check_that("cumulativeGasUsed", receipt["cumulativeGasUsed"], equal_to("0x14"))
        # check_that("gasUsed", receipt["gasUsed"], equal_to("0x14"))
        check_that("contractAddress", receipt["contractAddress"], is_none())
        check_that("logs", receipt["logs"], is_list())
        check_that("logsBloom", receipt["logsBloom"], equal_to(""))
        check_that("status", receipt["status"], equal_to("0x01"))
