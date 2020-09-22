# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'get_vesting_balances'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_balances", "wallet_get_vesting_balances")
@lcc.suite("Check work of method 'get_vesting_balances'", rank=1)
class GetVestingBalances(WalletBaseTest, BaseTest):

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_get_vesting_balances'")
    def method_main_check(self, get_random_integer):
        value_amount = get_random_integer

        lcc.set_step("Perform vesting balance create operation")
        broadcast_result = self.utils.perform_vesting_balance_create_operation(
            self, self.echo_acc0, self.echo_acc0, value_amount, self.__database_api_identifier
        )
        vesting_balance_id = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("Vesting balance object '{}' created".format(vesting_balance_id))
        lcc.set_step("Check get_vesting_balances method")
        get_vesting_balances_result = self.send_wallet_request(
            "get_vesting_balances", [self.echo_acc0], log_response=False
        )['result'][-1]
        check_that("vesting balance id", get_vesting_balances_result['id'], equal_to(vesting_balance_id))
        check_that("vesting balance amount", get_vesting_balances_result['balance']['amount'], equal_to(value_amount))
