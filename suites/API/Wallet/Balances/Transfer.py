# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import INIT5_PK

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'transfer'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_balances", "wallet_transfer")
@lcc.suite("Check work of method 'transfer'", rank=1)
class Transfer(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
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
        lcc.log_info("Echo account are: #1='{}'".format(self.echo_acc0))

        self.init5 = self.get_account_id('init5', self.__database_api_identifier, self.__registration_api_identifier)
        lcc.log_info("Echo account are: #1='{}'".format(self.init5))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_transfer'")
    def method_main_check(self, get_random_integer):
        value_amount = get_random_integer
        lcc.set_step("Perform vesting balance create operation")
        broadcast_result = self.utils.perform_vesting_balance_create_operation(
            self, self.echo_acc0, self.init5, value_amount, self.__database_api_identifier
        )
        vesting_balance_id = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("Vesting balance object '{}' created".format(vesting_balance_id))

        self.unlock_wallet()

        lcc.set_step("Import key")
        self.send_wallet_request("import_key", ['init5', INIT5_PK], log_response=False)
        lcc.log_info("Key imported")

        lcc.set_step("Check transfer method")
        lcc.log_info("Get current account balance")
        init5_balance = self.send_wallet_request(
            "list_id_balances", [self.init5], log_response=False
        )['result'][0]['amount']
        echo_acc0_balance = self.send_wallet_request(
            "list_id_balances", [self.echo_acc0], log_response=False
        )['result'][0]['amount']
        lcc.log_info(
            "Account balances before transfer init5: {}, echo_acc0: {}".format(init5_balance, echo_acc0_balance)
        )
        lcc.log_info("Transfre 10 assets from init5 to echo_acc0")
        self.send_wallet_request(
            "transfer", [self.init5, self.echo_acc0, 10, self.echo_asset, True], log_response=False
        )
        self.produce_block(self.__database_api_identifier)
        lcc.log_info("Assets transfered.")
        init5_balance_after_transfer = self.send_wallet_request(
            "list_id_balances", [self.init5], log_response=False
        )['result'][0]['amount']
        echo_acc0_balance_after_transfer = self.send_wallet_request(
            "list_id_balances", [self.echo_acc0], log_response=False
        )['result'][0]['amount']
        check_that("init5 balance", int(init5_balance_after_transfer), equal_to(int(init5_balance) - 10 * 10 ** 8 - 20))
        check_that(
            "echo_acc0 balance", int(echo_acc0_balance_after_transfer), equal_to(int(echo_acc0_balance) + 10 * 10 ** 8)
        )
