# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, has_entry

SUITE = {
    "description": "Method 'get_chain_id'"
}


@lcc.prop("main", "type")
@lcc.prop("negative", "type")
@lcc.tags("api", "database_api", "database_api_globals", "get_chain_id")
@lcc.suite("Check work of method 'get_chain_id'", rank=1)
class GetChainId(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.test("Simple work of method 'get_chain_id'")
    def method_main_check(self):
        lcc.set_step("Get chain id")
        response_id = self.send_request(self.get_request("get_chain_id"), self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_chain_id'")

        lcc.set_step("Check main fields")
        if not self.type_validator.is_hex(response["result"]):
            lcc.log_error("Wrong format of 'chain_id', got: {}".format(response["result"]))
        else:
            lcc.log_info("'chain_id' has correct format: hex")


@lcc.prop("negative", "type")
@lcc.tags("api", "database_api", "database_api_globals", "get_chain_id")
@lcc.suite("Negative testing of method 'get_chain_id'", rank=2)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__api_identifier))

    @lcc.test("Call method with params of all types")
    @lcc.depends_on("API.DatabaseApi.Globals.GetChainId.GetChainId.method_main_check")
    def call_method_with_params(self, get_all_random_types):
        lcc.set_step("Call method with all types of params")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            if i == 4:
                continue
            response_id = self.send_request(self.get_request("get_chain_id", random_values[i]), self.__api_identifier)
            response = self.get_response(response_id, negative=True)
            check_that(
                "'get_chain_id' return error message with '{}' params".format(random_type_names[i]),
                response,
                has_entry("error"),
                quiet=True
            )
