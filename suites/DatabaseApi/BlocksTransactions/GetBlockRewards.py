# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, check_that_in, is_str, is_list, is_integer, check_that, equal_to, \
    has_length, is_true

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_block_rewards'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_blocks_transactions", "get_block_rewards")
@lcc.suite("Check work of method 'get_block_rewards'", rank=1)
class GetBlock(BaseTest):

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

    @lcc.test("Simple work of method 'get_block_rewards'")
    def method_main_check(self):
        lcc.set_step("Get the full first block in the chain")
        block_num = 1
        response_id = self.send_request(self.get_request("get_block_rewards", [block_num]), self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_block_rewards' with block_num='{}' parameter".format(block_num))

        lcc.set_step("Check simple work of method 'get_block_rewards'")
        result = response["result"]
        require_that(
            "'the first full block'",
            result, has_length(3)
        )
        check_that_in(
            result,
            "emission", is_integer(),
            "fees", is_integer(),
            "rewards", is_list()
        )