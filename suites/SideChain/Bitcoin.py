# -*- coding: utf-8 -*-

from __future__ import print_function

import json
import time

import lemoncheesecake.api as lcc
import requests
from lemoncheesecake.matching import check_that, equal_to, require_that

from common.base_test import BaseTest
from project import SATOSHI_PRECISION, SATOSHI_PER_BYTE, BTC_FEE, INIT0_PK

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
        self._session = None
        self.btc_url = None
        self._headers = None

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
        rpcPort = 18443
        rpcUser = 'test'
        rpcPassword = 'test'
        serverURL = 'http://' + rpcUser + ':' + rpcPassword + '@localhost:' + str(rpcPort)
        self.btc_url = serverURL
        self._session = requests.Session()
        self._headers = {'content-type': 'application/json'}

    def btc_call(self, rpcMethod, *params):
        payload = json.dumps({"method": rpcMethod, "params": list(params), "jsonrpc": "2.0"})
        tries = 5
        hadConnectionFailures = False
        while True:
            try:
                response = self._session.post(self.btc_url, headers=self._headers, data=payload)
            except requests.exceptions.ConnectionError:
                tries -= 1
                if tries == 0:
                    raise Exception('Failed to connect for remote procedure call.')
                hadFailedConnections = True
                print(
                    "Couldn't connect for remote procedure call, will sleep for five seconds and then try again ({} "
                    "more tries)".format(
                        tries))
                time.sleep(10)
            else:
                if hadConnectionFailures:
                    print('Connected for remote procedure call after retry.')
                break
        if not response.status_code in (200, 500):
            raise Exception('RPC connection failure: ' + str(response.status_code) + ' ' + response.reason)
        responseJSON = response.json()
        if 'error' in responseJSON and responseJSON['error'] != None:
            raise Exception('Error in RPC call: ' + str(responseJSON['error']))
        return responseJSON['result']

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("The scenario checks the main parts before testing the bitcoin sidechain functionality")
    def bitcoin_sidechain_pre_run_scenario(self):
        backup_address = 'mipcBbFg9gMiCh81Kj8tqqdgoZub1ZJRfn'
        deposit_amount = 5
        withdrawal_amount = 100000
        balance_before_deposit = 0

        lcc.set_step("Sent 10 btc coins to new address in BTC network")
        new_adress = self.btc_call('getnewaddress')

        # generate 101 block by new address
        self.btc_call('generatetoaddress', 101, new_adress)

        # send 10 btc coins to new address
        self.btc_call('sendtoaddress', new_adress, 10.00)

        # generate blocks for aggregation in sidechain
        for i in range(0, 4):
            self.btc_call('generate', 1)

        # get new address balance in BTC network
        balance = self.btc_call('getreceivedbyaddress', new_adress)
        require_that("btc network balance", balance, equal_to(10))

        lcc.log_info("Perform sidechain_btc_create_address_operation for account {}".format(self.echo_acc0))
        operation = self.echo_ops.get_sidechain_btc_create_address_operation(echo=self.echo, account=self.echo_acc0,
                                                                             backup_address=backup_address)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        operation_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=True)["trx"]["operation_results"][0][1]
        lcc.log_info("Operation result id: {}".format(operation_result))

        lcc.log_info("Get btc address ")
        response_id = self.send_request(self.get_request("get_objects", [["1.19.0"]]), self.__database_api_identifier)
        address = self.get_response(response_id)["result"][0]["deposit_address"]["address"]
        lcc.log_info("BTC address '{}' of account '{}'".format(address, self.echo_acc0))

        lcc.set_step("Get {} account btc asset balance".format(self.echo_acc0))
        params = [self.echo_acc0, ["1.3.2"]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        balance_before_deposit = self.get_response(response_id)["result"][0]["amount"]
        lcc.log_info("'{}' account btc balance = {}".format(self.echo_acc0, balance_before_deposit))

        #transfer 5 btc coins from btc network to echo network
        self.btc_call('sendtoaddress', address, deposit_amount)

        # generate blocks for aggregation in sidechain
        for i in range(0, 5):
            time.sleep(3)
            self.btc_call('generate', 1)

        lcc.log_info("Get {} account btc asset balance".format(self.echo_acc0))
        params = [self.echo_acc0, ["1.3.2"]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        balance_after_deposit = self.get_response(response_id)["result"][0]["amount"]
        check_that("account balance", balance_after_deposit,
                   equal_to(balance_before_deposit + deposit_amount * SATOSHI_PRECISION - SATOSHI_PER_BYTE * BTC_FEE))

        # todo: ECHO-1241, ECHO-1428

        lcc.log_info("Create BTC address for '1.2.6' account")
        operation = self.echo_ops.get_sidechain_btc_create_address_operation(echo=self.echo, account="1.2.6",
                                                                             backup_address=backup_address,
                                                                             signer=INIT0_PK)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        operation_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=True)["trx"]["operation_results"][0][1]
        lcc.log_info("Operation result id: {}".format(operation_result))

        lcc.log_info("Get btc address of '1.2.6' account")
        response_id = self.send_request(self.get_request("get_objects", [["1.19.2"]]), self.__database_api_identifier)
        new_btc_address = self.get_response(response_id, log_response=True)["result"][0]["deposit_address"]["address"]
        lcc.log_info("BTC address '{}' of account '1.2.6'".format(new_btc_address))

        lcc.log_info("Create sidechain_btc_withdraw_operation")
        operation = self.echo_ops.get_sidechain_btc_withdraw_operation(echo=self.echo, account=self.echo_acc0,
                                                                       btc_address=new_btc_address,
                                                                       value=withdrawal_amount)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=True)

        # generate blocks for aggregation in sidechain
        for i in range(0, 5):
            time.sleep(3)
            self.btc_call('generate', 1)

        lcc.set_step("Get account btc asset balance")
        params = [self.echo_acc0, ["1.3.2"]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        balance_after_withdrawal = self.get_response(response_id)["result"][0]["amount"]
        check_that("account balance", balance_after_withdrawal, equal_to(balance_after_deposit - withdrawal_amount))

        lcc.set_step("Get account btc asset balance")
        params = ["1.2.6", ["1.3.2"]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        balance = self.get_response(response_id)["result"][0]["amount"]
        check_that("account balance", balance,
                   equal_to(withdrawal_amount - 2 * BTC_FEE * SATOSHI_PER_BYTE))

        # lcc.set_step("Get btc_withdraws")
        # params = [["1.22.0", "1.22.1", "1.22.2", "1.22.3", "1.22.4"]]
        # response_id = self.send_request(self.get_request("get_objects", params),
        #                                 self.__database_api_identifier, debug_mode=True)
        # btc_withdraws = self.get_response(response_id, log_response=True)["result"]
        #
        # for i, withdraw in enumerate(btc_withdraws):
        #     lcc.log_info("withdraw: {}".format(params[0][i]))
        #     if check_that("'btc_withdraw'", withdraw, is_not_none()):
        #         check_that("'btc_withdraw'", withdraw, has_length(8))
        #         check_that("'account'", withdraw["account"], equal_to(self.echo_acc0))
        #         check_that("'btc address'", withdraw["btc_addr"], equal_to(btc_address))
        #         check_that("'value'", withdraw["value"], equal_to(amount))
        #         check_that("'is_approved'", withdraw["is_approved"], is_false())
        #
        # lcc.set_step("Get btc_aggregatings")
        # params = [["1.23.0", "1.23.1", "1.23.2", "1.23.3", "1.23.4", "1.23.5"]]
        # response_id = self.send_request(self.get_request("get_objects", params),
        #                                 self.__database_api_identifier, debug_mode=True)
        # btc_aggregatings = self.get_response(response_id, log_response=True)["result"]
        # for i, aggregating in enumerate(btc_aggregatings):
        #     lcc.log_info("withdraw: {}".format(params[0][i]))
        #     if check_that("'btc_aggregating'", aggregating, is_not_none()):
        #         if check_that("'btc_aggregating'", aggregating, has_length(14)):
        #             check_that("'cpfp_depth'", aggregating["cpfp_depth"], equal_to(i))
        #             check_that("'is_approved'", aggregating["is_approved"], is_false())
        #         else:
        #             check_that("'btc_aggregating'", aggregating, has_length(15))
        #             check_that("'cpfp_depth'", aggregating["cpfp_depth"], equal_to(i))
        #             # check_that("'previous_aggregation'", aggregating["previous_aggregation"], is_str())
        #             check_that("'is_approved'", aggregating["is_approved"], is_false())
        #
        # params = [self.echo_acc0, "btc"]
        # response_id = self.send_request(self.get_request("get_account_deposits", params),
        #                                 self.__database_api_identifier)
        # deposits = self.get_response(response_id, log_response=True)
        #
        # params = [self.echo_acc0, "btc"]
        # response_id = self.send_request(self.get_request("get_account_withdrawals", params),
        #                                 self.__database_api_identifier)
        # deposits = self.get_response(response_id, log_response=True)
        #
        # lcc.set_step("Get history of new account and echo_acc0 account")
        # operation_history_obj = "{}0".format(self.get_object_type(self.echo.config.object_types.OPERATION_HISTORY))
        # stop, start = operation_history_obj, operation_history_obj
        # limit = 100
        # params = [self.new_account, stop, limit, start]
        # response_id = self.send_request(self.get_request("get_account_history", params),
        # self.__history_api_identifier)
        # result = self.get_response(response_id)["result"]
        # new_acc_ids = [dict["op"][0] for dict in result]
        #
        # params = [self.echo_acc0, stop, limit, start]
        # response_id = self.send_request(self.get_request("get_account_history", params),
        # self.__history_api_identifier)
        # result = self.get_response(response_id)["result"]
        # acc0_ids = [dict["op"][0] for dict in result]
        # external_virtual_op_ids = set(new_acc_ids + acc0_ids)
        # lcc.log_info(str("Accounts operations ids: {}".format(external_virtual_op_ids)))
        #
        # lcc.set_step("Get history of committee member account")
        # params = ["1.2.6", stop, limit, start]
        # response_id = self.send_request(self.get_request("get_account_history", params),
        # self.__history_api_identifier)
        # result = self.get_response(response_id)["result"]
        # internal_ids = set([dict["op"][0] for dict in result])
        # lcc.log_info(str("Committee member account operations ids: {}".format(internal_ids)))
        #
        # lcc.set_step("Check that external and virtual operations logs separate from internal operation logs")
        # fist_sidechain_op_id = 38
        # last_sidechain_op_id = 64
        # for op_id in external_virtual_op_ids:
        #     if op_id in internal_ids and op_id < last_sidechain_op_id and op_id > fist_sidechain_op_id:
        #         raise Exception("Wrong work of method get_contract_history, get id: {}".format(op_id))
