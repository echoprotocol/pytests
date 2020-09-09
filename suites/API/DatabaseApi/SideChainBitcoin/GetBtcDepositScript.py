# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc

SUITE = {
    "description": "Method 'get_btc_deposit_script'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags(
    "api", "database_api", "sidechain", "sidechain_bitcoin", "database_api_sidechain_bitcoin", "get_btc_deposit_script"
)
@lcc.suite("Check work of method 'get_btc_deposit_script'", rank=1)
class GetBtcDepositScript(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_ethereum()
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

    @lcc.test("Simple work of method 'get_btc_deposit_script'")
    def method_main_check(self, get_random_valid_account_name):
        new_account_name = get_random_valid_account_name
        backup_address = 'mipcBbFg9gMiCh81Kj8tqqdgoZub1ZJRfn'
        lcc.set_step("Create and get new account")
        new_account_id = self.get_account_id(
            new_account_name, self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account_id))

        lcc.set_step("Perform sidechain_btc_create_address_operation")
        operation = self.echo_ops.get_sidechain_btc_create_address_operation(
            echo=self.echo, account=new_account_id, backup_address=backup_address
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=1):
            lcc.log_error("'sidechain_btc_create_address_operation' fallen while broadcast")
        else:
            lcc.log_info("'sidechain_btc_create_address_operation' broadcasted successfully.")
        lcc.set_step("Call 'Get_btc_address' method and check its result")
        response_id = self.send_request(
            self.get_request("get_btc_address", [new_account_id]), self.__database_api_identifier
        )
        btc_address_id = self.get_response(response_id)["result"]["id"]

        response_id = self.send_request(
            self.get_request("get_btc_deposit_script", [btc_address_id]), self.__database_api_identifier
        )
        btc_deposit_script = self.get_response(response_id)["result"]
        if not self.type_validator.is_hex(btc_deposit_script):
            lcc.log_error("Wrong format of 'btc_deposit_script', got: {}".format(btc_deposit_script))
        else:
            lcc.log_info("response from 'get_btc_deposit_script' has correct format: hex")
