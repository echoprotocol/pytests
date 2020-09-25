# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import INIT4_PK, WALLET_PASSWORD

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

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

        lcc.set_step("Check method publish_asset_feed")
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
        core_exchange_rate = asset_create_operation['common_options']['core_exchange_rate']
        self.send_wallet_request(
            "create_asset", [self.init4, asset_name, 10, asset_options, bitasset_options, True], log_response=False
        )
        self.produce_block(self.__database_api_identifier)
        result = self.send_wallet_request("list_assets", [asset_name, 10], log_response=False)['result']

        new_asset_id = result[0]['id']

        lcc.set_step("Perform 'asset_update_feed_producers_operation'")

        new_feed_producers = [self.init4, self.init5]
        asset_update_feed_producers_operation = self.echo_ops.get_asset_update_feed_producers_operation(
            echo=self.echo, issuer=self.init4, asset_to_update=new_asset_id, new_feed_producers=new_feed_producers, signer=INIT4_PK
        )

        collected_operation = self.collect_operations(
            asset_update_feed_producers_operation, self.__database_api_identifier
        )
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("'feed_producers' updated")
        lcc.log_info("{}".format(broadcast_result))

        core_exchange_rate['base']['asset_id'] = new_asset_id
        core_exchange_rate['base']['amount'] = 5
        core_exchange_rate['quote']['asset_id'] = self.echo_asset
        core_exchange_rate['quote']['amount'] = 1
        lcc.log_info("{}".format(core_exchange_rate))
        asset_feed_producers = self.send_wallet_request(
            "publish_asset_feed",
            [self.init4, asset_name, core_exchange_rate, True],
            log_response=False)
        lcc.log_info("{}".format(asset_feed_producers))
        self.produce_block(self.__database_api_identifier)
        bitasset_data_id = self.send_wallet_request("get_object", [new_asset_id], log_response=False)['result'][0]["bitasset_data_id"]
        bitasset_core_exchange_rate = self.send_wallet_request("get_object", [bitasset_data_id], log_response=False)['result'][0]['core_exchange_rate']
        check_that('core_exchange_rate', core_exchange_rate, equal_to(bitasset_core_exchange_rate))
