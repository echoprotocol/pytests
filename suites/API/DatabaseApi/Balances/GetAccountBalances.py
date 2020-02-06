# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_account_balances'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_balances", "get_account_balances")
@lcc.suite("Check work of method 'get_account_balances'", rank=1)
class GetAccountBalances(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))

    @lcc.test("Simple work of method 'get_account_balances'")
    def method_main_check(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name
        assets_ids = [self.echo_asset, self.eth_asset]

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get balances of new account")
        params = [new_account, assets_ids]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_account_balances'")

        lcc.set_step("Check that new account has empty balances")
        for i, result in enumerate(results):
            check_that_in(
                result,
                "amount", equal_to(0),
                "asset_id", equal_to(assets_ids[i])
            )


@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_balances", "get_account_balances")
@lcc.suite("Positive testing of method 'get_account_balances'", rank=2)
class PositiveTesting(BaseTest):

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

    @lcc.test("Transfer assets to new account and get updated account balance")
    @lcc.depends_on("API.DatabaseApi.Balances.GetAccountBalances.GetAccountBalances.method_main_check")
    def transfer_assets_and_get_updated_account_balance(self, get_random_valid_account_name,
                                                        get_random_integer_up_to_fifty):
        new_account = get_random_valid_account_name
        transfer_amount = get_random_integer_up_to_fifty

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get balances of new account")
        params = [new_account, [self.echo_asset]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_account_balances' in '{}' assets".format(self.echo_asset))

        lcc.set_step("Perform transfer operation to add assets to new account")
        self.utils.perform_transfer_operations(self, self.echo_acc0, new_account, self.__database_api_identifier,
                                               transfer_amount=transfer_amount)
        lcc.log_info("Amount '{}' in '{}' assets added to new account '{}'".format(transfer_amount, self.echo_asset,
                                                                                   new_account))

        lcc.set_step("Get updated balances of new account")
        params = [new_account, [self.echo_asset]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        updated_response = self.get_response(response_id)
        lcc.log_info("Call method 'get_account_balances' in '{}' assets".format(self.echo_asset))

        lcc.set_step("Check that account balance increased by transfer amount")
        check_that_in(
            updated_response["result"][0],
            "amount", equal_to(response["result"][0]["amount"] + transfer_amount),
            "asset_id", equal_to(self.echo_asset)
        )

    @lcc.test("Try to get account balance in nonexistent assets")
    @lcc.depends_on("API.DatabaseApi.Balances.GetAccountBalances.GetAccountBalances.method_main_check")
    def get_account_balance_in_nonexistent_asset(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get nonexistent asset id")
        nonexistent_asset_id = self.utils.get_nonexistent_asset_id(self, self.__database_api_identifier)
        lcc.log_info("Nonexistent asset id is '{}'".format(nonexistent_asset_id))

        lcc.set_step("Get balances of new account in nonexistent asset id")
        params = [new_account, [nonexistent_asset_id]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_account_balances' in '{}' assets".format(nonexistent_asset_id))

        lcc.set_step("Check that new account has empty balance in nonexistent assets")
        check_that_in(
            response["result"][0],
            "amount", equal_to(0),
            "asset_id", equal_to(nonexistent_asset_id)
        )
