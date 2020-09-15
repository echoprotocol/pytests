# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'get_account_by_address'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_accounts", "wallet_get_account_by_address")
@lcc.suite("Check work of method 'get_account_by_address'", rank=1)
class GetAccountByAddress(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

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
        lcc.log_info("Echo account are: #1='{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_get_account_by_address'")
    def method_main_check(self, get_random_string):
        label = get_random_string
        lcc.set_step("Create account address for new account")
        broadcast_result = self.utils.perform_account_address_create_operation(
            self, self.echo_acc0, label, self.__database_api_identifier
        )
        account_address_object = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("{}".format(account_address_object))
        response = self.send_wallet_request("get_object", [account_address_object], log_response=False)
        address = response['result'][0]['address']
        lcc.log_info("Account address create operation for new account performed, new address: {}".format(address))

        lcc.set_step("Check get_account_by_address response")
        response = self.send_wallet_request("get_account_by_address", [address], log_response=False)
        check_that('owner of {} address'.format(address), response['result'], equal_to(self.echo_acc0), quiet=True)
