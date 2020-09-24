# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import INIT4_PK, INIT5_PK, WALLET_PASSWORD

import lemoncheesecake.api as lcc

SUITE = {
    "description": "Method 'publish_asset_feed'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_assets", "wallet_publish_asset_feed")
@lcc.suite("Check work of method 'publish_asset_feed'", rank=1)
class PublishAssetFeed(WalletBaseTest, BaseTest):

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
        self.feed_lifetime_sec = 82800

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.disabled()
    @lcc.test("Simple work of method 'wallet_publish_asset_feed'")
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

        lcc.set_step("Check method publish_asset_feed")
        self.init4 = self.get_account_id('init4', self.__database_api_identifier, self.__registration_api_identifier)
        self.init5 = self.get_account_id('init5', self.__database_api_identifier, self.__registration_api_identifier)
        asset_name = get_random_valid_asset_name
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
        core_exchange_rate = asset_create_operation['common_options']['core_exchange_rate']
        self.send_wallet_request(
            "create_asset", [self.init4, asset_name, 10, asset_options, bitasset_options, True], log_response=False
        )
        self.produce_block(self.__database_api_identifier)
        result = self.send_wallet_request("list_assets", [asset_name, 10], log_response=False)['result']

        new_asset_id = result[0]['id']

        core_exchange_rate['base']['asset_id'] = new_asset_id
        # asset_feed_producers = self.send_wallet_request(
        #     "publish_asset_feed",
        #     [self.init4, asset_name, core_exchange_rate, True],
        #     log_response=False)
        self.produce_block(self.__database_api_identifier)
