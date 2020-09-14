# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc

from lemoncheesecake.matching import check_that, equal_to, not_equal_to

SUITE = {
    "description": "Method 'normalize_brain_key'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_keys", "wallet_normalize_brain_key")
@lcc.suite("Check work of method 'normalize_brain_key'", rank=1)
class NormalizeBrainKey(WalletBaseTest, BaseTest):

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

    @lcc.test("Simple work of method 'wallet_normalize_brain_key'")
    def method_main_check(self):
        lcc.set_step("Check normalize brain key")
        request_result = self.send_wallet_request('suggest_brain_key', [], log_response=False)['result']
        if len(request_result['brain_key'].split(' ')) == 16:
            lcc.log_info("Correct brain key")
        else:
            lcc.log_error("Wrong length of brain key.")

        normalize_brain_key = self.send_wallet_request('normalize_brain_key', [request_result['brain_key']], log_response=False)['result']
        check_that("normalize_brain_key", request_result['brain_key'], equal_to(normalize_brain_key))
        brain_key_copy = request_result['brain_key']
        brain_key_copy = brain_key_copy.lower()
        brain_key_copy = brain_key_copy.replace(" ", "  ")

        check_that("normalize_brain_key", brain_key_copy, not_equal_to(request_result['brain_key']))

        normalize_brain_key = self.send_wallet_request('normalize_brain_key', [brain_key_copy], log_response=False)['result']
        check_that("normalize_brain_key", normalize_brain_key, equal_to(request_result['brain_key']))
