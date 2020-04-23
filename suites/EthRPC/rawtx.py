# -*- coding: utf-8 -*-
from copy import deepcopy

import lemoncheesecake.api as lcc
import requests
from lemoncheesecake.matching import require_that, has_length, require_that_in, is_integer, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Rawtx"
}

#todo: undisabled on github
@lcc.disabled()
@lcc.tags("rawtx")
@lcc.prop("main", "type")
@lcc.suite("Check JSON PRC")
class Rawtx(BaseTest):

    def __init__(self):
        super().__init__()
        self.rpcPort = None
        self.test_rcp_url = None
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None

    def rpc_call(self, method, params):
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0,
        }
        lcc.log_debug("request {}".format(payload))
        return payload

    def get_response_a(self, payload):
        response = requests.post(self.test_rcp_url, json=payload).json()
        lcc.log_debug("response {}".format(response))
        if require_that("eth-rpc response", response, has_length(3)):
            require_that_in(
                response,
                "id", is_integer(),
                "jsonrpc", equal_to("2.0")
            )
            return response

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Check sendRawTransaction")
    def main_check(self):
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

        # def transfer(self):
        params = [signed_tx_hex+"01"+signatures_hex+"00"]
        lcc.log_info(str(params))
        payload = self.rpc_call("eth_sendRawTransaction", params)
        trx_hash = self.get_response_a(payload)


