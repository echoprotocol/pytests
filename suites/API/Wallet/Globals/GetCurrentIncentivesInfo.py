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

    def check_incentives_info(self, info, name):
        if self.type_validator.is_asset_id(info[0][0]):
            lcc.log_info("Correct format of {} asset id".format(name))
        else:
            lcc.log_info("Wrong format of {} asset id".format(name))
        if isinstance(info[0][1], int):
            lcc.log_info("Correct type of {} pool amount".format(name))
        else:
            lcc.log_info("Wrong {} pool amount type".format(name))

    @lcc.test("Simple work of method 'wallet_get_current_incentives_info'")
    def method_main_check(self):
        incentives_info = self.send_wallet_request("get_current_incentives_info", [], log_response=False)['result']
        self.check_incentives_info(incentives_info['incentives_pool'], 'incentives_pool')
        self.check_incentives_info(incentives_info['incentives'], 'incentives')
