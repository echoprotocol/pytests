# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Operation 'vesting_balance_withdraw'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("operations", "vesting_balances_operations", "vesting_balance_withdraw")
@lcc.suite("Check work of method 'vesting_balance_withdraw'", rank=1)
class VestingBalanceCreate(BaseTest):

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
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'vesting_balance_withdraw'")
    def method_main_check(self, get_random_valid_asset_name, get_random_integer, get_random_valid_account_name):
        new_asset_amount = get_random_integer
        new_asset = get_random_valid_asset_name
        new_account = get_random_valid_account_name

        lcc.set_step("Create asset and get new asset id")
        new_asset = self.utils.get_asset_id(self, new_asset, self.__database_api_identifier)
        lcc.log_info("New asset created, asset_id is '{}'".format(new_asset))

        lcc.set_step("Add created assets to account")
        self.utils.add_assets_to_account(self, new_asset_amount, new_asset, self.echo_acc0,
                                         self.__database_api_identifier)
        lcc.log_info("Created '{}' assets added to '{}' account successfully".format(new_asset, self.echo_acc0))

        lcc.set_step("Create new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Perform 'vesting_balance_create' operation")
        operation = self.echo_ops.get_vesting_balance_create_operation(echo=self.echo, creator=self.echo_acc0,
                                                                       owner=new_account, amount=new_asset_amount,
                                                                       amount_asset_id=new_asset)

        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("'vesting_balance' created successfully")

        lcc.set_step("Add vesting balance to new account and get vesting balance id")
        response_id = self.send_request(self.get_request("get_vesting_balances", [new_account]),
                                        self.__database_api_identifier)
        vesting_balances_amount = self.get_response(response_id)["result"][0]["balance"]["amount"]
        check_that("vesting_balances_amount", vesting_balances_amount, equal_to(new_asset_amount))

        vesting_balance_id = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("vesting balance id: {}".format(vesting_balance_id))

        lcc.set_step("Perform 'vesting_balance_withdraw' operation")
        operation = self.echo_ops.get_vesting_balance_withdraw_operation(echo=self.echo,
                                                                         vesting_balance=vesting_balance_id,
                                                                         owner=new_account, amount=new_asset_amount,
                                                                         amount_asset_id=new_asset)
        lcc.log_info("Add balance to pay fee for 'vesting_balance_withdraw' operation")
        self.utils.add_balance_for_operations(self, new_account, operation, self.__database_api_identifier,
                                              log_broadcast=False)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("'vesting_balance_withdraw' broadcasted successfully")

        lcc.set_step("Check that 'vesting_balance' equal to 0 after withdrawn")
        response_id = self.send_request(self.get_request("get_vesting_balances", [new_account]),
                                        self.__database_api_identifier)
        vesting_balances_amount = self.get_response(response_id)["result"][0]["balance"]["amount"]
        check_that("vesting_balances_amount", vesting_balances_amount, equal_to(0))
