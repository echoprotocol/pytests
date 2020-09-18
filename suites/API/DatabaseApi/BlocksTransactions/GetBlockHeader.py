# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import (
    check_that, check_that_in, equal_to, has_length, is_integer, is_list, is_str, require_that
)

SUITE = {
    "description": "Methods: 'get_block_header', 'get_objects' (block summary object)"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.prop("negative", "type")
@lcc.tags(
    "api", "database_api", "database_api_blocks_transactions", "get_block_header", "database_api_objects", "get_objects"
)
@lcc.suite("Check work of methods: 'get_block_header', 'get_objects' (block summary object)", rank=1)
class GetBlockHeader(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of methods: 'get_block_header', 'get_objects' (block summary object)")
    def method_main_check(self):
        lcc.set_step("Get the block header of the first block in the chain")
        block_num = 1
        response_id = self.send_request(
            self.get_request("get_block_header", [block_num]), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_block_header' with block_num='{}' parameter".format(block_num))

        lcc.set_step("Check simple work of method 'get_block_header'")
        block_header = response["result"]
        require_that("'the block header of the first block'", block_header, has_length(10), quiet=True)
        check_that_in(
            block_header,
            "previous",
            is_str(),
            "round",
            is_integer(),
            "attempt",
            is_integer(),
            "transaction_merkle_root",
            is_str(),
            "vm_root",
            is_list(),
            "prev_signatures",
            is_list(),
            "extensions",
            is_list(),
            quiet=True
        )
        if not self.type_validator.is_iso8601(block_header["timestamp"]):
            lcc.log_error("Wrong format of 'timestamp', got: {}".format(block_header["timestamp"]))
        else:
            lcc.log_info("'timestamp' has correct format: iso8601")
        if not self.type_validator.is_account_id(block_header["account"]):
            lcc.log_error("Wrong format of 'account id', got: {}".format(block_header["account"]))
        else:
            lcc.log_info("'id' has correct format: account_id")
        if not self.type_validator.is_account_id(block_header["delegate"]):
            lcc.log_error("Wrong format of 'delegate', got: {}".format(block_header["delegate"]))
        else:
            lcc.log_info("'delegate' has correct format: account_id")

        lcc.set_step("Get block summary object by id")
        params = ["2.7.{}".format(block_num - 1)]
        response_id = self.send_request(self.get_request("get_objects", [params]), self.__database_api_identifier)
        get_objects_results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with param: {}".format(params))

        lcc.set_step("Check length of received objects")
        require_that("'list of received objects'", get_objects_results, has_length(len(params)), quiet=True)

        lcc.set_step("Check block_summary object")
        self.object_validator.validate_block_summary_object(self, get_objects_results[0])
        check_that_in(get_objects_results[0], "block_id", equal_to(block_header["previous"]), quiet=True)


@lcc.prop("negative", "type")
@lcc.tags("api", "database_api", "database_api_blocks_transactions", "get_block_header")
@lcc.suite("Negative testing of method 'get_block_header'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("API identifier are: database='{}'".format(self.__database_api_identifier))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Check negative int value in get_block_header")
    @lcc.depends_on("API.DatabaseApi.BlocksTransactions.GetBlockHeader.GetBlockHeader.method_main_check")
    def check_negative_int_value_in_get_block_header(self):
        error_message = "Assert Exception: result >= 0: Invalid cast from negative number to unsigned"

        lcc.set_step("Get 'get_block_header' with negative block number")
        response_id = self.send_request(self.get_request("get_block_header", [-1]), self.__database_api_identifier)
        message = self.get_response(response_id, negative=True)["error"]["message"]
        check_that("error_message", message, equal_to(error_message), quiet=True)
