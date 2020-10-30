# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc

SUITE = {
    "description": "Method 'get_current_incentives_info'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_globals", "get_current_incentives_info")
@lcc.suite("Check work of method 'get_current_incentives_info'", rank=1)
class GetCurrentIncentivesInfo(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    def check_incentives_info(self, info, name):
        if self.type_validator.is_asset_id(info[0][0]):
            lcc.log_info("Correct format of {} asset id".format(name))
        else:
            lcc.log_info("Wrong format of {} asset id".format(name))
        if isinstance(info[0][1], int):
            lcc.log_info("Correct type of {} pool amount".format(name))
        else:
            lcc.log_info("Wrong {} pool amount type".format(name))

    @lcc.test("Simple work of method 'get_current_incentives_info'")
    def method_main_check(self):
        lcc.set_step("Get current incentives info")
        response_id = self.send_request(self.get_request("get_current_incentives_info", []), self.__database_api_identifier)
        incentives_info = self.get_response(response_id)['result']
        lcc.log_info("Call method 'get_current_incentives_info'")
        self.check_incentives_info(incentives_info['incentives_pool'], 'incentives_pool')
        self.check_incentives_info(incentives_info['incentives'], 'incentives')
