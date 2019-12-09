# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Operation 'balance_freeze'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "balance_object_operations", "balance_freeze")
@lcc.suite("Check work of method 'balance_freeze'", rank=1)
class BalanceFreeze(BaseTest):

    def __init__(self):
        super().__init__()
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
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of operation 'balance_freeze'")
    def method_main_check(self, get_random_integer):
        value_amount = get_random_integer

        lcc.set_step("Perform balance freeze operation")
        operation = self.echo_ops.get_balance_freeze_operation(echo=self.echo, account=self.echo_acc0,
                                                               value_amount=value_amount, duration=90)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get account frozen balance")
        response_id = self.send_request(self.get_request("get_frozen_balances", [self.echo_acc0]),
                                        self.__database_api_identifier)
        frozen_balance_amount = self.get_response(response_id)["result"][-1]["balance"]["amount"]
        lcc.log_info("{} assets added to frozen balance".format(frozen_balance_amount))
        check_that(
            "freezed balance amount",
            frozen_balance_amount, equal_to(value_amount),
            quiet=False
        )
