# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import INIT5_PK

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'import_balance'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_balances", "wallet_import_balance")
@lcc.suite("Check work of method 'import_balance'", rank=1)
class ImportBalance(WalletBaseTest, BaseTest):

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

        self.init4 = self.get_account_id('init4', self.__database_api_identifier, self.__registration_api_identifier)
        lcc.log_info("Echo account are: #1='{}'".format(self.init4))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_import_balance'")
    def method_main_check(self):
        self.unlock_wallet()

        self.import_key('init4')

        lcc.set_step("Check method import balance")
        response = self.send_wallet_request("import_balance", [self.init4, True, [INIT5_PK]], log_response=False)
        lcc.log_info(str(response))
        check_that(
            "imported balance amount", response['result'][0][0]['operations'][0][1]['total_claimed']['amount'],
            equal_to(61)
        )
