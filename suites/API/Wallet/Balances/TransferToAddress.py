# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'transfer_to_address'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_balances", "wallet_transfer_to_address")
@lcc.suite("Check work of method 'transfer_to_address'", rank=1)
class TransferToAddress(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

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
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        self.init5 = self.get_account_id('init5', self.__database_api_identifier, self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.init5))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_transfer_to_address'")
    def method_main_check(self, get_random_integer, get_random_string):
        label = get_random_string
        operation_history_obj = "{}0".format(self.get_object_type(self.echo.config.object_types.OPERATION_HISTORY))
        start = stop = operation_history_obj
        transfer_amount = 1
        self.unlock_wallet()
        self.import_key('init5')

        lcc.set_step("Create account address for new account")
        self.utils.perform_account_address_create_operation(self, self.echo_acc0, label, self.__database_api_identifier)

        lcc.set_step("Get account address")
        params = [self.echo_acc0, label]
        response_id = self.send_request(
            self.get_request("get_account_address_by_label", params), self.__database_api_identifier
        )
        address = self.get_response(response_id)["result"]
        lcc.log_info("new account address: '{}'".format(address))

        self.send_wallet_request(
            "transfer_to_address", [self.init5, address, transfer_amount, self.echo_asset, True], log_response=False
        )
        result = self.send_wallet_request(
            "get_account_address_history", [address, start, stop, 1], log_response=False
        )['result']
        transfer = result[0]['op'][1]
        check_that(
            'amount of transfer operation in address history', transfer['amount']['amount'],
            equal_to(transfer_amount * 10 ** 8)
        )
