# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc

SUITE = {
    "description": "Method 'get_dynamic_global_properties'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_accounts", "wallet_get_dynamic_global_properties")
@lcc.suite("Check work of method 'get_dynamic_global_properties'", rank=1)
class WalletGetDynamicGlobalProperties(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_get_dynamic_global_properties'")
    def method_main_check(self):
        lcc.set_step('Check get_dynamic_global_properties method')
        get_dynamic_global_properties_result = self.send_wallet_request("get_dynamic_global_properties", [], log_response=False)['result']

        lcc.set_step("Check main fields")
        self.object_validator.validate_dynamic_global_property_object(self, get_dynamic_global_properties_result)
