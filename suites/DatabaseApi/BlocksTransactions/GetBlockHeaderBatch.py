# -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, check_that_in, is_str, is_list, is_integer, has_length, equal_to, \
    check_that

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_block_header_batch'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("database_api", "get_block_header_batch")
@lcc.suite("Check work of method 'get_block_header_batch'", rank=1)
class GetBlockHeaderBatch(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_block_header_batch'")
    def method_main_check(self):
        lcc.set_step("Get the block header of the first block in the chain")
        block_num = 1
        response_id = self.send_request(self.get_request("get_block_header_batch", [[block_num]]),
                                        self.__database_api_identifier)
        results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_block_header_batch' with block_num='{}' parameter".format(block_num))

        lcc.set_step("Check simple work of method 'get_block_header'")
        for block_info in results:
            require_that("'get_block_header_batch' result", block_info, has_length(2))
            require_that("'number of searched block'", block_info[0], equal_to(block_num))
            if check_that("'length of the block info'", block_info[1], has_length(10)):
                check_that_in(
                    block_info[1],
                    "previous", is_str("0000000000000000000000000000000000000000"),
                    "round", is_integer(),
                    "attempt", is_integer(),
                    "transaction_merkle_root", is_str("0000000000000000000000000000000000000000"),
                    "vm_root", is_list(),
                    "prev_signatures", is_list(),
                    "extensions", is_list(),
                    quiet=True
                )
                if not self.validator.is_iso8601(block_info[1]["timestamp"]):
                    lcc.log_error("Wrong format of 'timestamp', got: {}".format(block_info[1]["timestamp"]))
                else:
                    lcc.log_info("'timestamp' has correct format: iso8601")
                if not self.validator.is_account_id(block_info[1]["account"]):
                    lcc.log_error("Wrong format of 'account id', got: {}".format(block_info[1]["account"]))
                else:
                    lcc.log_info("'id' has correct format: account_id")
                if not self.validator.is_account_id(block_info[1]["delegate"]):
                    lcc.log_error("Wrong format of 'delegate', got: {}".format(block_info[1]["delegate"]))
                else:
                    lcc.log_info("'delegate' has correct format: account_id")


@lcc.prop("positive", "type")
@lcc.tags("database_api", "get_block_header_batch")
@lcc.suite("Positive testing of method 'get_block_header_batch'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def get_random_block_num(self, _to, _from=1):
        block_num = random.randrange(_from, _to)
        if block_num == _to:
            return self.get_random_block_num(_to=_to, _from=_from)
        return block_num

    def get_head_block_number(self):
        self.produce_block(self.__database_api_identifier)
        response_id = self.send_request(self.get_request("get_dynamic_global_properties"),
                                        self.__database_api_identifier)
        head_block_number = self.get_response(response_id)["result"]["head_block_number"]
        return head_block_number

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Check info about several blocks")
    @lcc.depends_on("DatabaseApi.BlocksTransactions.GetBlockHeaderBatch.GetBlockHeaderBatch.method_main_check")
    def work_of_method_with_several_blocks(self):
        block_count = 2
        block_numbers = []

        lcc.set_step("Get random block numbers from first block to block header")
        for i in range(block_count):
            block_numbers.append(self.get_random_block_num(_to=self.get_head_block_number()))
        block_numbers = sorted(block_numbers)
        lcc.log_info("Random block numbers are: '{}'".format(block_numbers))

        lcc.set_step("Get the block header of the first block in the chain")
        response_id = self.send_request(self.get_request("get_block_header_batch", [block_numbers]),
                                        self.__database_api_identifier)
        results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_block_header_batch' with block_nums='{}' parameter".format(block_numbers))

        lcc.set_step("Check work 'get_block_header_batch' with several blocks")
        for i, block_info in enumerate(results):
            lcc.set_step("Check #'{}' block in 'get_block_header_batch' result".format(i))
            require_that("'get_block_header_batch' result", block_info, has_length(2))
            require_that("'number of searched block'", block_info[0], equal_to(block_numbers[i]))
            if check_that("'length of the block info'", block_info[1], has_length(10)):
                check_that_in(
                    block_info[1],
                    "round", is_integer(),
                    "vm_root", is_list(),
                    "prev_signatures", is_list(),
                    "extensions", is_list(),
                    quiet=True
                )
                if not self.validator.is_hex(block_info[1]["previous"]):
                    lcc.log_error("Wrong format of 'previous', got: {}".format(block_info[1]["previous"]))
                else:
                    lcc.log_info("'previous' has correct format: hex")
                if not self.validator.is_iso8601(block_info[1]["timestamp"]):
                    lcc.log_error("Wrong format of 'timestamp', got: {}".format(block_info[1]["timestamp"]))
                else:
                    lcc.log_info("'timestamp' has correct format: iso8601")
                if not self.validator.is_account_id(block_info[1]["account"]):
                    lcc.log_error("Wrong format of 'account id', got: {}".format(block_info[1]["account"]))
                else:
                    lcc.log_info("'id' has correct format: account_id")
                if not self.validator.is_account_id(block_info[1]["delegate"]):
                    lcc.log_error("Wrong format of 'delegate', got: {}".format(block_info[1]["delegate"]))
                else:
                    lcc.log_info("'delegate' has correct format: account_id")
                if not self.validator.is_hex(block_info[1]["transaction_merkle_root"]):
                    lcc.log_error("Wrong format of 'transaction_merkle_root', got: {}".format(
                        block_info[1]["transaction_merkle_root"]))
                else:
                    lcc.log_info("'transaction_merkle_root' has correct format: hex")

                prev_signatures = block_info[1]["prev_signatures"]
                for j, prev_signature in enumerate(prev_signatures):
                    lcc.log_info("Check fields in prev_signatures#'{}'".format(j))
                    check_that_in(
                        prev_signature,
                        "_step", is_integer(),
                        "_value", is_integer(),
                        "_producer", is_integer(),
                        "_delegate", is_integer(),
                        "_fallback", is_integer(),
                        quiet=True
                    )
                    if not self.validator.is_digit(prev_signature["_leader"]):
                        lcc.log_error("Wrong format of '_leader', got: {}".format(prev_signature["_leader"]))
                    else:
                        lcc.log_info("'_leader' has correct format: int")
                    if not self.validator.is_hex(prev_signature["_bba_sign"]):
                        lcc.log_error("Wrong format of '_bba_sign', got: {}".format(prev_signature["_bba_sign"]))
                    else:
                        lcc.log_info("'_bba_sign' has correct format: hex")
