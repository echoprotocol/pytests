# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import has_length, has_entry, require_that, check_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Methods: 'get_dynamic_global_properties', 'get_objects' (dynamic global property object)"
}


@lcc.prop("main", "type")
@lcc.prop("negative", "type")
@lcc.tags(
    "api", "database_api", "database_api_globals", "get_dynamic_global_properties",
    "database_api_objects", "get_objects"
)
@lcc.suite(
    "Check work of methods: 'get_dynamic_global_properties', 'get_objects' (dynamic global property object)", rank=1
)
class GetDynamicGlobalProperties(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.test(
        "Simple work of methods: 'get_dynamic_global_properties', 'get_objects' (dynamic global property object)"
    )
    def method_main_check(self):
        lcc.set_step("Get dynamic global properties")
        response_id = self.send_request(self.get_request("get_dynamic_global_properties"),
                                        self.__database_api_identifier)
        get_dynamic_global_properties_result = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_dynamic_global_properties'")

        lcc.set_step("Check main fields")
        self.object_validator.validate_dynamic_global_property_object(self, get_dynamic_global_properties_result)

        lcc.set_step("Get dynamic global propreties object")
        dynamic_global_properties_id = get_dynamic_global_properties_result["id"]
        params = [dynamic_global_properties_id]
        response_id = self.send_request(self.get_request("get_objects", [params]), self.__database_api_identifier)
        get_objects_results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with params: {}".format(params))

        lcc.set_step("Check length of received objects")
        require_that(
            "'list of received objects'",
            get_objects_results, has_length(len(params)),
            quiet=True
        )

        lcc.set_step(
            "Check the identity of returned results of api-methods: 'get_dynamic_global_properties', 'get_objects'"
        )
        require_that(
            'results',
            get_objects_results[0], equal_to(get_dynamic_global_properties_result),
            quiet=True
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
    @lcc.depends_on("API.DatabaseApi.Globals.GetDynamicGlobalProperties.GetDynamicGlobalProperties.method_main_check")
    def call_method_with_params(self, get_all_random_types):
        lcc.set_step("Call method with all types of params")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            response_id = self.send_request(self.get_request("get_dynamic_global_properties", random_values[i]),
                                            self.__api_identifier)
            response = self.get_response(response_id, negative=True)
            check_that(
                "'get_dynamic_global_properties' return error message with '{}' params".format(
                    random_type_names[i]
                ),
                response, has_entry("error"),
                quiet=True
            )
