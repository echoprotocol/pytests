# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, not_equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Operation 'account_update'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "asset_transfer_operations", "account_update")
@lcc.suite("Check work of method 'account_update'", rank=1)
class AccountUpdate(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None


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
        lcc.log_info("Echo accounts are: #1='{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'account_update'")
    def method_main_check(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name

        lcc.set_step("Register an account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get info about account and store current 'delegating_account'")
        response_id = self.send_request(self.get_request("get_accounts", [[new_account]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        current_delegating_account = response["result"][0]["options"]["delegating_account"]
        lcc.log_info("Current delegating account of '{}' is '{}'".format(new_account, current_delegating_account))

        lcc.set_step("Add assets to a new account to pay a fee for operation")
        operation = self.echo_ops.get_account_update_operation(echo=self.echo, account=new_account,
                                                               delegating_account=self.echo_acc0)

        fee = self.get_required_fee(operation, self.__database_api_identifier)[0].get("amount")
        self.utils.perform_transfer_operations(self, self.echo_acc0, new_account,
                                               self.__database_api_identifier, transfer_amount=fee)
        lcc.log_info("Needed amount '{}' to pay fee added to account '{}'".format(fee, new_account))

        lcc.set_step("Perform 'account_update_operation' to change delegating_account")
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Check that delegating_account have been changed")
        response_id = self.send_request(self.get_request("get_accounts", [[new_account]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        new_delegating_account = response["result"][0]["options"]["delegating_account"]

        check_that("new_delegating_account", new_delegating_account, not_equal_to(current_delegating_account))
