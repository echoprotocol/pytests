# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'get_account_address_by_label'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_accounts", "wallet_get_account_address_by_label")
@lcc.suite("Check work of method 'get_account_address_by_label'", rank=1)
class GetAccountAddressesByLabel(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_get_account_address_by_label'")
    def method_main_check(self, get_random_string):
        label = get_random_string

        self.unlock_wallet()
        self.import_key('init4')

        lcc.set_step("Create a transaction to generate account address")
        self.init4 = self.get_account_id('init4', self.__database_api_identifier, self.__registration_api_identifier)

        self.send_wallet_request("generate_account_address", [self.init4, label, True], log_response=False)
        self.produce_block(self.__database_api_identifier)

        account_address_by_label = self.send_wallet_request(
            "get_account_address_by_label", [self.init4, label], log_response=False
        )['result']

        account_address = self.send_wallet_request(
            "get_account_addresses", [self.init4, 0, 100], log_response=False
        )['result'][-1]['address']
        check_that('account address', account_address_by_label, equal_to(account_address))
