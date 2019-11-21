# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, has_item

from common.base_test import BaseTest

SUITE = {
    "description": "Operation 'asset_update_feed_producers'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "asset_management_operations", "asset_update_feed_producers")
@lcc.suite("Check work of method 'asset_update_feed_producers'", rank=1)
class AssetUpdateFeedProducers(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc1 = self.get_account_id(self.accounts[1], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'asset_update_feed_producers'")
    def method_main_check(self, get_random_valid_account_name, get_random_valid_asset_name):
        new_account = get_random_valid_account_name
        new_asset_name = get_random_valid_asset_name
        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Add balance to new account to perform 'asset_create_operation'")
        asset_create_operation = self.echo_ops.get_asset_create_operation(echo=self.echo, issuer=new_account,
                                                                          symbol=new_asset_name,
                                                                          feed_lifetime_sec=86400,
                                                                          minimum_feeds=1,
                                                                          short_backing_asset="1.3.0")
        self.utils.add_balance_for_operations(self, new_account, asset_create_operation,
                                              self.__database_api_identifier)
        lcc.log_info("Balance to account added")

        lcc.set_step("Perform 'asset_create_operation'")
        collected_operation = self.collect_operations(asset_create_operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        new_asset_id = str(broadcast_result["trx"]["operation_results"][0][1])
        lcc.log_info("New asset created, asset_id: '{}'")

        lcc.set_step("Add balance to new account to perform 'asset_update_feed_producers_operation'")
        new_feed_producers = [self.echo_acc0, self.echo_acc1]
        asset_update_feed_producers_operation = self.echo_ops.get_asset_update_feed_producers_operation(
            echo=self.echo, issuer=new_account, asset_to_update=new_asset_id,
            new_feed_producers=new_feed_producers)
        self.utils.add_balance_for_operations(self, new_account, asset_update_feed_producers_operation,
                                              self.__database_api_identifier)
        lcc.log_info("Balance to account added")

        lcc.set_step("Perform 'asset_update_feed_producers_operation'")
        collected_operation = self.collect_operations(asset_update_feed_producers_operation,
                                                      self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("'feed_producers' updated")

        lcc.set_step("Check that asset feed producers updated")
        response_id = self.send_request(self.get_request("get_assets", [[new_asset_id]]),
                                        self.__database_api_identifier)
        bitasset_data_id = self.get_response(response_id)["result"][0]["bitasset_data_id"]
        response_id = self.send_request(self.get_request("get_objects", [[bitasset_data_id]]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][0]
        for feed in result["feeds"]:
            check_that("new_feed_producers", new_feed_producers, has_item(feed[0]))
