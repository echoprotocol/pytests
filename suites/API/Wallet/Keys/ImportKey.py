# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import INIT4_PK

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'import_key'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_keys", "wallet_import_key")
@lcc.suite("Check work of method 'import_key'", rank=1)
class ImportKey(WalletBaseTest, BaseTest):

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

    @lcc.test("Simple work of method 'wallet_generate_account_address'")
    def method_main_check(self):
        lcc.set_step("Import private key to wallet")
        request_result = self.send_wallet_request('import_key', ['init4', INIT4_PK], log_response=False)['result']
        check_that("import key status", request_result, equal_to(True), quiet=True)
