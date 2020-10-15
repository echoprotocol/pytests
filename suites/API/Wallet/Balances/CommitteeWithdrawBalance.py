# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'committee_withdraw_balance'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_balances", "wallet_committee_withdraw_balance")
@lcc.suite("Check work of method 'committee_withdraw_balance'", rank=1)
class CommitteeWithdrawBalance(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

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

        self.init4 = self.get_account_id('init4', self.__database_api_identifier, self.__registration_api_identifier)
        lcc.log_info("Echo account are: #1='{}'".format(self.init4))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_committee_withdraw_balance'")
    def method_main_check(self):
        self.unlock_wallet()
        self.import_key('init4')

        lcc.set_step("Withdraw committee balance")
        current_frozen_balance_amount = self.send_wallet_request(
            "get_committee_frozen_balance", [self.init4], log_response=False
        )['result']['amount']
        if int(current_frozen_balance_amount) < 1010:
            lcc.log_info("Committee frozen balance less then required amount")
            self.send_wallet_request("committee_freeze_balance", [self.init4, 1010, True], log_response=False)
            lcc.log_info("Assets added to committee frozen balance")
            self.produce_block(self.__database_api_identifier)
            current_frozen_balance_amount = self.send_wallet_request(
                "get_committee_frozen_balance", [self.init4], log_response=False
            )['result']['amount']

        lcc.set_step("Check committee withdraw balance method")
        self.send_wallet_request("committee_withdraw_balance", [self.init4, 10, True], log_response=False)
        self.produce_block(self.__database_api_identifier)
        new_frozen_balance_amount = self.send_wallet_request(
            "get_committee_frozen_balance", [self.init4], log_response=False
        )['result']['amount']

        check_that(
            "committee frozen balance",
            int(current_frozen_balance_amount) - 10, equal_to(new_frozen_balance_amount)
        )
