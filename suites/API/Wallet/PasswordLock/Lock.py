# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import WALLET_PASSWORD

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'lock'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_password_lock", "wallet_lock")
@lcc.suite("Check work of method 'lock'", rank=1)
class Lock(WalletBaseTest, BaseTest):

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

    @lcc.test("Simple work of method 'wallet_lock'")
    def method_main_check(self):
        lcc.set_step("Check lock wallet method")
        is_new = self.send_wallet_request("is_new", [], log_response=False)['result']
        if is_new:
            lcc.log_info("Set a new wallet password")
            self.send_wallet_request("set_password", [WALLET_PASSWORD], log_response=False)['result']

        is_locked = self.send_wallet_request("is_locked", [], log_response=False)['result']
        if not is_locked:
            lcc.log_info("Lock wallet")
            self.send_wallet_request("lock", [], log_response=False)['result']
            is_locked = self.send_wallet_request("is_locked", [], log_response=False)['result']
        else:
            lcc.log_info("Wallet is locked, unlock to checking the wallet lock process")
            self.send_wallet_request("unlock", [WALLET_PASSWORD], log_response=False)['result']
            is_locked = self.send_wallet_request("is_locked", [], log_response=False)['result']
            if not is_locked:
                lcc.log_info("Lock wallet")
                self.send_wallet_request("lock", [], log_response=False)['result']
            is_locked = self.send_wallet_request("is_locked", [], log_response=False)['result']

        check_that("wallet lock status", is_locked, equal_to(True))
