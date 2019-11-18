# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_objects' (frozen balances object)"
}


@lcc.prop("main", "type")
@lcc.tags("api", "database_api", "database_api_objects", "get_objects")
@lcc.suite("Check work of method 'get_objects' (frozen balances object)", rank=1)
class GetFrozenBalancesObject(BaseTest):

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

    @lcc.test("Simple work of method 'get_objects' (frozen balances object)")
    def method_main_check(self, get_random_integer):
        value_amount = get_random_integer

        lcc.set_step("Perform balance freeze operation")
        operation = self.echo_ops.get_balance_freeze_operation(echo=self.echo, account=self.echo_acc0,
                                                               value_amount=value_amount, duration=90)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("Balance freezeed")

        lcc.set_step("Get account frozen balance")
        response_id = self.send_request(self.get_request("get_frozen_balances", [self.echo_acc0]),
                                        self.__database_api_identifier)
        get_frozen_balances_result = self.get_response(response_id)["result"][0]
        lcc.log_info("Call method 'get_frozen_balances' with params: {}".format(self.echo_acc0))

        lcc.set_step("Get balance object")
        frozen_balances_id = get_frozen_balances_result["id"]
        response_id = self.send_request(self.get_request("get_objects", [[frozen_balances_id]]),
                                        self.__database_api_identifier)
        get_object_result = self.get_response(response_id)["result"][-1]
        lcc.log_info("Call method 'get_objects' with params: {}".format(frozen_balances_id))

        lcc.set_step("Checking balance object")
        self.object_validator.validate_frozen_balance_object(self, get_object_result)

        lcc.set_step("Check the identity of returned results of api-methods: 'get_frozen_balances', 'get_objects'")
        check_that(
            "'get_object' result of 'get_frozen_balances'",
            get_object_result, equal_to(get_frozen_balances_result),
            quiet=True
        )
