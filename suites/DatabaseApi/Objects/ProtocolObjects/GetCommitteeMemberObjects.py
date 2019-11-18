# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import has_length, require_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_objects' (committee member object)"
}


@lcc.prop("main", "type")
@lcc.tags("api", "database_api", "database_api_objects", "get_objects")
@lcc.suite("Check work of method 'get_objects' (committee member object)", rank=1)
class GetCommitteeMemberObjects(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.test("Simple work of method 'get_objects' (committee member object)")
    def method_main_check(self):
        lcc.set_step("Get committee member object")
        params = ["1.4.0"]
        response_id = self.send_request(self.get_request("get_objects", [params]), self.__database_api_identifier)
        results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with params: {}".format(params))

        lcc.set_step("Check length of received objects")
        require_that(
            "'list of received objects'",
            results, has_length(len(params)),
            quiet=True
        )

        for i, asset_info in enumerate(results):
            lcc.set_step("Checking committee member object #{} - '{}'".format(i, params[i]))
            self.object_validator.validate_committee_member_object(self, asset_info)

        lcc.set_step("Get info about default committee member")
        response_id = self.send_request(
            self.get_request("get_committee_members", [params]),
            self.__database_api_identifier
        )
        get_assets_results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_committee_members' with params: {}".format(params))

        lcc.set_step("Check the identity of returned results of api-methods: 'get_committee_members', 'get_objects'")
        require_that(
            'results',
            results, equal_to(get_assets_results),
            quiet=True
        )
