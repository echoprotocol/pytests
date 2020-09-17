# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import WALLET_PASSWORD

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'set_password'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_password_lock", "wallet_set_password")
@lcc.suite("Check work of method 'set_password'", rank=1)
class SetPassword(WalletBaseTest, BaseTest):

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

    @lcc.test("Simple work of method 'wallet_set_password'")
    def method_main_check(self):
        lcc.set_step("Check set_password wallet method")
        is_new = self.send_wallet_request("is_new", [], log_response=False)['result']
        if is_new:
            lcc.log_info("Set a new wallet password")
            response = self.send_wallet_request("set_password", [WALLET_PASSWORD], log_response=False)['result']
            check_that("set_password", response, equal_to(None))
        else:
            is_locked = self.send_wallet_request("is_locked", [], log_response=False)['result']
            if is_locked:
                lcc.log_info("Unlock wallet")
                self.send_wallet_request("unlock", [WALLET_PASSWORD], log_response=False)['result']
                is_locked = self.send_wallet_request("is_locked", [], log_response=False)['result']
                lcc.log_info("Set a new wallet password")
                response = self.send_wallet_request("set_password", ["new_password"], log_response=False)['result']
                check_that("set_password", response, equal_to(None))

                self.send_wallet_request("unlock", ["new_password"], log_response=False)['result']
                self.send_wallet_request("set_password", [WALLET_PASSWORD], log_response=False)['result']
            else:
                response = self.send_wallet_request("set_password", ["new_password"], log_response=False)['result']
                check_that("set_password", response, equal_to(None))

                self.send_wallet_request("unlock", ["new_password"], log_response=False)['result']
                response = self.send_wallet_request("set_password", [WALLET_PASSWORD], log_response=False)['result']
                if response is None:
                    lcc.log_info("wallet reseted successfully")
