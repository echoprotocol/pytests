# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_bool

SUITE = {
    "description": "Method 'is_new'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_password_lock", "wallet_is_new")
@lcc.suite("Check work of method 'is_new'", rank=1)
class IsNew(WalletBaseTest, BaseTest):

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

    @lcc.test("Simple work of method 'wallet_is_new'")
    def method_main_check(self):
        lcc.set_step("Get is_new wallet status")
        response = self.send_wallet_request("is_new", [], log_response=False)['result']
        check_that("get wallet is_new status", response, is_bool())
