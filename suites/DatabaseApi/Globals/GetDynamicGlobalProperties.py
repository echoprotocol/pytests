# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, check_that, has_length, has_entry, greater_than_or_equal_to, \
    is_list

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_dynamic_global_properties'"
}


@lcc.prop("main", "type")
@lcc.prop("negative", "type")
@lcc.tags("api", "database_api", "database_api_globals", "get_dynamic_global_properties")
@lcc.suite("Check work of method 'get_dynamic_global_properties'", rank=1)
class GetDynamicGlobalProperties(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.test("Simple work of method 'get_dynamic_global_properties'")
    def method_main_check(self):
        lcc.set_step("Get dynamic global properties")
        response_id = self.send_request(self.get_request("get_dynamic_global_properties"),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_dynamic_global_properties'")

        lcc.set_step("Check main fields")
        dynamic_global_properties = ["head_block_number", "committee_budget",
                                     "dynamic_flags", "last_irreversible_block_num"]
        dynamic_global_properties_time = ["time", "next_maintenance_time", "last_budget_time"]
        result = response["result"]
        if check_that("dynamic global properties", result, has_length(10)):
            if not self.validator.is_dynamic_global_object_id(result["id"]):
                lcc.log_error("Wrong format of 'dynamic_global_object_id', got: {}".format(result))
            else:
                lcc.log_info("'id' has correct format: dynamic_global_object_id")
            for propertie in dynamic_global_properties:
                self.check_uint64_numbers(result, propertie, quiet=True)
                value = int(result[propertie])
                check_that(propertie, value, greater_than_or_equal_to(0), quiet=True)
            if not self.validator.is_hex(result["head_block_id"]):
                lcc.log_error("Wrong format of 'head_block_id', got: {}".format(result))
            else:
                lcc.log_info("'head_block_id' has correct format: hex")

            for time_propertie in dynamic_global_properties_time:
                if not self.validator.is_iso8601(result[time_propertie]):
                    lcc.log_error(
                        "Wrong format of '{}', got: {}".format(time_propertie, result[time_propertie]))
                else:
                    lcc.log_info("'{}' has correct format: iso8601".format(time_propertie))
            check_that_in(
                result, "extensions", is_list(), quiet=True
            )


@lcc.prop("negative", "type")
@lcc.tags("api", "database_api", "database_api_globals", "get_dynamic_global_properties")
@lcc.suite("Negative testing of method 'get_dynamic_global_properties'", rank=3)
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
    @lcc.tags("Bug: 'ECHO-680'")
    @lcc.depends_on("DatabaseApi.Globals.GetDynamicGlobalProperties.GetDynamicGlobalProperties.method_main_check")
    def call_method_with_params(self, get_all_random_types):
        lcc.set_step("Call method with all types of params")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            # todo: remove if. Bug: "ECHO-680"
            if i == 4:
                continue
            response_id = self.send_request(self.get_request("get_dynamic_global_properties", random_values[i]),
                                            self.__api_identifier)
            response = self.get_response(response_id, negative=True)
            check_that(
                "'get_dynamic_global_properties' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True
            )
