# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'get_incentives_info'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_globals", "get_incentives_info")
@lcc.suite("Check work of method 'get_incentives_info'", rank=1)
class GetIncentivesInfo(BaseTest):

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

    def get_head_block_number(self):
        self.produce_block(self.__database_api_identifier)
        response_id = self.send_request(
            self.get_request("get_dynamic_global_properties"), self.__database_api_identifier
        )
        head_block_number = self.get_response(response_id)["result"]["head_block_number"]
        return head_block_number

    @lcc.test("Simple work of method 'get_incentives_info'")
    def method_main_check(self):
        lcc.set_step("Get incentives info")
        head_block_number = self.get_head_block_number()
        response_id = self.send_request(
            self.get_request("get_incentives_info", [head_block_number - 1, head_block_number]),
            self.__database_api_identifier
        )
        incentives_info = self.get_response(response_id)['result'][0]
        lcc.log_info("Call method 'get_incentives_info'")
        lcc.set_step("Check incentives_info format")
        check_that("block number", incentives_info['block_number'], equal_to(head_block_number - 1))
        if self.type_validator.is_incentives_pool_id(incentives_info['id']):
            lcc.log_info("Correct format of incentives id, got {}".format(incentives_info['id']))
        else:
            lcc.log_info("Wrong format of incentives id, got {}".format(incentives_info['id']))

        if self.type_validator.is_asset_id(incentives_info['pool'][0][0]):
            lcc.log_info("Correct format of {} asset id".format("pool"))
        else:
            lcc.log_info("Wrong format of {} asset id".format("pool"))
        if isinstance(incentives_info['pool'][0][1], int):
            lcc.log_info("Correct type of {} amount".format("pool"))
        else:
            lcc.log_info("Wrong {} amount type".format("pool"))
        if isinstance(incentives_info['incentives'][0][0], int) and isinstance(incentives_info['incentives'][0][1],
                                                                               int):
            lcc.log_info("Correct format of incentives")
        else:
            lcc.log_info("Wrong format of incentives")


@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_globals", "get_incentives_info")
@lcc.suite("Positive testing of method 'get_incentives_info'", rank=2)
class PositiveTesting(BaseTest):

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

    def get_head_block_number(self):
        self.produce_block(self.__database_api_identifier)
        response_id = self.send_request(
            self.get_request("get_dynamic_global_properties"), self.__database_api_identifier
        )
        head_block_number = self.get_response(response_id)["result"]["head_block_number"]
        return head_block_number

    @lcc.test("Simple work of method 'get_incentives_info'")
    def method_main_check(self):
        head_block_number = self.get_head_block_number()
        lcc.set_step("Get incentives info")
        response_id = self.send_request(
            self.get_request("get_incentives_info", [head_block_number, head_block_number]),
            self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_incentives_info'")
        check_that("block number", response['result'][0]['block_number'], equal_to(head_block_number))
        check_that('one block info returned', len(response['result']), equal_to(1))