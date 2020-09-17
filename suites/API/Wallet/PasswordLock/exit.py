# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc

SUITE = {
    "description": "Method 'exit'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_password_lock", "wallet_exit")
@lcc.suite("Check work of method 'exit'", rank=1)
class Exit(WalletBaseTest, BaseTest):

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

    @lcc.disabled()
    @lcc.test("Simple work of method 'wallet_exit'")
    def method_main_check(self):
        lcc.set_step("Check exit wallet method")
        exit = self.send_wallet_request("exit", [], log_response=False)['result']
        lcc.log_info("{}".format(exit))
