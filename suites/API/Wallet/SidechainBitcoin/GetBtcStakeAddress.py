# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'get_btc_stake_address'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_sidechain_bitcoin", "wallet_get_btc_stake_address")
@lcc.suite("Check work of method 'get_btc_stake_address'", rank=1)
class GetBtcStakeAddress(WalletBaseTest, BaseTest):

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

    @lcc.test("Simple work of method 'wallet_get_btc_stake_address'")
    @lcc.depends_on("API.Wallet.SidechainBitcoin.CreateBtcStakeAddress.CreateBtcStakeAddress.method_main_check")
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

        if self.type_validator.is_btc_stake_address_id(result['id']):
            lcc.log_info("Correct format of `btc_stake_address_id`, got: {}".format(result['id']))
        else:
            lcc.log_info("Wrong format of `btc_stake_address_id`, got: {}".format(result['id']))
        check_that("account", result['account'], equal_to(self.init4))
        if self.type_validator.is_btc_address(result['address']):
            lcc.log_info("New btc_address created!")
        else:
            lcc.log_info("Wrong btc_address format")
        if self.type_validator.is_hex(result['stake_script']):
            lcc.log_info("correct format of stake script, got: {}".format(result['stake_script']))
        else:
            lcc.log_info("Wrong format of stake script, got: {}".format(result['stake_script']))
