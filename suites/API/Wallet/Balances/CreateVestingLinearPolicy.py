# -*- coding: utf-8 -*-
import time

from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'create_vesting_linear_policy'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_balances", "wallet_create_vesting_linear_policy")
@lcc.suite("Check work of method 'create_vesting_linear_policy'", rank=1)
class CreateVestingLinearPolicy(WalletBaseTest, BaseTest):

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
        self.init5 = self.get_account_id('init5', self.__database_api_identifier, self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.init5))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_create_vesting_linear_policy'")
    def method_main_check(self):
        self.unlock_wallet()
        self.import_key('init5')
        begin_timestamp = self.get_expiration_time(5)
        lcc.set_step("Create vesting linear policy")
        get_vesting_balances_result = self.send_wallet_request(
            "create_vesting_linear_policy", [self.init5, self.init5, 1, self.echo_asset, begin_timestamp, 10, 20, True],
            log_response=False
        )
        lcc.log_info("asdasd {}".format(get_vesting_balances_result))
        lcc.log_info("Vesting linear policy created")
        lcc.set_step("Check vesting linear policy")
        get_vesting_balances_result = self.send_wallet_request(
            "get_vesting_balances", [self.init5], log_response=False
        )['result'][-1]
        check_that("amount", get_vesting_balances_result['allowed_withdraw']['amount'], equal_to(0))
        time.sleep(5)
        self.produce_block(self.__database_api_identifier)
        get_vesting_balances_result = self.send_wallet_request(
            "get_vesting_balances", [self.init5], log_response=False
        )['result'][-1]
        check_that("amount", get_vesting_balances_result['allowed_withdraw']['amount'], equal_to(0))
        time.sleep(20)
        self.produce_block(self.__database_api_identifier)
        get_vesting_balances_result = self.send_wallet_request(
            "get_vesting_balances", [self.init5], log_response=False
        )['result'][-1]
        check_that("amount", get_vesting_balances_result['allowed_withdraw']['amount'], equal_to(100000000))
