# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'create_eth_address'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_sidechain_ethereum", "wallet_create_eth_address")
@lcc.suite("Check work of method 'create_eth_address'", rank=1)
class ImportKey(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.init4 = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_ethereum()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier
            )
        )
        self.init5 = self.get_account_id('init5', self.__database_api_identifier, self.__registration_api_identifier)

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_create_eth_address'")
    def method_main_check(self):
        self.unlock_wallet()

        self.import_key('init5')

        result = self.send_wallet_request('create_eth_address', [self.init5, True], log_response=False)['result']
        eth_address_object = self.utils.get_eth_address(self, self.init5, self.__database_api_identifier)["result"]

        lcc.set_step("Check get_eth_address method")
        result = self.send_wallet_request('get_eth_address', [self.init5], log_response=False)['result']
        check_that("eth address object", eth_address_object, equal_to(result))