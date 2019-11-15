# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'vesting_balances_object'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "database_api", "database_api_objects", "get_objects")
@lcc.suite("Check work of method 'vesting_balances_object'", rank=1)
class GetVestingBalances(BaseTest):

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
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'vesting_balances_object'")
    def method_main_check(self, get_random_integer):
        value_amount = get_random_integer

        lcc.set_step("Perform 'vesting_balance_create_operation'")
        broadcast_result = self.utils.perform_vesting_balance_create_operation(self, self.echo_acc0,
                                                                               self.echo_acc0, value_amount,
                                                                               self.__database_api_identifier)
        vesting_balance_id = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("Vesting balance object '{}' created".format(vesting_balance_id))
        lcc.set_step("Get vesting balance object")
        params = [vesting_balance_id]
        response_id = self.send_request(self.get_request("get_objects", [params]),
                                        self.__database_api_identifier)
        get_object_result = self.get_response(response_id)["result"][0]
        lcc.log_info("Call method 'get_objects' with params: {}".format(params))

        lcc.set_step("Checking vesting balance object")
        self.object_validator.validate_vesting_balance_object(self, get_object_result)

        lcc.set_step("Get vesting balance of account")
        response_id = self.send_request(self.get_request("get_vesting_balances", [self.echo_acc0]),
                                        self.__database_api_identifier)
        get_vesting_balances_result = self.get_response(response_id)["result"][-1]
        lcc.log_info("Call method 'get_vesting_balances' with params: {}".format(self.echo_acc0))

        lcc.set_step("Check the identity of returned results of api-methods: 'get_vesting_balances', 'get_objects'")
        check_that("get_object result of vesting_balance", get_object_result, equal_to(get_vesting_balances_result),
                   quiet=True)
