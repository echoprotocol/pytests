# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import INIT5_PK, WALLET_PASSWORD

import lemoncheesecake.api as lcc

SUITE = {
    "description": "Method 'withdraw_vesting'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_balances", "wallet_withdraw_vesting")
@lcc.suite("Check work of method 'withdraw_vesting'", rank=1)
class WithdrawVesting(WalletBaseTest, BaseTest):

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

    @lcc.test("Simple work of method 'wallet_withdraw_vesting'")
    @lcc.disabled()
    # TODO: fix after ECHO-2405
    def method_main_check(self, get_random_integer):
        value_amount = get_random_integer
        lcc.set_step("Perform vesting balance create operation")
        broadcast_result = self.utils.perform_vesting_balance_create_operation(
            self, self.echo_acc0, self.init5, value_amount, self.__database_api_identifier
        )
        vesting_balance_id = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("Vesting balance object '{}' created".format(vesting_balance_id))

        lcc.set_step("Unlock wallet")
        response = self.send_wallet_request("is_new", [], log_response=False)
        if response['result']:
            self.send_wallet_request("set_password", [WALLET_PASSWORD], log_response=False)
        response = self.send_wallet_request("is_locked", [], log_response=False)
        if response['result']:
            self.send_wallet_request("unlock", [WALLET_PASSWORD], log_response=False)
        lcc.log_info("Wallet unlocked")

        lcc.set_step("Import key")
        self.send_wallet_request("import_key", ['init5', INIT5_PK], log_response=False)
        lcc.log_info("Key imported")

        lcc.set_step("Check get_vesting_balances method")
        get_vesting_balances_result = self.send_wallet_request("get_vesting_balances", [self.init5], log_response=False)
        lcc.log_info("{}".format(get_vesting_balances_result))

        get_vesting_balances_result = self.send_wallet_request(
            "withdraw_vesting", [vesting_balance_id, value_amount, self.echo_asset, True], log_response=False
        )
        self.produce_block(self.__database_api_identifier)
        lcc.log_info("{}".format(get_vesting_balances_result))
        get_vesting_balances_result = self.send_wallet_request("get_vesting_balances", [self.init5], log_response=False)
        lcc.log_info("{}".format(get_vesting_balances_result))