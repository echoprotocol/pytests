# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Operation 'account_address_create'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "asset_transfer_operations", "account_address_create")
@lcc.suite("Check work of method 'account_address_create'", rank=1)
class AccountAddressCreate(BaseTest):

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

    @lcc.test("Simple work of method 'account_address_create'")
    def method_main_check(self, get_random_valid_account_name, get_random_string):
        new_account = get_random_valid_account_name
        label = get_random_string

        lcc.set_step("Register an account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Perform 'account_address_create_operation'")
        operation = self.echo_ops.get_account_address_create_operation(echo=self.echo, owner=new_account,
                                                                       label=label)
        fee = self.get_required_fee(operation, self.__database_api_identifier)[0].get("amount")
        self.utils.perform_transfer_operations(self, self.echo_acc0, new_account,
                                               self.__database_api_identifier, transfer_amount=fee)
        lcc.log_info("Needed amount '{}' to pay fee added to account '{}'".format(fee, new_account))

        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                log_broadcast=False)
        lcc.log_info("Transaction broadcasted successfully")

        lcc.set_step("Check that account address created")
        response_id = self.send_request(self.get_request("get_account_addresses", [new_account, 0, 1]),
                                        self.__database_api_identifier)
        address = self.get_response(response_id)["result"][0]["address"]
        lcc.log_info("Account's: '{}', address created, address: '{}'".format(new_account, address))
        response_id = self.send_request(self.get_request("get_account_by_address", [address]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        check_that("'get_account_by_address' result", result, equal_to(new_account))
