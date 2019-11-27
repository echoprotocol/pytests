# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import lemoncheesecake.api as lcc

from common.base_test import BaseTest
from fixtures.base_fixtures import get_random_integer

SUITE = {
    "description": "Check contract result id"
}


# @lcc.tags("Manual testing")
# @lcc.disabled()
@lcc.prop("main", "type")
@lcc.tags("scenarios", "check_contract_result_id")
@lcc.suite("Check scenario 'check_contract_result_id'")
class CheckContractResultId(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__network_broadcast_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None
        self.contract = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet()")

    def add_to_datetime(self, str_datetime, days=0, hours=0, minutes=0, seconds=0):
        formatted_datetime = datetime.strptime(str_datetime, "%Y-%m-%dT%H:%M:%S")
        formatted_datetime = formatted_datetime + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        return formatted_datetime.strftime("%Y-%m-%dT%H:%M:%S")

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__network_broadcast_identifier = self.get_identifier("network_broadcast")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', network_broadcast='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier,
                self.__network_broadcast_identifier))

        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc1 = self.get_account_id(self.accounts[1], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

    def setup_test(self, test):
        lcc.set_step("Setup for '{}'".format(str(test).split(".")[-1]))
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)
        lcc.log_info("Canceled all subscriptions successfully")

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'get_block_tx_number'")
    def method_main_check(self):
        subscription_callback_id, trx_to_broadcast = get_random_integer(), 1
        signed_trx = []
        amount = 1000

        lcc.set_step("First: Collect operation for deploying contract with expiration")
        operation = self.echo_ops.get_contract_create_operation(self.echo, self.echo_acc0, self.contract,
                                                                self.__database_api_identifier)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        datetime_str = self.get_datetime(global_datetime=True)
        datetime_str = self.add_to_datetime(datetime_str, seconds=10)
        signed_trx.append(self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                  expiration=datetime_str, no_broadcast=True, log_broadcast=True))

        lcc.set_step("Second: Collect operation for deploying contract with expiration")
        operation = self.echo_ops.get_contract_create_operation(self.echo, self.echo_acc0, self.contract,
                                                                self.__database_api_identifier)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        datetime_str = self.get_datetime(global_datetime=True)
        datetime_str = self.add_to_datetime(datetime_str, seconds=10)
        broadcast = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                            expiration=datetime_str, no_broadcast=True, log_broadcast=True)
        signed_trx.append(broadcast)

        lcc.set_step("Third: Collect operation for deploying contract withOUT expiration")
        operation = self.echo_ops.get_contract_create_operation(self.echo, self.echo_acc0, self.contract,
                                                                self.__database_api_identifier)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        signed_trx.append(self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                  no_broadcast=True, log_broadcast=True))


        lcc.set_step("Broadcast")
        for i in range(0, 100):
            try:
                params = [subscription_callback_id, signed_trx[0]]
                response_id = self.send_request(self.get_request("broadcast_transaction_with_callback", params),
                                                self.__network_broadcast_identifier, debug_mode=True)
                self.get_response(response_id, log_response=True)
            except:
                lcc.log_info("fuck")
            try:
                params = [subscription_callback_id, signed_trx[1]]
                response_id = self.send_request(self.get_request("broadcast_transaction_with_callback", params),
                                                self.__network_broadcast_identifier, debug_mode=True)
                self.get_response(response_id, log_response=True)
            except:
                lcc.log_info("fuck")
            try:
                response_id = self.send_request(self.get_request("broadcast_transaction_with_callback", params),
                                                self.__network_broadcast_identifier, debug_mode=True)
                self.get_response(response_id, log_response=True)
            except:
                lcc.log_info("fuck")

        # response_id = self.send_request(self.get_request("get_block", [68]),
        #                                 self.__database_api_identifier, debug_mode=True)
        # self.get_response(response_id, log_response=True)