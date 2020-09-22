# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import INIT5_PK, WALLET_PASSWORD

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'request_unfreeze_balance'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_balances", "wallet_request_unfreeze_balance")
@lcc.suite("Check work of method 'request_unfreeze_balance'", rank=1)
class FreezeBalance(WalletBaseTest, BaseTest):

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

    # this test required smaller frozen_balances_multipliers and maintenance_interval
    # to run this test you should update genesis
    # TODO check after bug fixed ECHO-2404
    @lcc.disabled()
    @lcc.test("Simple work of method 'wallet_request_unfreeze_balance'")
    def method_main_check(self, get_random_integer):
        value_amount = get_random_integer
        lcc.set_step("Unlock wallet")
        response = self.send_wallet_request("is_new", [], log_response=False)
        if response['result']:
            self.send_wallet_request("set_password", [WALLET_PASSWORD], log_response=False)
        response = self.send_wallet_request("is_locked", [], log_response=False)
        if response['result']:
            self.send_wallet_request("unlock", [WALLET_PASSWORD], log_response=False)
        lcc.log_info("Wallet unlocked")
        lcc.set_step("Import key")
        self.send_wallet_request("import_key", ['init5', INIT5_PK], log_response=False)
        lcc.log_info("Key imported")

        lcc.set_step("Freeze balance")
        self.init5 = self.get_account_id('init5', self.__database_api_identifier, self.__registration_api_identifier)
        self.send_wallet_request(
            "freeze_balance", [self.init5, value_amount, self.echo_asset, 90, True], log_response=False
        )
        self.produce_block(self.__database_api_identifier)
        lcc.log_info('{} assets added to frozen balance'.format(value_amount))
        frozen_balance_id = self.send_wallet_request(
            "list_frozen_balances", [self.init5], log_response=False
        )["result"][-1]['id']
        lcc.set_step("Request unfreeze balance")
        request = self.send_wallet_request(
            "request_unfreeze_balance", [self.init5, [frozen_balance_id], True], log_response=False
        )
        # request_unfreeze_balance created bug https://jira.pixelplex.by/browse/ECHO-2404
        lcc.log_info("{}".format(request))
        response_id = self.send_request(
            self.get_request("get_objects", [[frozen_balance_id]]), self.__database_api_identifier
        )
        get_objects_results = self.get_response(response_id)["result"][0]
        check_that("frozen balance object", get_objects_results, equal_to(None), quiet=False)
