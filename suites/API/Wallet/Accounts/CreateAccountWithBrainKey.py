# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'create_account_with_brain_key'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_accounts", "wallet_create_account_with_brain_key")
@lcc.suite("Check work of method 'create_account_with_brain_key'", rank=1)
class CreateAccountWithBrainKey(WalletBaseTest, BaseTest):

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

    @lcc.test("Simple work of method 'wallet_create_account_with_brain_key'")
    def method_main_check(self, get_random_valid_account_name, get_random_eth_address):
        new_account = get_random_valid_account_name
        evm_address = get_random_eth_address
        keys = self.generate_keys()

        self.unlock_wallet()
        self.import_key('init4')

        lcc.set_step("Create a transaction to generate account address")
        self.init4 = self.get_account_id('init4', self.__database_api_identifier, self.__registration_api_identifier)

        lcc.set_step("Check that new account registrated")
        response = self.send_wallet_request(
            "create_account_with_brain_key", [keys[2], new_account, self.init4, evm_address, True, True],
            log_response=False
        )
        lcc.log_info(str(response))
        check_that(
            "registrated account name",
            response['result'][0]['operations'][0][1]['name'],
            equal_to(new_account),
            quiet=True
        )
