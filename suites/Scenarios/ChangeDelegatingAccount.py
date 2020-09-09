# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, not_equal_to, require_that

SUITE = {
    "description": "Change delegating account using 'change_delegating_account'"
}


@lcc.prop("main", "type")
@lcc.tags("scenarios", "change_delegating_account")
@lcc.suite("Check scenario 'Change delegating account'")
class ChangeDelegatingAccount(BaseTest):

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
            "API identifiers are: database='{}', registration='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier
            )
        )
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("The scenario describes ability to delete or change delegating account.")
    def change_delegating_account_scenario(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name

        lcc.set_step("Registration an account")
        new_account = self.get_account_id(
            new_account, self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get info about account and store current 'delegating_account'")
        response_id = self.send_request(
            self.get_request("get_accounts", [[new_account]]), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        current_delegating_account = response["result"][0]["options"]["delegating_account"]
        lcc.log_info("Current delegating account of '{}' is '{}'".format(new_account, current_delegating_account))

        lcc.set_step("Add assets to a new account to pay a fee")
        operation = self.echo_ops.get_account_update_operation(
            echo=self.echo, account=new_account, delegating_account=self.echo_acc0
        )

        fee = self.get_required_fee(operation, self.__database_api_identifier).get("amount")
        if fee != 0:
            self.utils.perform_transfer_operations(
                self, self.echo_acc0, new_account, self.__database_api_identifier, transfer_amount=fee
            )
            lcc.log_info("Needed amount '{}' to pay fee added to account '{}'".format(fee, new_account))

        lcc.set_step("Perform 'account_update_operation' to change delegating_account")
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception("Account '{}' did not updated".format(new_account))
        lcc.log_info("Account '{}' successfully updated".format(new_account))

        lcc.set_step("Get info about account and store new 'delegating_account'")
        response_id = self.send_request(
            self.get_request("get_accounts", [[new_account]]), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        new_delegating_account = response["result"][0]["options"]["delegating_account"]
        lcc.log_info("New delegating account of '{}' is '{}'".format(new_account, new_delegating_account))

        lcc.set_step("Check that 'delegating_account' is updated")
        require_that("new 'delegating_account'", new_delegating_account, not_equal_to(current_delegating_account))

        check_that("new 'delegating_account'", new_delegating_account, equal_to(self.echo_acc0))
