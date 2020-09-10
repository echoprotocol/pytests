# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, has_item

from project import INIT4_PK
SUITE = {
    "description": "Method 'generate_account_address'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_accounts", "wallet_generate_account_address")
@lcc.suite("Check work of method 'generate_account_address'", rank=1)
class GenerateAccountAddress(WalletBaseTest, BaseTest):

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

    @lcc.test("Simple work of method 'wallet_generate_account_address'")
    def method_main_check(self, get_random_string):
        label = get_random_string
        lcc.set_step("Import private key to wallet")
        self.send_wallet_request('import_key', ['init4', INIT4_PK], log_response=False)
        lcc.log_info("key imported")

        lcc.set_step("Create a transaction to generate account address")
        self.init4_id = self.get_account_id(
            'init4', self.__database_api_identifier, self.__registration_api_identifier
        )

        response = self.send_wallet_request("generate_account_address", [self.init4_id, label, True], log_response=False)
        self.produce_block(self.__database_api_identifier)
        response = self.send_wallet_request("get_account_addresses", [self.init4_id, 0, 50], log_response=True)
        result_labels = [result['label'] for result in response['result']]
        check_that("label of new address", result_labels, has_item(label), quiet=False)
