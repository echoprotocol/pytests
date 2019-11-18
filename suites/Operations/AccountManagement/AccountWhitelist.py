# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Operation 'account_whitelist'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "asset_transfer_operations", "account_whitelist")
@lcc.suite("Check work of method 'account_whitelist'", rank=1)
class AccountWhitelist(BaseTest):

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

    @lcc.test("Simple work of method 'account_whitelist'")
    def method_main_check(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name

        lcc.set_step("Register an account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Add account to 'whitelisted_accounts'")
        operation = self.echo_ops.get_account_whitelist_operation(self.echo, authorizing_account=self.echo_acc0,
                                                                  account_to_list=new_account, new_listing=1)

        fee = self.get_required_fee(operation, self.__database_api_identifier)[0].get("amount")
        self.utils.perform_transfer_operations(self, self.echo_acc0, new_account,
                                               self.__database_api_identifier, transfer_amount=fee)
        lcc.log_info("Needed amount '{}' to pay fee added to account '{}'".format(fee, new_account))

        lcc.set_step("Perform 'account_whitelist_operation' to add account to 'whitelisted_accounts'")
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        response_id = self.send_request(self.get_request("get_accounts", [[self.echo_acc0]]),
                                        self.__database_api_identifier)
        whitelisted_accounts = self.get_response(response_id)["result"][0]["whitelisted_accounts"][-1]
        check_that("whitelisted_accounts", new_account, equal_to(whitelisted_accounts))

        lcc.set_step("Add account to 'blacklisted_accounts'")
        operation = self.echo_ops.get_account_whitelist_operation(self.echo, authorizing_account=self.echo_acc0,
                                                                  account_to_list=new_account, new_listing=2)

        fee = self.get_required_fee(operation, self.__database_api_identifier)[0].get("amount")
        self.utils.perform_transfer_operations(self, self.echo_acc0, new_account,
                                               self.__database_api_identifier, transfer_amount=fee)
        lcc.log_info("Needed amount '{}' to pay fee added to account '{}'".format(fee, new_account))

        lcc.set_step("Perform 'account_whitelist_operation' to add account to 'blacklisted_accounts'")
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        response_id = self.send_request(self.get_request("get_accounts", [[self.echo_acc0]]),
                                        self.__database_api_identifier)
        blacklisted_accounts = self.get_response(response_id)["result"][0]["blacklisted_accounts"][-1]
        check_that("blacklisted_accounts", new_account, equal_to(blacklisted_accounts))

        lcc.set_step("Add account to 'whitelisted_accounts' and 'blacklisted_accounts'")
        operation = self.echo_ops.get_account_whitelist_operation(self.echo, authorizing_account=self.echo_acc0,
                                                                  account_to_list=new_account, new_listing=3)

        fee = self.get_required_fee(operation, self.__database_api_identifier)[0].get("amount")
        self.utils.perform_transfer_operations(self, self.echo_acc0, new_account,
                                               self.__database_api_identifier, transfer_amount=fee)
        lcc.log_info("Needed amount '{}' to pay fee added to account '{}'".format(fee, new_account))

        lcc.set_step("Perform 'account_whitelist_operation' to add account to either, white and black list")
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        response_id = self.send_request(self.get_request("get_accounts", [[self.echo_acc0]]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)
        whitelisted_accounts = result["result"][0]["whitelisted_accounts"][-1]
        blacklisted_accounts = result["result"][0]["blacklisted_accounts"][-1]
        check_that("whitelisted_accounts", new_account, equal_to(whitelisted_accounts))
        check_that("blacklisted_accounts", new_account, equal_to(blacklisted_accounts))

        lcc.set_step("Remove account from 'whitelisted_accounts' and 'blacklisted_accounts'")
        operation = self.echo_ops.get_account_whitelist_operation(self.echo, authorizing_account=self.echo_acc0,
                                                                  account_to_list=new_account, new_listing=0)

        fee = self.get_required_fee(operation, self.__database_api_identifier)[0].get("amount")
        self.utils.perform_transfer_operations(self, self.echo_acc0, new_account,
                                               self.__database_api_identifier, transfer_amount=fee)
        lcc.log_info("Needed amount '{}' to pay fee added to account '{}'".format(fee, new_account))

        lcc.set_step("Perform 'account_whitelist_operation' to remove account from any, white and black list")
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        response_id = self.send_request(self.get_request("get_accounts", [[self.echo_acc0]]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)
        whitelisted_accounts = result["result"][0]["whitelisted_accounts"]
        blacklisted_accounts = result["result"][0]["blacklisted_accounts"]
        check_that("whitelisted_accounts", whitelisted_accounts, equal_to([]))
        check_that("blacklisted_accounts", blacklisted_accounts, equal_to([]))
