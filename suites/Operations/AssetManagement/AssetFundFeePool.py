# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Operation 'asset_fund_fee_pool'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "asset_management_operations", "asset_fund_fee_pool")
@lcc.suite("Check work of method 'asset_fund_fee_pool'", rank=1)
class AssetFundFeePool(BaseTest):

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

    @lcc.test("Simple work of method 'asset_fund_fee_pool'")
    def method_main_check(self, get_random_valid_account_name, get_random_valid_asset_name, get_random_integer_up_to_ten):
        new_asset_name = get_random_valid_asset_name
        value_amount = get_random_integer_up_to_ten

        lcc.set_step("Create a new asset and get new asset_id")
        new_asset_id = self.utils.get_asset_id(self, new_asset_name, self.__database_api_identifier)
        lcc.log_info("New asset created, asset_id: '{}'".format(new_asset_id))
        lcc.set_step("Get current asset fee pool")
        response_id = self.send_request(self.get_request("get_objects", [[new_asset_id]]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][0]["dynamic_asset_data_id"]
        response_id = self.send_request(self.get_request("get_objects", [[result]]),
                                        self.__database_api_identifier)
        fee_pool = self.get_response(response_id)["result"][0]["fee_pool"]
        lcc.log_info("Asset fee pool: '{}'".format(fee_pool))
        lcc.set_step("Perform 'asset_fund_fee_pool_operation'")
        asset_fund_fee_pool_operation = self.echo_ops.get_asset_fund_fee_pool_operation(
            self.echo, from_account=self.echo_acc0, asset_id=new_asset_id, amount=value_amount)
        collected_operation = self.collect_operations(asset_fund_fee_pool_operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                log_broadcast=False)
        lcc.log_info("'asset_fund_fee_pool_operation' broadcasted successfully")
        lcc.set_step("Check that assets added to fee pool")
        response_id = self.send_request(self.get_request("get_objects", [[new_asset_id]]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][0]["dynamic_asset_data_id"]
        response_id = self.send_request(self.get_request("get_objects", [[result]]),
                                        self.__database_api_identifier)
        current_fee_pool = self.get_response(response_id)["result"][0]["fee_pool"]
        check_that("fee_pool", fee_pool + value_amount, equal_to(current_fee_pool))
