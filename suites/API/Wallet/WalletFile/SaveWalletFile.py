# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'save_wallet_file'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_wallet_file", "wallet_save_wallet_file")
@lcc.suite("Check work of method 'save_wallet_file'", rank=1)
class SaveWalletFile(WalletBaseTest, BaseTest):

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

    @lcc.test("Simple work of method 'wallet_save_wallet_file'")
    def method_main_check(self, get_random_string):
        file_name = get_random_string
        lcc.set_step("Check method save_wallet_file")
        lcc.log_info("Try to load a non-existent wallet file")
        request_result = self.send_wallet_request(
            'load_wallet_file', [file_name + '.json'], log_response=False
        )['result']
        check_that("import key status", request_result, equal_to(False), quiet=True)
        lcc.log_info("Save wallet file '{}'".format(file_name + '.json'))
        request_result = self.send_wallet_request(
            'save_wallet_file', [file_name + '.json'], log_response=False
        )['result']
        check_that("import key status", request_result, equal_to(None), quiet=True)
        lcc.log_info("Load created wallet file '{}'".format(file_name + '.json'))
        request_result = self.send_wallet_request(
            'load_wallet_file', [file_name + '.json'], log_response=False
        )['result']
        check_that("import key status", request_result, equal_to(True), quiet=True)
