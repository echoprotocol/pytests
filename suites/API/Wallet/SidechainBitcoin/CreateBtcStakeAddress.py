# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc

SUITE = {
    "description": "Method 'create_btc_stake_address'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_sidechain_bitcoin", "wallet_create_btc_stake_address")
@lcc.suite("Check work of method 'create_btc_stake_address'", rank=1)
class CreateBtcStakeAddress(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.init4 = None

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_create_btc_stake_address'")
    def method_main_check(self, get_random_btc_public_key):

        self.unlock_wallet()
        self.import_key('init4')
        result = self.send_wallet_request("get_btc_stake_address", [self.init4], log_response=False)['result']
        if result is None:
            btc_public_key = get_random_btc_public_key
            result = self.send_wallet_request(
                "create_btc_stake_address", [self.init4, btc_public_key, True], log_response=False
            )['result']

            result = self.send_wallet_request("get_btc_stake_address", [self.init4], log_response=False)['result']

            if self.type_validator.is_btc_address(result['address']):
                lcc.log_info("New btc_stake_address created!")
            else:
                lcc.log_info("Wrong btc_stake_address format")
        else:
            lcc.log_warning("Account already have stake address")
