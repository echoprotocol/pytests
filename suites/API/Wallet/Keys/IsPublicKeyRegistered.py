# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'is_public_key_registered'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_keys", "wallet_is_public_key_registered")
@lcc.suite("Check work of method 'is_public_key_registered'", rank=1)
class IsPublicKeyRegistered(WalletBaseTest, BaseTest):

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

    @lcc.test("Simple work of method 'wallet_is_public_key_registered'")
    def method_main_check(self):
        lcc.set_step("Check is public key registered")
        request_result = self.send_wallet_request('is_public_key_registered', ['ECHOCh3WGJCMKkBJHFJpzaC378cwwYisNbNKpD6oYhcuA6nR'], log_response=False)['result']
        check_that("key registered status", request_result, equal_to(True), quiet=True)
        request = self.send_wallet_request('create_eddsa_keypair', [], log_response=False)

        request_result = self.send_wallet_request('is_public_key_registered', [request['result'][0]], log_response=False)['result']
        if self.type_validator.is_echorand_key(request['result'][0]):
            check_that("key registered status", request_result, equal_to(False), quiet=True)
        else:
            lcc.log_error("Wrong format of key")
