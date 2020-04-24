# -*- coding: utf-8 -*-
from copy import deepcopy

import lemoncheesecake.api as lcc
import requests
from lemoncheesecake.matching import require_that, has_length, require_that_in, is_integer, equal_to, is_none, \
    check_that

from common.base_test import BaseTest

SUITE = {
    "description": "Run 'transaction part' tests for JSON PRC interface of ECHO node"
}


@lcc.prop("main", "type")
@lcc.tags("eth_rpc", "eth_rpc_transaction")
@lcc.suite("Check EthRPC 'transaction part'")
class Transaction(BaseTest):

    def __init__(self):
        super().__init__()
        self.rpcPort = None
        self.test_rcp_url = None
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None
        self.account_address = None

    def rpc_call(self, method, params):
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0,
        }
        lcc.log_debug("request {}".format(payload))
        return payload

    def get_rpc_response(self, payload):
        response = requests.post(self.test_rcp_url, json=payload).json()
        if require_that("eth-rpc response", response, has_length(3)):
            require_that_in(
                response,
                "id", is_integer(),
                "jsonrpc", equal_to("2.0")
            )
            return response

    def transfer(self):
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=self.echo_acc0,
                                                                  to_account_id=self.echo_acc1, amount=1)
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        signed_tx = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                            ethrpc_broadcast=True)
        signatures = signed_tx["signatures"]
        signatures_hex = bytes(signatures).hex()[2:]
        del signed_tx["signatures"]
        signed_tx_hex = bytes(signed_tx).hex()
        params = [signed_tx_hex + "01" + signatures_hex + "00"]
        payload = self.rpc_call("eth_sendRawTransaction", params)
        trx_hash = self.get_rpc_response(payload)
        return trx_hash

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc1 = self.get_account_id(self.accounts[1], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

        self.rpcPort = 56454
        self.test_rcp_url = 'http://localhost:' + str(self.rpcPort)
        self.account_address = "0x0000000000000000000000000000000000000006"

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Check connection to EthPRC interface.")
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

    @lcc.test("Check method 'eth_getBlockTransactionCountByHash'")
    @lcc.depends_on("EthRPC.Transaction.Transaction.main_check")
    def eth_get_block_transaction_count_by_trx_hash(self):
        self.transfer()
        block_id = self.get_rpc_response(self.rpc_call("eth_blockNumber", []))
        block_hash = self.get_rpc_response(
            self.rpc_call("eth_getBlockByNumber", [block_id["result"], True]))["result"]["hash"]
        payload = self.rpc_call("eth_getBlockTransactionCountByHash", [block_hash])
        response = self.get_rpc_response(payload)
        require_that("'result'", response["result"], equal_to("0x01"))

    @lcc.test("Check method 'eth_getBalance'")
    @lcc.depends_on("EthRPC.Transaction.Transaction.main_check")
    def eth_get_balance(self):
        payload = self.rpc_call("eth_getBalance", [self.account_address, "latest"])
        response = self.get_rpc_response(payload)
        balance = self.echo.api.database.get_account_balances("1.2.6", ["1.3.0"])[0]["amount"]
        require_that('account balance', int(response["result"], 16), equal_to(int(balance)))

    @lcc.test("Check method 'eth_getTransactionCount'")
    @lcc.depends_on("EthRPC.Transaction.Transaction.main_check")
    def eth_get_transaction_count(self):
        payload = self.rpc_call("eth_getTransactionCount", [self.account_address, "latest"])
        response = self.get_rpc_response(payload)
        account_ops = self.echo.api.history.get_account_history("1.2.6", "1.6.0", 100, "1.6.0")
        require_that('account balance', int(response["result"], 16), equal_to(len(account_ops)))





