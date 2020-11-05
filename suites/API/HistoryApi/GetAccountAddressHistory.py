# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from project import INIT4_PK

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'get_account_address_history'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "history_api", "get_account_address_history")
@lcc.suite("Check work of method 'get_account_address_history'", rank=1)
class GetAccountAddressHistory(BaseTest):

    def __init__(self):
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__history_api_identifier = None
        self.echo_acc0 = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__history_api_identifier = self.get_identifier("history")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', "
            "history='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier, self.__history_api_identifier
            )
        )
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        self.init4 = self.get_account_id('init4', self.__database_api_identifier, self.__registration_api_identifier)
        lcc.log_info("Echo account are: #1='{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'get_account_address_history'")
    def method_main_check(self, get_random_string, get_random_integer_up_to_ten):
        label = get_random_string
        transfer_amount = get_random_integer_up_to_ten
        limit = 1
        operation_history_obj = "{}0".format(self.get_object_type(self.echo.config.object_types.OPERATION_HISTORY))
        start = stop = operation_history_obj
        lcc.set_step("Create account address for new account")
        self.utils.perform_account_address_create_operation(self, self.echo_acc0, label, self.__database_api_identifier)

        lcc.set_step("Get account address")
        params = [self.echo_acc0, label]
        response_id = self.send_request(
            self.get_request("get_account_address_by_label", params), self.__database_api_identifier
        )
        address = self.get_response(response_id)["result"]
        lcc.log_info("new account address: '{}'".format(address))

        lcc.set_step("Check get_account_address_history response")
        lcc.log_info("Transfer to address {} assets".format(transfer_amount))
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

        lcc.set_step("Check that transfer operation added to address history")
        self.produce_block(self.__database_api_identifier)

        params = [address, start, stop, limit]
        response_id = self.send_request(
            self.get_request("get_account_address_history", params), self.__history_api_identifier
        )
        result = self.get_response(response_id)['result']

        transfer = result[0]['op'][1]
        check_that(
            'amount of transfer operation in address history', transfer['amount']['amount'], equal_to(transfer_amount)
        )
