# -*- coding: utf-8 -*-

from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, not_equal_to

SUITE = {
    "description": "Operation 'request_balance_unfreeze'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "balance_object_operations", "request_balance_unfreeze")
@lcc.suite("Check work of method 'request_balance_unfreeze'", rank=1)
class RequestBalanceUnfreeze(BaseTest):

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
            "API identifiers are: database='{}', registration='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier
            )
        )
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo accounts are: #1='{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    # todo: enable in github
    # this test required smaller frozen_balances_multipliers and maintenance_interval
    # to run this test you should update genesis
    @lcc.disabled()
    @lcc.test("Simple work of operation 'request_balance_unfreeze'")
    def method_main_check(self, get_random_integer):
        value_amount = get_random_integer

        lcc.set_step("Perform balance freeze operation")
        operation = self.echo_ops.get_balance_freeze_operation(
            echo=self.echo, account=self.echo_acc0, value_amount=value_amount, duration=1
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("Balance of {} account was frozen".format(self.echo_acc0))

        lcc.set_step("Get account frozen balance")
        response_id = self.send_request(
            self.get_request("get_frozen_balances", [self.echo_acc0]), self.__database_api_identifier
        )
        response = self.get_response(response_id)

        frozen_balance_amount = response["result"][-1]["balance"]["amount"]
        objects_to_unfreeze = response["result"][-1]["id"]
        lcc.log_info("{} assets added to frozen balance".format(frozen_balance_amount))
        check_that("freezed balance amount", frozen_balance_amount, equal_to(value_amount), quiet=False)
        response_id = self.send_request(
            self.get_request("get_objects", [[objects_to_unfreeze]]), self.__database_api_identifier
        )
        get_objects_results = self.get_response(response_id)["result"][0]
        check_that("freezed balance amount", get_objects_results, not_equal_to(None), quiet=False)

        lcc.set_step("Unfreeze balance")
        operation = self.echo_ops.get_request_balance_unfreeze_operation(
            echo=self.echo, account=self.echo_acc0, objects_to_unfreeze=[objects_to_unfreeze]
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        response_id = self.send_request(
            self.get_request("get_objects", [[objects_to_unfreeze]]), self.__database_api_identifier
        )
        get_objects_results = self.get_response(response_id)["result"][0]
        check_that("freezed balance amount", get_objects_results, not_equal_to(None), quiet=False)

        self.set_timeout_wait(10)
        lcc.log_info("Balance has been unfrozen")
        self.produce_block(self.__database_api_identifier)
        lcc.set_step("Get account frozen balance")
        response_id = self.send_request(
            self.get_request("get_objects", [[objects_to_unfreeze]]), self.__database_api_identifier
        )
        get_objects_results = self.get_response(response_id)["result"][0]
        check_that("freezed balance amount", get_objects_results, equal_to(None), quiet=False)
