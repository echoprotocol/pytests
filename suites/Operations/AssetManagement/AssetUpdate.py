# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Operation 'asset_update'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "asset_management_operations", "asset_update")
@lcc.suite("Check work of method 'asset_update'", rank=1)
class AssetUpdate(BaseTest):

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

    @lcc.test("Simple work of method 'asset_update'")
    def method_main_check(self, get_random_valid_asset_name):
        new_asset_name = get_random_valid_asset_name
        max_supply = "9999999999999"

        lcc.set_step("Create a new asset and get new asset_id")
        new_asset_id = self.utils.get_asset_id(self, new_asset_name, self.__database_api_identifier)
        lcc.log_info("New asset created, asset_id is '{}'".format(new_asset_id))

        lcc.set_step("Perform asset update operation")
        asset_update_operation = self.echo_ops.get_asset_update_operation(echo=self.echo, issuer=self.echo_acc0,
                                                                          new_issuer=self.echo_acc1,
                                                                          asset_to_update=new_asset_id,
                                                                          max_supply=max_supply,
                                                                          new_options=True)
        collected_operation = self.collect_operations(asset_update_operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("Asset updated successfully")

        lcc.set_step("Check updated asset")
        response_id = self.send_request(self.get_request("get_assets", [[new_asset_id]]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][0]
        response_issuer = result["issuer"]
        response_max_supply = result["options"]["max_supply"]
        check_that("'Updated new asset issuer'", response_issuer, equal_to(self.echo_acc1))
        check_that("'Updated new asset max_supply'", response_max_supply, equal_to(max_supply))
