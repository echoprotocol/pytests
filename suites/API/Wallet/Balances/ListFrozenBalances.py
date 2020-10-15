# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'list_frozen_balances'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_balances", "wallet_list_frozen_balances")
@lcc.suite("Check work of method 'list_frozen_balances'", rank=1)
class ListFrozenBalances(WalletBaseTest, BaseTest):

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

    @lcc.test("Simple work of method 'wallet_list_frozen_balances'")
    def method_main_check(self, get_random_integer):
        value_amount = get_random_integer
        lcc.set_step("Perform balance freeze operation")
        operation = self.echo_ops.get_balance_freeze_operation(
            echo=self.echo, account=self.echo_acc0, value_amount=value_amount, duration=90
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        self.produce_block(self.__database_api_identifier)
        lcc.log_info("Balance freezed")

        lcc.set_step("Check list frozen balance method")
        result = self.send_wallet_request("list_frozen_balances", [self.echo_acc0], log_response=False)["result"][-1]
        check_that("frozen_balance", result['balance']['amount'], equal_to(value_amount))
        if self.type_validator.is_frozen_balance_id(result['id']):
            lcc.log_info("Correct format of frozen_balance_id")
        else:
            lcc.log_error("Wrong frozen_balance_id format!")
