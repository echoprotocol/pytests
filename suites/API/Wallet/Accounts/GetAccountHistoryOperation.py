# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'get_account_history_operations'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_accounts", "wallet_get_account_history_operations")
@lcc.suite("Check work of method 'get_account_history_operations'", rank=1)
class GetAccountHistoryOperations(WalletBaseTest, BaseTest):

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
            "API identifiers are: database='{}', registration='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier
            )
        )
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        self.echo_acc1 = self.get_account_id(
            self.accounts[1], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_get_account_history_operations'")
    def method_main_check(self):
        operation_history_obj = "{}0".format(self.get_object_type(self.echo.config.object_types.OPERATION_HISTORY))
        start = stop = operation_history_obj
        operation_id = 0

        self.utils.perform_transfer_operations(
            self, self.echo_acc0, self.echo_acc1, self.__database_api_identifier, transfer_amount=5
        )
        self.produce_block(self.__database_api_identifier)
        lcc.set_step("Get relative account history")
        result = self.send_wallet_request(
            "get_account_history_operations", [self.echo_acc0, operation_id, start, stop, 1], log_response=False
        )['result'][0]

        check_that('operation id', result['op'][0], equal_to(operation_id))
        if self.type_validator.is_operation_history_id(result['id']):
            lcc.log_info("Correct format of history object")
        else:
            lcc.log_info("Wrong format of history object, got {}".format(result['id']))
