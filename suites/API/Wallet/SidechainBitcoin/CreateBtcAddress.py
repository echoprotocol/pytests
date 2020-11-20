# -*- coding: utf-8 -*-
import time

from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'create_btc_address'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_sidechain_bitcoin", "wallet_create_btc_address")
@lcc.suite("Check work of method 'create_btc_address'", rank=1)
class CreateBtcAddress(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.init4 = None

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
        self.init4 = self.get_account_id('init4', self.__database_api_identifier, self.__registration_api_identifier)

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_create_btc_address'")
    def method_main_check(self):
        backup_address = 'mipcBbFg9gMiCh81Kj8tqqdgoZub1ZJRfn'

        response_id = self.send_request(
            self.get_request("get_btc_address", [self.init4]), self.__database_api_identifier
        )
        btc_address = self.get_response(response_id)["result"]
        if btc_address is None:
            self.unlock_wallet()
            self.import_key('init4')

            lcc.set_step("Get account withdrawals")
            result = self.send_wallet_request(
                "create_btc_address", [self.init4, backup_address, True], log_response=False
            )['result']
            time.sleep(10)
            response_id = self.send_request(
                self.get_request("get_btc_address", [self.init4]), self.__database_api_identifier
            )
            result = self.get_response(response_id)["result"]
            if self.type_validator.is_btc_address_id(result['id']):
                lcc.log_info("Id has correct format: '{}'".format(result['id']))
            else:
                lcc.log_error("Wrong id format!")

            check_that('account', result['account'], equal_to(self.init4))

            if self.type_validator.is_btc_address(result['deposit_address']['address']):
                lcc.log_info("Address has correct format: '{}'".format(result['deposit_address']['address']))
            else:
                lcc.log_error("Wrong address format!")
            check_that("backup_address", result['backup_address'], equal_to(backup_address))
        else:
            lcc.log_warning("Account {} already has btc address, method does not checked".format(self.init4))
