# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'update_asset'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_assets", "wallet_update_asset")
@lcc.suite("Check work of method 'update_asset'", rank=1)
class UpdateAsset(WalletBaseTest, BaseTest):

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
        self.init5 = self.get_account_id('init5', self.__database_api_identifier, self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.init4, self.init5))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_update_asset'")
    def method_main_check(self, get_random_valid_asset_name):
        asset_name = get_random_valid_asset_name

        self.unlock_wallet()
        self.import_key('init4', 'init5')

        lcc.set_step("Check method update_asset")
        lcc.log_info("Create {} asset".format(asset_name))
        asset_options = self.echo_ops.get_asset_create_operation(
            echo=self.echo, issuer=self.init4, symbol=asset_name
        )[1]['common_options']
        self.send_wallet_request(
            "create_asset", [self.init4, asset_name, 10, asset_options, None, True], log_response=False
        )

        self.produce_block(self.__database_api_identifier)
        result = self.send_wallet_request("list_assets", [asset_name, 10], log_response=False)['result']
        new_asset_id = result[0]['id']
        new_amount = 2
        asset_options['core_exchange_rate']['base']['amount'] = new_amount
        asset_options['core_exchange_rate']['quote']['amount'] = new_amount
        asset_options['core_exchange_rate']['base']['asset_id'] = new_asset_id

        self.send_wallet_request("update_asset", [asset_name, self.init5, asset_options, True], log_response=False)
        self.produce_block(self.__database_api_identifier)

        result = self.send_wallet_request("list_assets", [asset_name, 10], log_response=False)['result']
        check_that("asset name", asset_name, equal_to(result[0]['symbol']))
        check_that(
            "new base amount", new_amount, equal_to(result[0]['options']['core_exchange_rate']['base']['amount'])
        )
        check_that(
            "new quote amount", new_amount, equal_to(result[0]['options']['core_exchange_rate']['quote']['amount'])
        )
