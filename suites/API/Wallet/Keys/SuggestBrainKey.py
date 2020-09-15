# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc

SUITE = {
    "description": "Method 'suggest_brain_key'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_keys", "wallet_suggest_brain_key")
@lcc.suite("Check work of method 'suggest_brain_key'", rank=1)
class SuggestBrainKey(WalletBaseTest, BaseTest):

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

    @lcc.test("Simple work of method 'wallet_suggest_brain_key'")
    def method_main_check(self):
        lcc.set_step("Check suggest brain key")
        request_result = self.send_wallet_request('suggest_brain_key', [], log_response=False)['result']
        if len(request_result['brain_key'].split(' ')) == 16:
            lcc.log_info("Correct brain key")
        else:
            lcc.log_error("Wrong length of brain key.")
        if self.type_validator.is_wif(request_result['active_priv_key']):
            lcc.log_info("Private key is correct!")
        else:
            lcc.log_error("Wrong format of private key.")
        if self.type_validator.is_echorand_key(request_result['echorand_pub_key']):
            lcc.log_info("Echorand private key is correct!")
        else:
            lcc.log_error("Wrong format of echorand private key.")
