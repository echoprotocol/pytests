# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'get_transaction'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_blocks_transactions", "wallet_get_transaction")
@lcc.suite("Check work of method 'get_transaction'", rank=1)
class GetTransaction(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
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

    def get_head_block_number(self):
        self.produce_block(self.__database_api_identifier)
        response_id = self.send_request(
            self.get_request("get_dynamic_global_properties"), self.__database_api_identifier
        )
        head_block_number = self.get_response(response_id)["result"]["head_block_number"]
        return head_block_number

    @lcc.test("Simple work of method 'wallet_get_transaction'")
    def method_main_check(self):
        self.produce_block(self.__database_api_identifier)
        head_block_num = self.get_head_block_number()
        lcc.set_step("Call method 'get_transaction'")
        response = self.send_wallet_request("get_transaction", [head_block_num, 0], log_response=True)
        check_that("transfer operation in transaction", response['result']['operations'][0][0], equal_to(0))
