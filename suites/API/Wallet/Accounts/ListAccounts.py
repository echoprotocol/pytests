# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc

SUITE = {
    "description": "Method 'list_accounts'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_accounts", "wallet_list_accounts")
@lcc.suite("Check work of method 'list_accounts'", rank=1)
class GetListAccounts(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("API identifiers are: database='{}'".format(self.__database_api_identifier))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_list_accounts'")
    def method_main_check(self):
        limit = 10
        lcc.set_step("Get list accounts")
        response = self.send_wallet_request("list_accounts", ['', limit], log_response=False)
        for entry in range(limit):
            list_account_entry_id = response['result'][entry][1]
            if not self.type_validator.is_account_id(list_account_entry_id):
                lcc.log_error("Wrong format of 'list account entry id', got: {}".format(list_account_entry_id))
            else:
                lcc.log_info(
                    "List account entry id '{}' has correct format: account_object_type".format(list_account_entry_id)
                )
            list_account_entry_name = response['result'][entry][0]
            if not self.type_validator.is_account_name(list_account_entry_name):
                lcc.log_error("Wrong format of 'list account entry name', got: {}".format(list_account_entry_name))
            else:
                lcc.log_info(
                    "List account entry name '{}' has correct format: account_object_type"
                    .format(list_account_entry_name)
                )
