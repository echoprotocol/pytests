# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc

from common.base_test import BaseTest

SUITE = {
    "description": "Entering the currency bitcoin in the network ECHO to the account and withdraw that currency"
}


@lcc.tags("manual")
@lcc.disabled()
@lcc.prop("main", "type")
@lcc.tags("scenarios", "sidechain", "sidechain_bitcoin", "scenarios_bitcoin")
@lcc.suite("Check scenario 'BtcToEcho and EchoToBtc'")
class Bitcoin(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.new_account = None
        self.temp_count = 0

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("The scenario checks the main parts before testing the bitcoin sidechain functionality")
    def bitcoin_sidechain_pre_run_scenario(self):
        lcc.log_info("Perform sidechain_btc_create_address_operation")
        operation = self.echo_ops.get_sidechain_btc_create_address_operation(echo=self.echo, account=self.echo_acc0,
                                                                             backup_address='mipcBbFg9gMiCh81Kj8tqqdgoZub1ZJRfn')
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=True)

        lcc.log_info("Get btc address")
        response_id = self.send_request(self.get_request("get_objects", [["1.19.0"]]), self.__database_api_identifier,
                                        debug_mode=True)
        response = self.get_response(response_id, log_response=True)

        lcc.log_info("Get account btc asset balance")
        params = [self.echo_acc0, ["1.3.2"]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier, debug_mode=True)
        current_balance = self.get_response(response_id, log_response=True)["result"][0]["amount"]
        half_balance = int(current_balance / 2)

        lcc.log_info("Create sidechain_btc_withdraw_operation")
        operation = self.echo_ops.get_sidechain_btc_withdraw_operation(echo=self.echo, account=self.echo_acc0,
                                                                       btc_address='mmYVef1naUBA4Y5PWYJA8fZRPKAkwdMD4L',
                                                                       value=half_balance)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=True)
        lcc.log_info("Get account btc asset balance")
        params = [self.echo_acc0, ["1.3.2"]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier, debug_mode=True)
        current_balance = self.get_response(response_id, log_response=True)["result"][0]["amount"]
