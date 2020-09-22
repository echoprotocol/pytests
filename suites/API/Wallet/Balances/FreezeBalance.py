# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import INIT5_PK, WALLET_PASSWORD

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'freeze_balance'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_balances", "wallet_freeze_balance")
@lcc.suite("Check work of method 'freeze_balance'", rank=1)
class FreezeBalance(WalletBaseTest, BaseTest):

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_freeze_balance'")
    def method_main_check(self, get_random_integer):
        value_amount = get_random_integer
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

        lcc.set_step("Check freeze balance method")
        self.init5 = self.get_account_id('init5', self.__database_api_identifier, self.__registration_api_identifier)
        self.send_wallet_request(
            "freeze_balance", [self.init5, value_amount, self.echo_asset, 90, True], log_response=False
        )
        self.produce_block(self.__database_api_identifier)
        result = self.send_wallet_request("list_frozen_balances", [self.init5], log_response=False)["result"][-1]
        check_that("frozen_balance", int(result['balance']['amount']), equal_to(value_amount * 10 ** 8))
        if self.type_validator.is_frozen_balance_id(result['id']):
            lcc.log_info("Correct format of frozen_balance_id")
        else:
            lcc.log_error("Wrong frozen_balance_id format!")
