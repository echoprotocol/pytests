# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc

SUITE = {
    "description": "Method 'create_eddsa_keypair'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_keys", "wallet_create_eddsa_keypair")
@lcc.suite("Check work of method 'create_eddsa_keypair'", rank=1)
class CreateEddsaKeypair(WalletBaseTest, BaseTest):

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
        lcc.set_step("Create eddsa keypair")
        request = self.send_wallet_request('create_eddsa_keypair', [], log_response=False)
        if self.type_validator.is_echorand_key(request['result'][0]):
            lcc.log_info("Created key {} has correct format!".format(request['result'][0]))
        else:
            lcc.log_error("Wrong format of key")
        if self.type_validator.is_wif(request['result'][1]):
            lcc.log_info("Created key {} has correct format!".format(request['result'][1]))
        else:
            lcc.log_error("Wrong format of key")
