# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc

SUITE = {
    "description": "Method 'get_committee_frozen_balance'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_balances", "wallet_get_committee_frozen_balance")
@lcc.suite("Check work of method 'get_committee_frozen_balance'", rank=1)
class GetCommitteeFrozenBalance(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info(
            "Database API identifiers are: '{}'".format(
                self.__database_api_identifier
            )
        )
        self.committee_members_info = self.get_active_committee_members_info(self.__database_api_identifier)
        self.init0 = self.committee_members_info[0]["account_id"]

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_get_committee_frozen_balance'")
    def method_main_check(self):
        result = self.send_wallet_request("get_committee_frozen_balance", [self.init0], log_response=False)['result']
        if self.type_validator.is_digit(result['amount']):
            lcc.log_info("Correct format of balance amount")
        else:
            lcc.log_error("Wrong balance format!")
        if self.type_validator.is_asset_id(result['asset_id']):
            lcc.log_info("Correct format of asset_id")
        else:
            lcc.log_error("Wrong asset_id format!")
