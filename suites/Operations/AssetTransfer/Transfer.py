# -*- coding: utf-8 -*-

from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Operation 'transfer'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "asset_transfer_operations", "transfer")
@lcc.suite("Check work of method 'transfer'", rank=1)
class Transfer(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'transfer'")
    def method_main_check(self, get_random_integer_up_to_ten):
        transfer_amount = get_random_integer_up_to_ten
        lcc.set_step("Get current account balance")
        response_id = self.send_request(
            self.get_request("get_account_balances", [self.echo_acc1, [self.echo_asset]]),
            self.__database_api_identifier
        )
        account_balance = self.get_response(response_id)["result"][0]["amount"]
        lcc.log_info("Account: {}, have balance: {}".format(self.echo_acc1, account_balance))

        lcc.set_step("Perform transfer operation")
        transfer_operation = self.echo_ops.get_transfer_operation(
            echo=self.echo, from_account_id=self.echo_acc0, amount=transfer_amount, to_account_id=self.echo_acc1
        )
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("'transfer' operation broadcasted successfully")

        lcc.set_step("Check that asset was transferred")
        response_id = self.send_request(
            self.get_request("get_account_balances", [self.echo_acc1, [self.echo_asset]]),
            self.__database_api_identifier
        )
        current_account_balance = self.get_response(response_id)["result"][0]["amount"]
        lcc.log_info("Account: {}, have balance: {}".format(self.echo_acc1, current_account_balance))
        check_that("transferred amount", current_account_balance - account_balance, equal_to(transfer_amount))
