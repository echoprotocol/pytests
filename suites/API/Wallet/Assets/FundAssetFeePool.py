# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import INIT4_PK, INIT5_PK, WALLET_PASSWORD

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'fund_asset_fee_pool'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_assets", "wallet_fund_asset_fee_pool")
@lcc.suite("Check work of method 'fund_asset_fee_pool'", rank=1)
class FundAssetFeePool(WalletBaseTest, BaseTest):

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

    @lcc.test("Simple work of method 'wallet_fund_asset_fee_pool'")
    def method_main_check(self, get_random_valid_asset_name, get_random_integer_up_to_ten):
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

        lcc.set_step("Check method fund_asset_fee_pool")
        self.init4 = self.get_account_id('init4', self.__database_api_identifier, self.__registration_api_identifier)
        self.init5 = self.get_account_id('init5', self.__database_api_identifier, self.__registration_api_identifier)
        asset_name = get_random_valid_asset_name
        fee_pool_amount = get_random_integer_up_to_ten

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

        lcc.log_info("Get bitasset fee pool")
        dynamic_asset_data_id = self.send_wallet_request(
            "list_assets", [asset_name, 1], log_response=False
        )['result'][0]['dynamic_asset_data_id']
        bitasset_fee_pool = self.send_wallet_request(
            "get_object", [dynamic_asset_data_id], log_response=False
        )['result'][0]['fee_pool']
        self.send_wallet_request(
            "fund_asset_fee_pool", [self.init4, asset_name, fee_pool_amount, True], log_response=False
        )['result']
        self.produce_block(self.__database_api_identifier)
        bitasset_new_fee_pool = self.send_wallet_request(
            "get_object", [dynamic_asset_data_id], log_response=False
        )['result']
        check_that(
            "bitasset_fee_pool",
            bitasset_new_fee_pool[0]['fee_pool'],
            equal_to(bitasset_fee_pool + fee_pool_amount * 10 ** 8),
            quiet=True
        )
