# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from eth_utils import is_list
from lemoncheesecake.matching import require_that, has_length, check_that, check_that_in, is_list, is_, is_integer, \
    is_dict, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_frozen_balances'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_balances", "get_frozen_balances")
@lcc.suite("Check work of method 'get_frozen_balances'", rank=1)
class GetFrozenBalances(BaseTest):

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
        lcc.log_info(
            "API identifiers are: database='{}'".format(self.__database_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'get_frozen_balances'")
    def method_main_check(self, get_random_integer):
        value_amount = get_random_integer

        lcc.set_step("Get balances of account")
        params = [self.echo_acc0, [self.echo_asset]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        total_balance = self.get_response(response_id)["result"][0]["amount"]

        lcc.set_step("Perform balance freeze operation")
        operation = self.echo_ops.get_balance_freeze_operation(echo=self.echo, account=self.echo_acc0,
                                                               value_amount=value_amount, duration=90)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get required fee for default 'balance_freeze' operation")
        response_id = self.send_request(self.get_request("get_required_fees", [[operation[:-1]], self.echo_asset]),
                                        self.__database_api_identifier)
        fee_amount = self.get_response(response_id)["result"][0]["amount"]

        lcc.set_step("Get account frozen balance")
        response_id = self.send_request(self.get_request("get_frozen_balances", [self.echo_acc0]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]

        lcc.set_step("Check simple work of method 'get_frozen_balances'")
        require_that("'get_frozen_balances result'", result, is_list(), quiet=True)
        if check_that("frozen_balance", result[-1], has_length(6)):
            check_that_in(
                result[-1],
                "owner", is_(self.echo_acc0),
                "balance", is_dict(),
                "multiplier", is_integer(),
                "extensions", is_list(),
                quiet=True
            )
            balance = result[-1]["balance"]
            if check_that("balance", balance, has_length(2)):
                check_that_in(
                    balance,
                    "amount", is_(value_amount),
                    "asset_id", is_(self.echo_asset),
                    quiet=True
                )
            if not self.type_validator.is_frozen_balance_id(result[-1]["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(result["id"]))
            else:
                lcc.log_info("'id' has correct format: frozen_balance_type")
            if not self.type_validator.is_iso8601(result[-1]["unfreeze_time"]):
                lcc.log_error("Wrong format of 'unfreeze_time', got: {}".format(result["unfreeze_time"]))
            else:
                lcc.log_info("'unfreeze_time' has correct format: iso8601")
            frozen_balance = balance["amount"]

            lcc.set_step("Get unfrozen balances of account")
            params = [self.echo_acc0, [self.echo_asset]]
            response_id = self.send_request(self.get_request("get_account_balances", params),
                                            self.__database_api_identifier)
            unfrozen_balance = self.get_response(response_id)["result"][0]["amount"]

            lcc.set_step("Check account balances")
            require_that("balance", int(unfrozen_balance),
                         equal_to(int(total_balance) - int(frozen_balance) - int(fee_amount)))
