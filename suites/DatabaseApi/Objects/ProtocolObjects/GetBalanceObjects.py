# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, require_that, has_length

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_objects' (balance objects)"
}


@lcc.prop("main", "type")
@lcc.tags("api", "database_api", "database_api_objects", "get_objects")
@lcc.suite("Check work of method 'get_objects' (balance objects)", rank=1)
class GetBalanceObjects(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.public_key = None
        self.init3_account_name = "init3"

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        if self.utils.check_accounts_have_initial_balances([self.init3_account_name]):
            lcc.set_step("Check execution status")
            lcc.set_step("Setup for {}".format(self.__class__.__name__))
            self.__database_api_identifier = self.get_identifier("database")
            lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))
            self.public_key = self.get_account_by_name(self.init3_account_name,
                                                       self.__database_api_identifier)["result"]["echorand_key"]
            lcc.log_info("'{}' account public key: '{}'".format(self.init3_account_name, self.public_key))
        else:
            lcc.log_error("'{}' account does not have initial balance in genesis".format(self.init3_account_name))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'get_objects' (balance objects)")
    def method_main_check(self):
        lcc.set_step("Get balance objects by public key")
        response_id = self.send_request(self.get_request("get_balance_objects", [[self.public_key]]),
                                        self.__database_api_identifier)
        get_balance_objects_result = self.get_response(response_id, log_response=True)["result"][0]
        lcc.log_info("Call method 'get_balance_objects' with params: {}".format(self.public_key))
        balance_id = get_balance_objects_result["id"]

        params = [balance_id]
        lcc.set_step("Get balance object")
        response_id = self.send_request(self.get_request("get_objects", [params]),
                                        self.__database_api_identifier)
        results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with params: {}".format(params))

        lcc.set_step("Check length of received objects")
        require_that(
            "'list of received objects'",
            results, has_length(len(params)),
            quiet=True
        )

        for i, balance_info in enumerate(results):
            lcc.set_step("Checking balance object #{} - '{}'".format(i, params[i]))
            self.object_validator.validate_balance_object(self, balance_info)

            lcc.set_step("Check the identity of returned results of api-methods: 'get_balance_objects', 'get_objects'")
            check_that("get_object result of vesting_balance", balance_info, equal_to(get_balance_objects_result),
                       quiet=True)
