# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'get_account_count'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_accounts", "wallet_get_account_count")
@lcc.suite("Check work of method 'get_account_count'", rank=1)
class GetAccountCount(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("API identifiers are: database='{}'".format(self.__database_api_identifier))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_get_account_count'")
    def method_main_check(self):
        lcc.set_step("Get account count")
        response_id = self.send_request(self.get_request("get_account_count"), self.__database_api_identifier)
        response = self.get_response(response_id)
        DBApi_response_result = response['result']
        response = self.send_wallet_request("get_account_count", log_response=False)
        WalletApi_response_result = response['result']
        check_that('account count', DBApi_response_result, equal_to(WalletApi_response_result), quiet=True)
