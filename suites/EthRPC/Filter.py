# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from project import ETHRPC_URL

import lemoncheesecake.api as lcc
import requests
from lemoncheesecake.matching import (
    equal_to, has_item, has_length, is_integer, is_list, is_true, not_equal_to, require_that, require_that_in
)

SUITE = {
    "description": "Run 'filter part' tests for JSON PRC interface of ECHO node"
}


@lcc.prop("main", "type")
@lcc.tags("eth_rpc", "eth_rpc_filter")
@lcc.suite("Check EthRPC 'filter part'")
class Filter(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

    def rpc_call(self, method, params):
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0,
        }
        return payload

    def get_ethrpc_response(self, payload, log_response=False):
        response = requests.post(ETHRPC_URL, json=payload).json()
        if log_response:
            lcc.log_info("Response: {}".format(response))
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

        self.account_address = "0x0000000000000000000000000000000000000006"

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Check method 'eth_newFilter'")
    def eth_new_filter(self):
        payload = self.rpc_call("eth_newFilter", [{
            "topics": [""]
        }])
        filter_id = self.get_ethrpc_response(payload)["result"]
        require_that("filter_id", int(filter_id, 16), is_integer())
        self.transfer()
        payload = self.rpc_call("eth_getFilterChanges", [filter_id])
        filter_result = self.get_ethrpc_response(payload, log_response=True)["result"]
        require_that("filter_result", filter_result, equal_to([]))

    @lcc.test("Check method 'eth_newBlockFilter'")
    def eth_new_block_filter(self):
        payload = self.rpc_call("eth_newBlockFilter", [])
        filter_id = self.get_ethrpc_response(payload)["result"]
        require_that("filter_id", int(filter_id, 16), is_integer())
        self.transfer()
        payload = self.rpc_call("eth_getFilterChanges", [filter_id])
        filter_results = self.get_ethrpc_response(payload)["result"]
        require_that("filter_result", filter_results, not_equal_to([]))
        block_id = self.get_ethrpc_response(self.rpc_call("eth_blockNumber", []))
        block_hash = self.get_ethrpc_response(self.rpc_call("eth_getBlockByNumber",
                                                            [block_id["result"], True]))["result"]["hash"]
        require_that("filter_result", filter_results, has_item(block_hash))

    @lcc.test("Check method 'eth_newPendingTransactionFilter'")
    def eth_new_pending_transaction_filter(self):
        payload = self.rpc_call("eth_newPendingTransactionFilter", [])
        filter_id = self.get_ethrpc_response(payload)["result"]
        require_that("filter_id", int(filter_id, 16), is_integer())
        self.transfer()
        payload = self.rpc_call("eth_getFilterChanges", [filter_id])
        filter_results = self.get_ethrpc_response(payload)["result"]
        if require_that("filter_result", filter_results, not_equal_to([])):
            for pending_transaction in filter_results:
                if not self.type_validator.is_eth_hash(pending_transaction):
                    lcc.log_error("Wrong format of 'pending_transaction', got: '{}'".format(pending_transaction))
                else:
                    lcc.log_info("'pending_transaction' has correct format: eth_hash")

    @lcc.test("Check method 'eth_uninstallFilter'")
    def eth_uninstall_filter(self):
        error_massage = "Assert Exception: _filters.count(filter_id): filter not found"
        payload = self.rpc_call("eth_newPendingTransactionFilter", [])
        filter_id = self.get_ethrpc_response(payload)["result"]
        payload = self.rpc_call("eth_uninstallFilter", [filter_id])
        result = self.get_ethrpc_response(payload)["result"]
        require_that("result", result, is_true())
        payload = self.rpc_call("eth_getFilterChanges", [filter_id])
        filter_result = self.get_ethrpc_response(payload)["error"]
        require_that("filter_result", filter_result["message"], equal_to(error_massage))

    @lcc.test("Check method 'eth_getFilterLogs'")
    def eth_get_filter_logs(self):
        payload = self.rpc_call("eth_newBlockFilter", [])
        filter_id = self.get_ethrpc_response(payload)["result"]
        require_that("filter_id", int(filter_id, 16), is_integer())
        self.transfer()
        payload = self.rpc_call("eth_getFilterLogs", [filter_id])
        filter_results = self.get_ethrpc_response(payload)["result"]
        require_that("filter_result", filter_results, not_equal_to([]))
        block_id = self.get_ethrpc_response(self.rpc_call("eth_blockNumber", []))
        block_hash = self.get_ethrpc_response(self.rpc_call("eth_getBlockByNumber",
                                                            [block_id["result"], True]))["result"]["hash"]
        for filter_result in filter_results:
            require_that("filter_result", filter_result, equal_to(block_hash))

    @lcc.test("Check method 'eth_getLogs'")
    def eth_get_logs(self):
        payload = self.rpc_call("eth_getLogs", [{
            "topics": [""]
        }])
        result = self.get_ethrpc_response(payload)["result"]
        require_that("filter_id", result, is_list())
