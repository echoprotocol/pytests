# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_, is_not_none, require_that

SUITE = {
    "description": "Perform 'update_asset_operation'"
}


@lcc.prop("main", "type")
@lcc.tags("scenarios", "update_asset")
@lcc.suite("Check scenario 'Update asset'")
class UpdateAsset(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__history_api_identifier = None
        self.echo_acc0 = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__history_api_identifier = self.get_identifier("history")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', "
            "history='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier, self.__history_api_identifier
            )
        )
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    @lcc.test("Perform update new asset")
    def update_asset(self, get_random_valid_account_name, get_random_valid_asset_name):
        new_account = get_random_valid_account_name
        new_asset_name = get_random_valid_asset_name

        lcc.set_step("Create and get new account. Add balance to pay for asset_create_operation fee")
        new_account = self.get_account_id(
            new_account, self.__database_api_identifier, self.__registration_api_identifier
        )
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
        lcc.log_info("New asset created, new_asset_id='{}'".format(new_asset_id))

        lcc.set_step("Get new asset info")
        param = [new_asset_id]
        response_id = self.send_request(self.get_request("get_assets", [param]), self.__database_api_identifier)
        result = self.get_response(response_id)["result"][0]
        require_that("'New asset result'", result, is_not_none(), quiet=True)

        lcc.set_step("Perform new asset update operation without 'new_options'")
        asset_update_operation = self.echo_ops.get_asset_update_operation(
            echo=self.echo,
            issuer=new_account,
            new_issuer=self.echo_acc0,
            asset_to_update=new_asset_id,
            new_options=False
        )
        self.utils.add_balance_for_operations(self, new_account, asset_create_operation, self.__database_api_identifier)
        collected_operation = self.collect_operations(asset_update_operation, self.__database_api_identifier)
        broadcast_result = \
            self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        broadcast_issuer = broadcast_result["trx"]["operations"][0][1]["new_issuer"]
        lcc.log_info("New asset issuer was updated to {}".format(broadcast_issuer))

        lcc.set_step("Get new asset info")
        param = [new_asset_id]
        response_id = self.send_request(self.get_request("get_assets", [param]), self.__database_api_identifier)
        response_issuer = self.get_response(response_id)["result"][0]["issuer"]
        check_that("'Updated new asset issuer'", response_issuer, is_(broadcast_issuer))

        lcc.set_step("Perform new asset update operation without 'new_issuer'")
        asset_update_operation = self.echo_ops.get_asset_update_operation(
            echo=self.echo,
            issuer=self.echo_acc0,
            asset_to_update=new_asset_id,
            max_supply="9999999999999",
            new_options=True
        )
        self.utils.add_balance_for_operations(self, new_account, asset_create_operation, self.__database_api_identifier)
        collected_operation = self.collect_operations(asset_update_operation, self.__database_api_identifier)
        broadcast_result = \
            self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        broadcast_max_supply = broadcast_result["trx"]["operations"][0][1]["new_options"]["max_supply"]
        lcc.log_info("New asset max_supply was updated to {}".format(broadcast_max_supply))

        lcc.set_step("Get new asset info")
        param = [new_asset_id]
        response_id = self.send_request(self.get_request("get_assets", [param]), self.__database_api_identifier)
        response_max_supply = self.get_response(response_id)["result"][0]["options"]["max_supply"]
        check_that("'Updated new asset max_supply'", response_max_supply, is_(broadcast_max_supply))
