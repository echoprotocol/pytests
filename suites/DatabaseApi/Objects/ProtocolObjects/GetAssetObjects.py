# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import has_length, require_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_objects' (asset object)"
}


@lcc.prop("main", "type")
@lcc.tags("api", "database_api", "database_api_objects", "get_objects")
@lcc.suite("Check work of method 'get_objects' (asset object)", rank=1)
class GetAssetObjects(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.test("Simple work of method 'get_objects' (asset object)")
    def method_main_check(self):
        lcc.set_step("Get asset object")
        params = ["1.3.0"]
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
            lcc.set_step("Checking asset object #{} - '{}'".format(i, params[i]))
            self.object_validator.validate_asset_object(self, asset_info)

        lcc.set_step("Get info about default asset")
        response_id = self.send_request(self.get_request("get_assets", [params]), self.__database_api_identifier)
        get_assets_results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_assets' with params: {}".format(params))

        lcc.set_step("Check the identity of returned results of api-methods: 'get_assets', 'get_objects'")
        require_that(
            'results',
            results, equal_to(get_assets_results),
            quiet=True
        )
