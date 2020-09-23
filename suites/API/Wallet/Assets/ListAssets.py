# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc

SUITE = {
    "description": "Method 'list_assets'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_balances", "wallet_list_assets")
@lcc.suite("Check work of method 'list_assets'", rank=1)
class ListAssets(WalletBaseTest, BaseTest):

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

    @lcc.test("Simple work of method 'wallet_list_assets'")
    def method_main_check(self):
        lcc.set_step("Check list_assets method")
        response = self.send_wallet_request("list_assets", ["", 10], log_response=False)
        test_successful = True
        for result in response['result']:
            if not self.type_validator.is_asset_id(result['id']):
                test_successful = False
        if test_successful:
            lcc.log_info("Method list_assets complited successfully")
        else:
            lcc.log_error("Wrong asset id returned")
