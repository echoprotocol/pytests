# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc

SUITE = {
    "description": "Method 'list_id_balances'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_balances", "wallet_list_id_balances")
@lcc.suite("Check work of method 'list_id_balances'", rank=1)
class ListIdBalances(WalletBaseTest, BaseTest):

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
            "API identifiers are: database='{}', registration='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier
            )
        )
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo account are: #1='{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_list_id_balances'")
    def method_main_check(self):
        lcc.set_step("Check list id balances method")
        result = self.send_wallet_request("list_id_balances", [self.echo_acc0], log_response=False)['result'][0]
        if self.type_validator.is_digit(result['amount']):
            lcc.log_info("Balance has correct format digit")
        else:
            lcc.log_error("Wrong format of balance")
        if self.type_validator.is_asset_id(result['asset_id']):
            lcc.log_info("Asset_id has correct format asset_id")
        else:
            lcc.log_error("Wrong format of asset_id")
