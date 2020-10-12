# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import INIT4_PK, INIT5_PK

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'update_asset_feed_producers'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_assets", "wallet_update_asset_feed_producers")
@lcc.suite("Check work of method 'update_asset_feed_producers'", rank=1)
class UpdateAssetFeedProducers(WalletBaseTest, BaseTest):

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

    @lcc.test("Simple work of method 'wallet_update_asset_feed_producers'")
    def method_main_check(self, get_random_valid_asset_name):
        self.unlock_wallet()

        lcc.set_step("Import key")
        self.send_wallet_request("import_key", ['init4', INIT4_PK], log_response=False)
        self.send_wallet_request("import_key", ['init5', INIT5_PK], log_response=False)
        lcc.log_info("Key imported")

        lcc.set_step("Check method update_asset_feed_producers")
        self.init4 = self.get_account_id('init4', self.__database_api_identifier, self.__registration_api_identifier)
        self.init5 = self.get_account_id('init5', self.__database_api_identifier, self.__registration_api_identifier)
        asset_name = get_random_valid_asset_name
        lcc.log_info("Create {} asset".format(asset_name))
        asset_create_operation = self.echo_ops.get_asset_create_operation(
            echo=self.echo,
            issuer=self.init4,
            symbol=asset_name,
            feed_lifetime_sec=86400,
            minimum_feeds=1,
            short_backing_asset=self.echo_asset
        )[1]

        asset_options = asset_create_operation['common_options']
        bitasset_options = asset_create_operation['bitasset_opts']
        self.send_wallet_request(
            "create_asset", [self.init4, asset_name, 10, asset_options, bitasset_options, True], log_response=False
        )
        self.produce_block(self.__database_api_identifier)

        asset_feed_producers = self.send_wallet_request(
            "update_asset_feed_producers", [asset_name, [self.init4, self.init5], True], log_response=False
        )['result']['operations'][0][1]["new_feed_producers"]
        self.produce_block(self.__database_api_identifier)

        check_that("asset name", asset_feed_producers, equal_to([self.init4, self.init5]))
