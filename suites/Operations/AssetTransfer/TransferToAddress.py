# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Operation 'transfer_to_address'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "asset_transfer_operations", "transfer_to_address")
@lcc.suite("Check work of method 'transfer_to_address'", rank=1)
class TransferToAddress(BaseTest):

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

    @lcc.test("Simple work of method 'transfer_to_address'")
    def method_main_check(self, get_random_integer, get_random_string, get_random_valid_account_name):
        new_asset_amount = get_random_integer
        label = get_random_string
        new_account = get_random_valid_account_name
        lcc.set_step("Create new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Perform account address create")
        self.utils.perform_account_address_create_operation(self, new_account, label,
                                                            self.__database_api_identifier)
        lcc.log_info("Account address created successfully")

        lcc.set_step("Get account address")
        _from, limit = 0, 100
        params = [new_account, _from, limit]
        response_id = self.send_request(self.get_request("get_account_addresses", params),
                                        self.__database_api_identifier)
        to_address = self.get_response(response_id)["result"][0]["address"]
        lcc.log_info("new account address: '{}'".format(to_address))

        lcc.set_step("Get account balance before transfer")
        balance_before_transfer = self.utils.get_account_balances(self, new_account,
                                                                  self.__database_api_identifier)["amount"]
        lcc.log_info("Account balance before transfer".format(balance_before_transfer))

        lcc.set_step("Perform transfer to address operation")
        operation = self.echo_ops.get_transfer_to_address_operation(echo=self.echo, from_account_id=self.echo_acc0,
                                                                    to_address=to_address, amount=new_asset_amount)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("Operation transfer to address broadcasted successfully")

        lcc.set_step("Check that 'transfer_to_address' operation completed successfully")
        balance_after_transfer = self.utils.get_account_balances(self, new_account,
                                                                 self.__database_api_identifier)["amount"]
        check_that("transferred assets amount", balance_after_transfer - balance_before_transfer,
                   equal_to(new_asset_amount))
