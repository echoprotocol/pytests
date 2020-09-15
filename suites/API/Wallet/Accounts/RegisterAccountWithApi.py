# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import WALLET_PASSWORD

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'register_account_with_api'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_accounts", "wallet_register_account_with_api")
@lcc.suite("Check work of method 'register_account_with_api'", rank=1)
class GetRegisterAccountWithApi(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_register_account_with_api'")
    def method_main_check(self, get_random_valid_account_name, get_random_eth_address):
        new_account = get_random_valid_account_name
        evm_address = get_random_eth_address
        public_key = self.store_new_account(new_account)

        lcc.set_step("Unlock wallet to register account")
        response = self.send_wallet_request("is_new", [], log_response=False)
        if response['result']:
            self.send_wallet_request("set_password", [WALLET_PASSWORD], log_response=False)
        response = self.send_wallet_request("is_locked", [], log_response=False)
        if response['result']:
            self.send_wallet_request("unlock", [WALLET_PASSWORD], log_response=False)
        lcc.log_info("Wallet unlocked")
        lcc.set_step("Check that new account registrated")
        response = self.send_wallet_request(
            "register_account_with_api", [new_account, public_key, public_key, evm_address], log_response=False
        )
        check_that("result", response['result'], equal_to(None), quiet=True)
