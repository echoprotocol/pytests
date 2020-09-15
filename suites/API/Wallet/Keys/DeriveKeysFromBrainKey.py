# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'derive_keys_from_brain_key'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_keys", "wallet_derive_keys_from_brain_key")
@lcc.suite("Check work of method 'derive_keys_from_brain_key'", rank=1)
class DeriveKeysFromBrainKey(WalletBaseTest, BaseTest):

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

    @lcc.test("Simple work of method 'wallet_derive_keys_from_brain_key'")
    def method_main_check(self):
        lcc.set_step("Derive keys from brain key")
        suggest_brain_key = self.send_wallet_request('suggest_brain_key', [], log_response=False)['result']
        if len(suggest_brain_key['brain_key'].split(' ')) == 16:
            lcc.log_info("Correct brain key")
        else:
            lcc.log_error("Wrong length of brain key.")
        request_result = self.send_wallet_request(
            'derive_keys_from_brain_key', [suggest_brain_key['brain_key'], 1], log_response=False
        )['result']
        check_that("derived key", request_result[0], equal_to(suggest_brain_key))
