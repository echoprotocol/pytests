# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, has_length, equal_to

from common.base_test import BaseTest
from fixtures.base_fixtures import get_random_integer

SUITE = {
    "description": "Broadcast transactions with callback and expiration"
}


@lcc.tags("Manual testing")
@lcc.disabled()
@lcc.prop("main", "type")
@lcc.tags("scenarios", "broadcast_transactions_with_callback")
@lcc.suite("Check scenario 'broadcast_transactions_with_callback'")
class BroadcastTransactionsWithCallback(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__network_broadcast_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None

    def add_to_datetime(self, str_datetime, days=0, hours=0, minutes=0, seconds=0):
        formatted_datetime = datetime.strptime(str_datetime, "%Y-%m-%dT%H:%M:%S")
        formatted_datetime = formatted_datetime + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        return formatted_datetime.strftime("%Y-%m-%dT%H:%M:%S")

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__network_broadcast_identifier = self.get_identifier("network_broadcast")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', network_broadcast='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier,
                self.__network_broadcast_identifier))

        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc1 = self.get_account_id(self.accounts[1], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

    def get_head_block_num(self):
        return self.echo.api.database.get_dynamic_global_properties()["head_block_number"]

    def setup_test(self, test):
        lcc.set_step("Setup for '{}'".format(str(test).split(".")[-1]))
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)
        lcc.log_info("Canceled all subscriptions successfully")

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'get_block_tx_number'")
    def method_main_check(self):
        subscription_callback_id, trx_to_broadcast = get_random_integer(), \
                                                     999
        signed_trx = []

        lcc.set_step("Prepare transfer's operations to broadcast")
        for i in range(trx_to_broadcast):
            transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                      from_account_id=self.echo_acc0,
                                                                      to_account_id=self.echo_acc1, amount=i + 1)
            collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
            datetime_str = self.get_datetime(global_datetime=True)
            datetime_str = self.add_to_datetime(datetime_str, seconds=60)
            signed_trx.append(self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                      expiration=datetime_str, no_broadcast=True, log_broadcast=True))
        lcc.log_info("{} transactions prepared".format(trx_to_broadcast))

        lcc.set_step("Broadcast transaction to the next block")
        current_block = self.get_head_block_num()
        params = [subscription_callback_id, signed_trx[0]]
        response_id = self.send_request(self.get_request("broadcast_transaction_with_callback", params),
                                        self.__network_broadcast_identifier)
        self.get_response(response_id)
        while True:
            expected_block = self.get_head_block_num()
            if expected_block != current_block:
                for signed_tx in signed_trx[1:]:
                    params = [subscription_callback_id, signed_tx]
                    response_id = self.send_request(self.get_request("broadcast_transaction_with_callback", params),
                                                    self.__network_broadcast_identifier, debug_mode=True)
                    self.get_response(response_id)
                break
        lcc.log_info("Transactions broadcasted")

        lcc.set_step("Get block id and check that all {} transactions added successfully".format(trx_to_broadcast))
        notice = self.get_notice(subscription_callback_id)
        block_num = notice["block_num"]

        response_id = self.send_request(self.get_request("get_block", [block_num]), self.__database_api_identifier)
        transactions = self.get_response(response_id)["result"]["transactions"]
        if len(transactions) != trx_to_broadcast:
            response_id = self.send_request(self.get_request("get_block", [block_num]),
                                            self.__database_api_identifier)
            new_transactions = self.get_response(response_id, log_response=True)["result"]["transactions"]
            check_that("transactions in block number", (transactions + new_transactions), has_length(trx_to_broadcast))
        else:
            check_that("transactions in block number", transactions, has_length(trx_to_broadcast))
        lcc.set_step("Check 'get_block_tx_number' response")
        response_id = self.send_request(self.get_request("get_block_header", [block_num + 1]),
                                        self.__database_api_identifier)
        block_id = self.get_response(response_id, log_response=True)["result"]["previous"]
        response_id = self.send_request(self.get_request("get_block_tx_number", [block_id + 2]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id, log_response=True)["result"]
        check_that("block transaction number", result, equal_to(trx_to_broadcast))
