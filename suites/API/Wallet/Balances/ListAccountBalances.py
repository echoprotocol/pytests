# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc

SUITE = {
    "description": "Method 'list_account_balances'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_blocks_transactions", "wallet_list_account_balances")
@lcc.suite("Check work of method 'list_account_balances'", rank=1)
class GetTransactionId(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
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

    @lcc.test("Simple work of method 'wallet_list_account_balances'")
    def method_main_check(self):
        response = self.send_wallet_request("list_account_balances", [self.echo_acc0], log_response=False)
        if 'result' in response:
            lcc.log_check('Correct response result received', True)
            if self.type_validator.is_digit(response['result'][0]["amount"]):
                lcc.log_check("Amount has correct format.", True)
            else:
                lcc.log_error("Wrong amount format!")
            if self.type_validator.is_asset_id(response['result'][0]["asset_id"]):
                lcc.log_check("Asset_id has correct format.", True)
            else:
                lcc.log_error("Wrong asset_id format!")
        else:
            lcc.log_error("Response received with error")
