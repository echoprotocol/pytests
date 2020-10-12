# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc

SUITE = {
    "description": "Method 'get_btc_deposit_script'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_sidechain_bitcoin", "wallet_get_btc_deposit_script")
@lcc.suite("Check work of method 'get_btc_deposit_script'", rank=1)
class GetBtcDepositScript(WalletBaseTest, BaseTest):

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

    @lcc.depends_on("API.Wallet.SidechainBitcoin.CreateBtcAddress.CreateBtcAddress.method_main_check")
    @lcc.test("Simple work of method 'wallet_get_btc_deposit_script'")
    def method_main_check(self):
        btc_address = self.send_wallet_request("get_btc_address", [self.init4], log_response=False)['result']
        if btc_address is None:
            lcc.log_error("Account {} has no btc address, method does not checked".format(self.init4))
        else:
            result = self.send_wallet_request(
                "get_btc_deposit_script", [btc_address['id']], log_response=False
            )['result']
            if self.type_validator.is_hex(result):
                lcc.log_info("Btc_deposit_script has correct format hex.")
            else:
                lcc.log_error("Wrong format of btc_deposit_script!")
