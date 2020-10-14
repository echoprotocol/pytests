# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, has_item, not_

SUITE = {
    "description": "Method 'whitelist_account'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_accounts", "wallet_whitelist_account")
@lcc.suite("Check work of method 'whitelist_account'", rank=1)
class WhitelistAccount(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.init4 = None

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_whitelist_account'")
    def method_main_check(self):
        self.unlock_wallet()
        self.import_key('init4')

        lcc.set_step("Check that account blacklisted")
        response = self.send_wallet_request(
            "whitelist_account", [self.init4, self.echo_acc0, 2, True], log_response=False
        )
        self.produce_block(self.__database_api_identifier)
        response = self.send_wallet_request("get_object", [self.init4], log_response=False)
        blacklisted_accounts = response['result'][0]['blacklisted_accounts']
        check_that("account {} blacklisted".format(self.echo_acc0), blacklisted_accounts, has_item(self.echo_acc0))

        lcc.set_step("Check that account whitelisted")
        response = self.send_wallet_request(
            "whitelist_account", [self.init4, self.echo_acc0, 1, True], log_response=False
        )
        self.produce_block(self.__database_api_identifier)
        response = self.send_wallet_request("get_object", [self.init4], log_response=False)
        whitelisted_accounts = response['result'][0]['whitelisted_accounts']
        check_that("account {} whitelisted".format(self.echo_acc0), whitelisted_accounts, has_item(self.echo_acc0))

        lcc.set_step("Check that account not in any of the lists")
        response = self.send_wallet_request(
            "whitelist_account", [self.init4, self.echo_acc0, 0, True], log_response=False
        )
        self.produce_block(self.__database_api_identifier)
        response = self.send_wallet_request("get_object", [self.init4], log_response=False)
        response_result = response['result'][0]
        check_that(
            "account {} not on whitelisted".format(self.echo_acc0), response_result['whitelisted_accounts'],
            not_(has_item(self.echo_acc0))
        )
        check_that(
            "account {} not on blacklisted".format(self.echo_acc0), response_result['blacklisted_accounts'],
            not_(has_item(self.echo_acc0))
        )
