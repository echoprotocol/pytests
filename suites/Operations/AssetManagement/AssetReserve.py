# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Operation 'asset_reserve'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "asset_management_operations", "asset_reserve")
@lcc.suite("Check work of method 'asset_reserve'", rank=1)
class AssetReserve(BaseTest):

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
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'asset_reserve'")
    def method_main_check(self, get_random_valid_account_name, get_random_valid_asset_name, get_random_integer_up_to_ten):
        new_account = get_random_valid_account_name
        new_asset_name = get_random_valid_asset_name
        value_amount = get_random_integer_up_to_ten

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Add balance to new account to perform create new asset operation")
        asset_create_operation = self.echo_ops.get_asset_create_operation(echo=self.echo, issuer=self.echo_acc0,
                                                                          symbol=new_asset_name)
        self.utils.add_balance_for_operations(self, new_account, asset_create_operation,
                                              self.__database_api_identifier)
        lcc.log_info("Balance to account added")

        lcc.set_step("Perform 'asset_create_operation'")
        collected_operation = self.collect_operations(asset_create_operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        new_asset_id = str(broadcast_result["trx"]["operation_results"][0][1])
        lcc.log_info("New asset created, asset_id: '{}'".format(new_asset_id))

        lcc.set_step("Perform 'asset_issue_operation'")
        asset_issue_operation = self.echo_ops.get_asset_issue_operation(echo=self.echo, issuer=self.echo_acc0,
                                                                        value_amount=value_amount,
                                                                        value_asset_id=new_asset_id,
                                                                        issue_to_account=new_account)
        collected_operation = self.collect_operations(asset_issue_operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("'asset_issue_operation' broadcasted successfully")

        lcc.set_step("Check that new account become new asset holder")
        response_id = self.send_request(self.get_request("get_account_balances", [new_account, [new_asset_id]]),
                                        self.__database_api_identifier)
        amount_in_new_asset = self.get_response(response_id)['result'][0]["amount"]
        check_that("value_amount in asset '{}'".format(new_asset_id), amount_in_new_asset, equal_to(value_amount))

        lcc.set_step("Perform 'asset_reserve_operation'")
        asset_reserve_operation = self.echo_ops.get_asset_reserve_operation(echo=self.echo, payer=new_account,
                                                                            reserve_amount=value_amount,
                                                                            reserve_asset_id=new_asset_id)
        collected_operation = self.collect_operations(asset_reserve_operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("'asset_reserve_operation' broadcasted successfully")

        lcc.set_step("Check asset reserved")
        response_id = self.send_request(self.get_request("get_account_balances", [new_account, [new_asset_id]]),
                                        self.__database_api_identifier)
        amount_in_new_asset = self.get_response(response_id)['result'][0]["amount"]
        check_that("value_amount in asset '{}'".format(new_asset_id), amount_in_new_asset, equal_to(0))
