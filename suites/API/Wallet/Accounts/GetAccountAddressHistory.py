# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
import time
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to
from project import INIT4_PK
SUITE = {
    "description": "Method 'get_account_address_history'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_accounts", "wallet_get_account_address_history")
@lcc.suite("Check work of method 'get_account_address_history'", rank=1)
class GetAccountAddressHistory(WalletBaseTest, BaseTest):

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
        self.init4 = self.get_account_id(
            'init4', self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo account are: #1='{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_get_account_address_history'")
    def method_main_check(self, get_random_string, get_random_integer_up_to_ten):
        label = get_random_string
        transfer_amount = get_random_integer_up_to_ten
        operation_history_obj = "{}0".format(self.get_object_type(self.echo.config.object_types.OPERATION_HISTORY))
        start = stop = operation_history_obj
        lcc.set_step("Create account address for new account")
        broadcast_result = self.utils.perform_account_address_create_operation(
            self, self.echo_acc0, label, self.__database_api_identifier
        )
        account_address_object = self.get_operation_results_ids(broadcast_result)
        response = self.send_wallet_request("get_object", [account_address_object], log_response=False)
        address = response['result'][0]['address']
        lcc.log_info("Account address create operation for new account performed, new address: {}".format(address))

        lcc.set_step("Check get_account_address_history response")

        self.utils.perform_transfer_to_address_operations(
            self,
            self.init4,
            address,
            self.__database_api_identifier,
            transfer_amount=transfer_amount,
            amount_asset_id=self.echo_asset,
            fee_asset_id=self.echo_asset,
            signer=INIT4_PK
        )

        lcc.set_step("Get account balance after transfer and store")
        time.sleep(10)
        self.produce_block(self.__database_api_identifier)
        result = self.send_wallet_request("get_account_address_history", [address, start, stop, 100], log_response=False)['result']
        transfer = result[0]['op'][1]
        check_that('amount of transfer operation in address history', transfer['amount']['amount'], equal_to(transfer_amount))
