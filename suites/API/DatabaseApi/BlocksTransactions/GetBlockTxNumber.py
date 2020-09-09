# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'get_block_tx_number'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_blocks_transactions", "get_block_tx_number")
@lcc.suite("Check work of method 'get_block_tx_number'", rank=1)
class GetBlockTxNumber(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__network_broadcast_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__network_broadcast_identifier = self.get_identifier("network_broadcast")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', network_broadcast='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier, self.__network_broadcast_identifier
            )
        )
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        self.echo_acc1 = self.get_account_id(
            self.accounts[1], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

    def get_head_block_num(self):
        return self.echo.api.database.get_dynamic_global_properties()["head_block_number"]

    def setup_test(self, test):
        lcc.set_step("Setup for '{}'".format(str(test).split(".")[-1]))
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)
        lcc.log_info("Canceled all subscriptions successfully")

    def teardown_test(self, test, status):
        lcc.set_step("Teardown for '{}'".format(str(test).split(".")[-1]))
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)
        lcc.log_info("Canceled all subscriptions successfully")
        lcc.log_info("Test {}".format(status))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'get_block_tx_number'")
    def method_main_check(self):
        operation_count = 1
        lcc.set_step("Perform transfer operation")
        self.utils.perform_transfer_operations(
            self,
            self.echo_acc0,
            self.echo_acc1,
            self.__database_api_identifier,
            operation_count=operation_count,
            log_broadcast=False
        )
        lcc.log_info("Transaction was broadcasted")
        lcc.set_step("Get block id and check that all {} transactions added successfully".format(operation_count))
        response_id = self.send_request(
            self.get_request("get_dynamic_global_properties"), self.__database_api_identifier
        )
        dynamic_global_property_object = self.get_response(response_id)["result"]
        head_block_id = dynamic_global_property_object['head_block_id']
        response_id = self.send_request(
            self.get_request("get_block_tx_number", [head_block_id]), self.__database_api_identifier
        )
        tx_number = self.get_response(response_id)["result"]
        check_that("block transaction number", tx_number, equal_to(operation_count))
