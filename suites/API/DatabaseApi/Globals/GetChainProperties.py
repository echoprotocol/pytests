# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, check_that, has_length, equal_to, has_entry

from common.base_test import BaseTest

SUITE = {
    "description": "Methods: 'get_chain_properties', 'get_objects' (chain property object)"
}


@lcc.prop("main", "type")
@lcc.prop("negative", "type")
@lcc.tags(
    "api", "database_api", "database_api_globals", "get_chain_properties",
    "database_api_objects", "get_objects"
)
@lcc.suite("Check work of methods: 'get_chain_properties', 'get_objects' (chain property object)", rank=1)
class GetChainProperties(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.test("Simple work of methods: 'get_chain_properties', 'get_objects' (chain property object)")
    def method_main_check(self):
        lcc.set_step("Get chain properties")
        response_id = self.send_request(self.get_request("get_chain_properties"), self.__database_api_identifier)
        get_chain_properties_results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_chain_properties'")

        lcc.set_step("Check main fields")
        self.object_validator.validate_chain_properties_object(self, get_chain_properties_results)

        lcc.set_step("Get chain properties object")
        params = [get_chain_properties_results["id"]]
        response_id = self.send_request(self.get_request("get_objects", [params]),
                                        self.__database_api_identifier)
        get_objects_results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with param: {}".format(params))

        lcc.set_step("Check length of received objects")
        require_that(
            "'list of received objects'",
            get_objects_results, has_length(len(params)),
            quiet=True
        )

        lcc.set_step(
            "Check the identity of returned results of api-methods: 'get_chain_properties', 'get_objects'"
        )
        require_that(
            'results',
            get_objects_results[0], equal_to(get_chain_properties_results),
            quiet=True
        )


@lcc.prop("negative", "type")
@lcc.tags("api", "database_api", "database_api_globals", "get_chain_properties")
@lcc.suite("Negative testing of method 'get_chain_properties'", rank=2)
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
    @lcc.depends_on("API.DatabaseApi.Globals.GetChainProperties.GetChainProperties.method_main_check")
    def call_method_with_params(self, get_all_random_types):
        lcc.set_step("Call method with all types of params")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            if i == 4:
                continue
            response_id = self.send_request(self.get_request("get_chain_properties", random_values[i]),
                                            self.__api_identifier)
            response = self.get_response(response_id, negative=True)
            check_that(
                "'get_chain_properties' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"),
                quiet=True
            )
