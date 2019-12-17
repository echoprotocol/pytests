# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, is_false, has_length, is_not_none

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

        # todo: ECHO-1241, ECHO-1428

        lcc.log_info("Get account btc asset balance")
        params = [self.echo_acc0, ["1.3.2"]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        privious = self.get_response(response_id)["result"][0]["amount"]

        lcc.log_info("Create sidechain_btc_withdraw_operation")
        amount = 1000000
        btc_address = 'mmYVef1naUBA4Y5PWYJA8fZRPKAkwdMD4L'
        operation = self.echo_ops.get_sidechain_btc_withdraw_operation(echo=self.echo, account=self.echo_acc0,
                                                                       btc_address=btc_address,
                                                                       value=amount)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=True)

        lcc.log_info("Get account btc asset balance")
        params = [self.echo_acc0, ["1.3.2"]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        current = self.get_response(response_id)["result"][0]["amount"]

        import time
        time.sleep(3)

        check_that("'notices id'", privious, equal_to(current + amount))

        lcc.set_step("Get btc_withdraws")
        params = [["1.22.0", "1.22.1", "1.22.2", "1.22.3", "1.22.4"]]
        response_id = self.send_request(self.get_request("get_objects", params),
                                        self.__database_api_identifier, debug_mode=True)
        btc_withdraws = self.get_response(response_id, log_response=True)["result"]

        for i, withdraw in enumerate(btc_withdraws):
            lcc.log_info("withdraw: {}".format(params[0][i]))
            if check_that("'btc_withdraw'", withdraw, is_not_none()):
                check_that("'btc_withdraw'", withdraw, has_length(8))
                check_that("'account'", withdraw["account"], equal_to(self.echo_acc0))
                check_that("'btc address'", withdraw["btc_addr"], equal_to(btc_address))
                check_that("'value'", withdraw["value"], equal_to(amount))
                check_that("'is_approved'", withdraw["is_approved"], is_false())

        lcc.set_step("Get btc_aggregatings")
        params = [["1.23.0", "1.23.1", "1.23.2", "1.23.3", "1.23.4", "1.23.5"]]
        response_id = self.send_request(self.get_request("get_objects", params),
                                        self.__database_api_identifier, debug_mode=True)
        btc_aggregatings = self.get_response(response_id, log_response=True)["result"]
        for i, aggregating in enumerate(btc_aggregatings):
            lcc.log_info("withdraw: {}".format(params[0][i]))
            if check_that("'btc_aggregating'", aggregating, is_not_none()):
                if check_that("'btc_aggregating'", aggregating, has_length(14)):
                    check_that("'cpfp_depth'", aggregating["cpfp_depth"], equal_to(i))
                    check_that("'is_approved'", aggregating["is_approved"], is_false())
                else:
                    check_that("'btc_aggregating'", aggregating, has_length(15))
                    check_that("'cpfp_depth'", aggregating["cpfp_depth"], equal_to(i))
                    # check_that("'previous_aggregation'", aggregating["previous_aggregation"], is_str())
                    check_that("'is_approved'", aggregating["is_approved"], is_false())

        params = [self.echo_acc0, "btc"]
        response_id = self.send_request(self.get_request("get_account_deposits", params),
                                        self.__database_api_identifier)
        deposits = self.get_response(response_id, log_response=True)

        params = [self.echo_acc0, "btc"]
        response_id = self.send_request(self.get_request("get_account_withdrawals", params),
                                        self.__database_api_identifier)
        deposits = self.get_response(response_id, log_response=True)

        lcc.set_step("Get history of new account and echo_acc0 account")
        operation_history_obj = "{}0".format(self.get_object_type(self.echo.config.object_types.OPERATION_HISTORY))
        stop, start = operation_history_obj, operation_history_obj
        limit = 100
        params = [self.new_account, stop, limit, start]
        response_id = self.send_request(self.get_request("get_account_history", params), self.__history_api_identifier)
        result = self.get_response(response_id)["result"]
        new_acc_ids = [dict["op"][0] for dict in result]

        params = [self.echo_acc0, stop, limit, start]
        response_id = self.send_request(self.get_request("get_account_history", params), self.__history_api_identifier)
        result = self.get_response(response_id)["result"]
        acc0_ids = [dict["op"][0] for dict in result]
        external_virtual_op_ids = set(new_acc_ids + acc0_ids)
        lcc.log_info(str("Accounts operations ids: {}".format(external_virtual_op_ids)))

        lcc.set_step("Get history of committee member account")
        params = ["1.2.6", stop, limit, start]
        response_id = self.send_request(self.get_request("get_account_history", params), self.__history_api_identifier)
        result = self.get_response(response_id)["result"]
        internal_ids = set([dict["op"][0] for dict in result])
        lcc.log_info(str("Committee member account operations ids: {}".format(internal_ids)))

        lcc.set_step("Check that external and virtual operations logs separate from internal operation logs")
        fist_sidechain_op_id = 38
        last_sidechain_op_id = 64
        for op_id in external_virtual_op_ids:
            if op_id in internal_ids and op_id < last_sidechain_op_id and op_id > fist_sidechain_op_id:
                raise Exception("Wrong work of method get_contract_history, get id: {}".format(op_id))

