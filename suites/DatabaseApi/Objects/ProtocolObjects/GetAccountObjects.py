# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import has_length, require_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_objects' (account object)"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_objects", "get_objects")
@lcc.suite("Check work of method 'get_objects' (account object)", rank=1)
class GetAccountObjects(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def check_fields_account_ids_format(self, response, field):
        if not self.type_validator.is_account_id(response[field]):
            lcc.log_error("Wrong format of '{}', got: {}".format(field, response[field]))
        else:
            lcc.log_info("'{}' has correct format: account_object_type".format(field))

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.test("Simple work of method 'get_objects' (account object)")
    def method_main_check(self):
        lcc.set_step("Get accounts objects")
        params = ["1.2.0", "1.2.1"]
        response_id = self.send_request(self.get_request("get_objects", [params]), self.__database_api_identifier)
        results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with params: {}".format(params))

        lcc.set_step("Check length of received objects")
        require_that(
            "'list of received objects'",
            results, has_length(len(params))
        )

        for i, account_info in enumerate(results):
            lcc.set_step("Checking account object #{} - '{}'".format(i, params[i]))
            self.object_validator.validate_account_structure(self, account_info)

        lcc.set_step("Get info about default accounts")
        response_id = self.send_request(self.get_request("get_accounts", [params]), self.__database_api_identifier)
        get_accounts_results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_accounts' with params: {}".format(params))

        lcc.set_step("Check the identity of returned results of api-methods: 'get_accounts', 'get_objects'")
        require_that(
            'results',
            results, equal_to(get_accounts_results),
            quiet=True
        )
