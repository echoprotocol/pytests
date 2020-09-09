# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc

from lemoncheesecake.matching import check_that, equal_to

from common.wallet_base_test import WalletBaseTest
from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_relative_account_history'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_accounts", "wallet_get_relative_account_history")
@lcc.suite("Check work of method 'get_relative_account_history'", rank=1)
class GetRelativeAccountHistory(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc1 = self.get_account_id(self.accounts[1], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_get_relative_account_history'")
    def method_main_check(self):
        lcc.set_step("Get relative account history")
        response_before_transfer = self.send_wallet_request("get_relative_account_history", [self.accounts[0], 0, 2, 0], log_response=False)

        lcc.set_step("Broadcast transfer operation")
        transfer_operation = self.echo_ops.get_transfer_operation(
            echo=self.echo, from_account_id=self.echo_acc0, to_account_id=self.echo_acc1, amount=2
        )
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("Transfered from {} to {} completed!".format(self.echo_acc0, self.echo_acc1))
        lcc.set_step("Get current relative account history")
        response_after_transfer = self.send_wallet_request("get_relative_account_history", [self.accounts[0], 0, 2, 0], log_response=False)
        check_that('updated relative account history', response_before_transfer['result'][0], equal_to(response_after_transfer['result'][1]), quiet=True)
