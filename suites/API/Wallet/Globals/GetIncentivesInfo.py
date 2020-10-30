# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'get_incentives_info'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_accounts", "wallet_get_incentives_info")
@lcc.suite("Check work of method 'get_incentives_info'", rank=1)
class GetIncentivesInfo(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier
            )
        )

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

    @lcc.test("Simple work of method 'wallet_get_incentives_info'")
    def method_main_check(self):
        head_block_num = self.get_head_block_number()
        incentives_info = self.send_wallet_request(
            "get_incentives_info", [head_block_num - 1, head_block_num], log_response=False
        )['result'][-1]
        check_that("block number", incentives_info['incentives_pool']['block_number'], equal_to(head_block_num))
        if self.type_validator.is_incentives_pool_id(incentives_info['incentives_pool']['id']):
            lcc.log_info("Correct format of incentives_pool id")
        else:
            lcc.log_error("Wrong format of incentives_pool id, got {}".format(incentives_info['incentives_pool']['id']))
        check_that("incentives asset", incentives_info['incentives'][0][0], equal_to(self.echo_asset))
        check_that("incentives amount", incentives_info['incentives'][0][1], equal_to(0))
