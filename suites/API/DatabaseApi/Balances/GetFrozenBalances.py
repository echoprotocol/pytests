# -*- coding: utf-8 -*-

from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, check_that_in, equal_to, has_length, is_, is_list, require_that

SUITE = {
    "description": "Methods: 'get_frozen_balances', 'get_objects' (frozen balance object)"
}


@lcc.prop("main", "type")
@lcc.tags("api", "database_api", "database_api_balances", "get_frozen_balances", "database_api_objects", "get_objects")
@lcc.suite("Check work of methods: 'get_frozen_balances', 'get_objects' (frozen balance object)", rank=1)
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
        lcc.log_info("API identifiers are: database='{}'".format(self.__database_api_identifier))
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'get_frozen_balances'")
    def method_main_check(self, get_random_integer):
        value_amount = get_random_integer

        lcc.set_step("Get balances of account")
        params = [self.echo_acc0, [self.echo_asset]]
        response_id = self.send_request(
            self.get_request("get_account_balances", params), self.__database_api_identifier
        )
        total_balance = self.get_response(response_id)["result"][0]["amount"]

        lcc.set_step("Perform balance freeze operation")
        operation = self.echo_ops.get_balance_freeze_operation(
            echo=self.echo, account=self.echo_acc0, value_amount=value_amount, duration=90
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get required fee for default 'balance_freeze' operation")
        response_id = self.send_request(
            self.get_request("get_required_fees", [[operation[:-1]], self.echo_asset]), self.__database_api_identifier
        )
        fee_amount = self.get_response(response_id)["result"][0]["amount"]

        lcc.set_step("Get account frozen balance")
        response_id = self.send_request(
            self.get_request("get_frozen_balances", [self.echo_acc0]), self.__database_api_identifier
        )
        get_frozen_balances_result = self.get_response(response_id)["result"]

        lcc.set_step("Check simple work of method 'get_frozen_balances'")
        require_that("'get_frozen_balances result'", get_frozen_balances_result, is_list(), quiet=True)

        validate_object = get_frozen_balances_result[-1]
        self.object_validator.validate_frozen_balance_object(self, validate_object)
        check_that_in(validate_object, "owner", is_(self.echo_acc0), quiet=True)
        balance = validate_object["balance"]
        check_that_in(balance, "amount", is_(value_amount), "asset_id", is_(self.echo_asset), quiet=True)
        frozen_balance = balance["amount"]

        lcc.set_step("Get unfrozen balances of account")
        params = [self.echo_acc0, [self.echo_asset]]
        response_id = self.send_request(
            self.get_request("get_account_balances", params), self.__database_api_identifier
        )
        unfrozen_balance = self.get_response(response_id)["result"][0]["amount"]

        lcc.set_step("Check account balances")
        require_that(
            "balance",
            int(unfrozen_balance),
            equal_to(int(total_balance) - int(frozen_balance) - int(fee_amount)),
            quiet=True
        )

        lcc.set_step("Get frozen balance object")
        frozen_balances_id = validate_object["id"]
        params = [frozen_balances_id]
        response_id = self.send_request(self.get_request("get_objects", [params]), self.__database_api_identifier)
        get_objects_results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with params: {}".format(params))

        require_that("'list of received objects'", get_objects_results, has_length(len(params)), quiet=True)

        lcc.set_step("Check the identity of returned results of api-methods: 'get_frozen_balances', 'get_objects'")
        check_that(
            "'get_object' result of 'get_frozen_balances'",
            get_objects_results[-1],
            equal_to(validate_object),
            quiet=True
        )
