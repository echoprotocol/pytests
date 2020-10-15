# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'call_contract'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_contracts", "wallet_call_contract")
@lcc.suite("Check work of method 'call_contract'", rank=1)
class CallContract(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.init4 = None
        self.contract = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet()")
        self.valid_contract_id = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier
            )
        )
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        self.init4 = self.get_account_id('init4', self.__database_api_identifier, self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.init4))
        self.valid_contract_id = self.utils.get_contract_id(
            self, self.echo_acc0, self.contract, self.__database_api_identifier
        )

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_call_contract'")
    def method_main_check(self):
        self.unlock_wallet()
        self.import_key('init4')

        lcc.set_step("Сheck call_contract method")
        response = self.send_wallet_request(
            "call_contract", [self.init4, self.valid_contract_id, self.greet, 1, self.echo_asset], log_response=False
        )['result']
        check_that("code", response['operations'][0][1]['code'], equal_to(self.greet))
