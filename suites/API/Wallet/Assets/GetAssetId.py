# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import INIT4_PK, INIT5_PK, WALLET_PASSWORD

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'get_asset_id'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_assets", "wallet_get_asset_id")
@lcc.suite("Check work of method 'get_asset_id'", rank=1)
class GetAssetId(WalletBaseTest, BaseTest):

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

    @lcc.test("Simple work of method 'wallet_get_asset_id'")
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
        lcc.set_step("Import key")
        self.send_wallet_request("import_key", ['init5', INIT5_PK], log_response=False)
        lcc.log_info("Key imported")

        lcc.set_step("Check method get_asset_id")
        self.init4 = self.get_account_id('init4', self.__database_api_identifier, self.__registration_api_identifier)
        self.init5 = self.get_account_id('init5', self.__database_api_identifier, self.__registration_api_identifier)
        asset_name = get_random_valid_asset_name

        lcc.log_info("Create {} asset".format(asset_name))
        asset_options = self.echo_ops.get_asset_create_operation(
            echo=self.echo, issuer=self.init4, symbol=asset_name
        )[1]['common_options']
        self.send_wallet_request(
            "create_asset", [self.init4, asset_name, 10, asset_options, None, True], log_response=False
        )
        self.produce_block(self.__database_api_identifier)

        asset_id = self.send_wallet_request("get_asset_id", [asset_name], log_response=False)['result']
        asset = self.send_wallet_request("get_asset", [asset_name], log_response=False)['result']
        check_that("asset id", asset['id'], equal_to(asset_id), quiet=True)
