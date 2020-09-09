# -*- coding: utf-8 -*-

from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Operation 'asset_create'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "asset_management_operations", "asset_create")
@lcc.suite("Check work of method 'asset_create'", rank=1)
class AssetCreate(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

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
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo accounts are: #1='{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'asset_create'")
    def method_main_check(self, get_random_valid_account_name, get_random_valid_asset_name):
        new_account = get_random_valid_account_name
        new_asset_name = get_random_valid_asset_name

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(
            new_account, self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))
        lcc.set_step("Add balance to new account to perform create new asset operation")
        asset_create_operation = self.echo_ops.get_asset_create_operation(
            echo=self.echo, issuer=new_account, symbol=new_asset_name
        )
        self.utils.add_balance_for_operations(self, new_account, asset_create_operation, self.__database_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}, balance added".format(new_account))

        lcc.set_step("Perform asset create operation using a new account")
        collected_operation = self.collect_operations(asset_create_operation, self.__database_api_identifier)
        broadcast_result = \
            self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        new_asset_id = str(broadcast_result["trx"]["operation_results"][0][1])
        lcc.log_info("New asset created, asset_id: '{}'".format(new_asset_id))

        lcc.set_step("Check new asset")
        response_id = self.send_request(
            self.get_request("get_assets", [[new_asset_id]]), self.__database_api_identifier
        )
        symbol = self.get_response(response_id)["result"][0]["symbol"]
        check_that("asset symbol", symbol, equal_to(new_asset_name))
