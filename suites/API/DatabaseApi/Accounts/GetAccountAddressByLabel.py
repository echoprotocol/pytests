# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, require_that

SUITE = {
    "description": "Methods: 'get_account_address_by_label'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "database_api", "database_api_accounts", "get_account_address_by_label")
@lcc.suite("Check work of methods: 'get_account_address_by_label'", rank=1)
class GetAccountAddressByLabel(BaseTest):

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

    @lcc.test("Simple work of methods: 'get_account_address_by_label'")
    @lcc.depends_on("API.DatabaseApi.Accounts.GetAccountAddresses.GetAccountAddresses.method_main_check")
    def method_main_check(self, get_random_valid_account_name, get_random_string):
        new_account = get_random_valid_account_name
        label = get_random_string

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(
            new_account, self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get addresses of created account in the network")
        params = [new_account, label]
        response_id = self.send_request(
            self.get_request("get_account_address_by_label", params), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_account_address_by_label' of new account")

        lcc.set_step("Check simple work of method 'get_account_address_by_label'")
        check_that("'new account addresses'", response["result"], equal_to(None), quiet=True)

        lcc.set_step("Create account address for new account")
        self.utils.perform_account_address_create_operation(self, new_account, label, self.__database_api_identifier)
        lcc.log_info("Account address create operation for new account performed")

        lcc.set_step("Get new address of created account in the network")
        params = [new_account, label]
        response_id = self.send_request(
            self.get_request("get_account_address_by_label", params), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_account_address_by_label' of new account")
        result = response["result"]

        lcc.set_step("Get list of addresses of created account in the network")
        params = [new_account, 0, 100]
        response_id = self.send_request(
            self.get_request("get_account_addresses", params), self.__database_api_identifier
        )
        address = self.get_response(response_id)['result'][0]['address']
        lcc.log_info("Call method 'get_account_addresses' of new account")

        lcc.set_step("Check new account address in method 'get_account_address_by_label'")
        require_that('address', result, equal_to(address), quiet=True)
