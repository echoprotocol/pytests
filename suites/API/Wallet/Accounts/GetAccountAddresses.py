# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc

from lemoncheesecake.matching import check_that, greater_than

from common.wallet_base_test import WalletBaseTest
from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_account_addresses'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_accounts", "wallet_get_account_addresses")
@lcc.suite("Check work of method 'get_account_addresses'", rank=1)
class GetAccountAddresses(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
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
        lcc.log_info("Echo account are: #1='{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_get_account_addresses'")
    def method_main_check(self, get_random_string):
        label = get_random_string
        response = self.send_wallet_request("get_account_addresses", [self.echo_acc0, 0, 10], log_response=False)
        account_addresses_len = len(response['result'])
        lcc.set_step("Create account address for new account")
        self.utils.perform_account_address_create_operation(self, self.echo_acc0, label,
                                                            self.__database_api_identifier)
        lcc.log_info("Account address create operation for new account performed")
        lcc.set_step("Check that get_account_addresses returns more addresses than there were")
        response = self.send_wallet_request("get_account_addresses", [self.echo_acc0, 0, 10], log_response=False)
        currnt_account_addresses_len = len(response['result'])
        check_that('addicted addresses to {} account'.format(self.echo_acc0), currnt_account_addresses_len, greater_than(account_addresses_len))
