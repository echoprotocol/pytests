# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_block_virtual_ops'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_blocks_transactions", "get_block_virtual_ops")
@lcc.suite("Check work of method 'get_block'", rank=1)
class GetBlockVirtualOps(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def get_head_block_num(self):
        return self.echo.api.database.get_dynamic_global_properties()["head_block_number"]

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'get_block_virtual_ops'")
    def method_main_check(self):
        lcc.set_step("Get the full first block in the chain")
        self.utils.set_timeout_until_num_blocks_released(self, self.__database_api_identifier, print_log=False)
        block_num = self.get_head_block_num()
        response_id = self.send_request(self.get_request("get_block_virtual_ops", [block_num]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_block_virtual_ops' with block_num='{}' parameter".format(block_num))

        check_that("result", response["result"], is_([]))


@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_blocks_transactions", "get_block_virtual_ops")
@lcc.suite("Positive testing of method 'get_block_virtual_ops'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Check virtual block_reward_operation in 1st block")
    def method_main_check(self):
        lcc.set_step("Get the first block virtual operations in the chain")
        block_num = 1
        virtual_operation_id = self.echo.config.operation_ids.BLOCK_REWARD
        response_id = self.send_request(self.get_request("get_block_virtual_ops", [block_num]),
                                        self.__database_api_identifier)
        block_operation_id = self.get_response(response_id)["result"][0]["op"][0]
        lcc.log_info("Call method 'get_block_virtual_ops' with block_num='{}' parameter".format(block_num))
        check_that("block_reward_operation", block_operation_id, is_(virtual_operation_id))
