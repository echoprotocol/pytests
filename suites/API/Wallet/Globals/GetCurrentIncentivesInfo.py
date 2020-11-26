# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc

SUITE = {
    "description": "Method 'get_current_incentives_info'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_accounts", "wallet_get_current_incentives_info")
@lcc.suite("Check work of method 'get_current_incentives_info'", rank=1)
class GetCurrentIncentivesInfo(WalletBaseTest, BaseTest):

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

    @lcc.test("Simple work of method 'wallet_get_current_incentives_info'")
    def method_main_check(self):
        incentives_info = self.send_wallet_request("get_current_incentives_info", [], log_response=False)['result']
        lcc.log_info("{}".format(incentives_info))
        if self.type_validator.is_incentives_pool_id(incentives_info['id']):
            lcc.log_info("Correct format of incentives pool id, got: {}".format(incentives_info['id']))
        else:
            lcc.log_info("Wrong format of incentives pool id, got: {}".format(incentives_info['id']))
        if self.type_validator.is_asset_id(incentives_info['pool'][0][0]):
            lcc.log_info("Correct format of {} asset id".format("pool"))
        else:
            lcc.log_info("Wrong format of {} asset id".format("pool"))
        if isinstance(incentives_info['pool'][0][1], int):
            lcc.log_info("Correct type of {} amount".format("pool"))
        else:
            lcc.log_info("Wrong {} amount type".format("pool"))
        if self.type_validator.is_asset_id(incentives_info['incentives'][0][0]):
            lcc.log_info("Correct format of {} asset id".format("incentives"))
        else:
            lcc.log_info("Wrong format of {} asset id".format("incentives"))
        if isinstance(incentives_info['incentives'][0][1], int):
            lcc.log_info("Correct type of {} amount".format("incentives"))
        else:
            lcc.log_info("Wrong {} amount type".format("incentives"))
        if isinstance(incentives_info['block_number'], int):
            lcc.log_info("Correct type of block_number, got {}".format(incentives_info['block_number']))
        else:
            lcc.log_info("Wrong type of block_number, got {}".format(incentives_info['block_number']))
