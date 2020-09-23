# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import INIT4_PK, WALLET_PASSWORD

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'create_asset'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_balances", "wallet_create_asset")
@lcc.suite("Check work of method 'create_asset'", rank=1)
class CreateAsset(WalletBaseTest, BaseTest):

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

    @lcc.test("Simple work of method 'wallet_create_asset'")
    def method_main_check(self, get_random_valid_asset_name):
        lcc.set_step("Unlock wallet")
        response = self.send_wallet_request("is_new", [], log_response=False)
        if response['result']:
            self.send_wallet_request("set_password", [WALLET_PASSWORD], log_response=False)
        response = self.send_wallet_request("is_locked", [], log_response=False)
        if response['result']:
            self.send_wallet_request("unlock", [WALLET_PASSWORD], log_response=False)
        lcc.log_info("Wallet unlocked")

        lcc.set_step("Import key")
        self.send_wallet_request("import_key", ['init4', INIT4_PK], log_response=False)
        lcc.log_info("Key imported")

        lcc.set_step("Check method import balance")
        self.init4 = self.get_account_id('init4', self.__database_api_identifier, self.__registration_api_identifier)
        asset_name = get_random_valid_asset_name
        asset_options = {
            "max_supply": "1000000000000000",
            "issuer_permissions": 15,
            "flags": 0,
            "core_exchange_rate":
                {
                    "base":
                        {
                            "amount": 1,
                            "asset_id": "1.3.0"
                        },
                    "quote":
                        {
                            "amount": 1,
                            "asset_id": "1.3.1"
                        }
                },
                "whitelist_authorities": [],
                "blacklist_authorities": [],
                "description": "ethereum asset",
                "extensions": []
        }

        self.send_wallet_request("create_asset", [self.init4, asset_name, 10, asset_options, None, True], log_response=False)
        self.produce_block(self.__database_api_identifier)
        result = self.send_wallet_request("list_assets", [asset_name, 10], log_response=False)['result']
        check_that("asset name", asset_name, equal_to(result[0]['symbol']))
