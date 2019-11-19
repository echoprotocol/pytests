# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, not_equal_to, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Operation 'override_transfer'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "asset_transfer_operations", "override_transfer")
@lcc.suite("Check work of method 'override_transfer'", rank=1)
class OverrideTransfer(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__asset_api_identifier = None
        self.echo_acc0 = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__asset_api_identifier = self.get_identifier("asset")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', asset='{}'".format(self.__database_api_identifier,
                                                                                       self.__registration_api_identifier,
                                                                                       self.__asset_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'override_transfer'")
    def method_main_check(self, get_random_valid_asset_name, get_random_integer, get_random_valid_account_name):
        new_asset_amount = get_random_integer
        new_asset = get_random_valid_asset_name
        new_account = get_random_valid_account_name
        _start = 0
        _limit = 10

        lcc.set_step("Create asset and get new asset id")
        operation = self.echo_ops.get_asset_create_operation(echo=self.echo, issuer=self.echo_acc0,
                                                             symbol=new_asset, flags=4)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        new_asset = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("New asset created, asset_id is '{}'".format(new_asset))

        lcc.set_step("Create new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Add created assets to account")
        self.utils.add_assets_to_account(self, new_asset_amount, new_asset, new_account,
                                         self.__database_api_identifier)
        lcc.log_info("Created '{}' asset added to '{}' account successfully".format(new_asset, new_account))

        lcc.set_step("Check that new account is asset holder".format(new_account))
        response_id = self.send_request(self.get_request("get_asset_holders", [new_asset, _start, _limit]),
                                        self.__asset_api_identifier)
        current_asset_holder = self.get_response(response_id)["result"][0]["account_id"]
        check_that("current asset holder", current_asset_holder, equal_to(new_account))

        lcc.set_step("Perform override_transfer operation")
        transfer_operation = self.echo_ops.get_override_transfer_operation(echo=self.echo, issuer=self.echo_acc0,
                                                                           from_account_id=new_account,
                                                                           amount=new_asset_amount,
                                                                           amount_asset_id=new_asset,
                                                                           to_account_id=self.echo_acc0)
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        lcc.log_info("'override_transfer' operation broadcasted successfully")
        lcc.set_step("Check new asset holder")
        response_id = self.send_request(self.get_request("get_asset_holders", [new_asset, _start, _limit]),
                                        self.__asset_api_identifier)
        asset_holder_after_override = self.get_response(response_id)["result"][0]["account_id"]
        check_that("asset holder", asset_holder_after_override, equal_to(self.echo_acc0))
        check_that("asset holder", asset_holder_after_override, not_equal_to(current_asset_holder))
