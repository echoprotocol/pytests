# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'update_bitasset'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_assets", "wallet_update_bitasset")
@lcc.suite("Check work of method 'update_bitasset'", rank=1)
class UpdateBitasset(WalletBaseTest, BaseTest):

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
        self.feed_lifetime_sec = 82800

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_update_bitasset'")
    def method_main_check(self, get_random_valid_asset_name):
        asset_name = get_random_valid_asset_name

        self.unlock_wallet()
        self.import_key('init4')

        lcc.set_step("Create {} asset".format(asset_name))
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
        lcc.set_step("Update bitasset")
        result = self.send_wallet_request("list_assets", [asset_name, 1], log_response=False)['result']

        bitasset_options['feed_lifetime_sec'] = self.feed_lifetime_sec

        self.send_wallet_request("update_bitasset", [asset_name, bitasset_options, True], log_response=False)
        lcc.log_info("'feed_lifetime_sec' updated")

        self.produce_block(self.__database_api_identifier)
        lcc.set_step("Check method update_bitasset")
        result = self.send_wallet_request("list_assets", [asset_name, 1], log_response=False)['result']
        check_that("asset name", asset_name, equal_to(result[0]['symbol']))
        bitasset_id = result[0]['bitasset_data_id']
        bitasset_object = self.send_wallet_request("get_object", [bitasset_id], log_response=False)['result'][0]
        check_that(
            'feed_lifetime_sec', self.feed_lifetime_sec, equal_to(bitasset_object['options']['feed_lifetime_sec'])
        )
