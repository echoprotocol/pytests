# -*- coding: utf-8 -*-

from __future__ import print_function

import json
import time

from common.base_test import BaseTest
from project import BITCOIN_URL, BTC_FEE, BTC_WITHDRAWAL_MIN, INIT0_PK, SATOSHI_PER_BYTE, SATOSHI_PRECISION

import lemoncheesecake.api as lcc
import requests
from lemoncheesecake.matching import (
    check_that, check_that_in, equal_to, has_length, is_bool, is_dict, is_integer, is_list, require_that
)

SUITE = {
    "description": "Entering the currency bitcoin in the network ECHO to the account and withdraw that currency"
}


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
            "API identifiers are: database='{}', registration='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier
            )
        )
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

        search_pattern = '://'
        split_index = BITCOIN_URL.find(search_pattern) + len(search_pattern)
        rpc_user = 'test'
        rpc_password = 'test'
        self.btc_url = '{}{}:{}@{}'.format(BITCOIN_URL[:split_index], rpc_user, rpc_password, BITCOIN_URL[split_index:])
        self._session = requests.Session()
        self._headers = {
            'content-type': 'application/json'
        }

    def btc_call(self, rpcMethod, *params):
        payload = json.dumps({
            "method": rpcMethod,
            "params": list(params),
            "jsonrpc": "2.0"
        })
        tries = 5
        hadConnectionFailures = False
        while True:
            try:
                response = self._session.post(self.btc_url, headers=self._headers, data=payload)
            except requests.exceptions.ConnectionError:
                tries -= 1
                if tries == 0:
                    raise Exception('Failed to connect for remote procedure call.')
                print(
                    "Couldn't connect for remote procedure call, will sleep for five seconds and then try again ({} "
                    "more tries)".format(tries)
                )
                time.sleep(10)
            else:
                if hadConnectionFailures:
                    print('Connected for remote procedure call after retry.')
                break
        if response.status_code not in range(200, 500):
            raise Exception('RPC connection failure: ' + str(response.status_code) + ' ' + response.reason)
        responseJSON = response.json()
        if 'error' in responseJSON and responseJSON['error'] is not None:
            raise Exception('Error in RPC call: ' + str(responseJSON['error']))
        return responseJSON['result']

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("The scenario checks the main parts before testing the bitcoin sidechain functionality")
    def bitcoin_sidechain_pre_run_scenario(self):
        backup_address = 'mipcBbFg9gMiCh81Kj8tqqdgoZub1ZJRfn'
        deposit_amount = 5
        withdrawal_amount = BTC_WITHDRAWAL_MIN * BTC_FEE
        withdraw_values = []
        deposit_values = []

        lcc.set_step("Create new address in BTC network")
        new_address = self.btc_call('getnewaddress')

        # generate 101 block by new address
        self.btc_call('generatetoaddress', 101, new_address)

        # send 10 btc coins to new address
        self.btc_call('sendtoaddress', new_address, 10.00)

        # generate blocks for aggregation in sidechain
        for i in range(0, 5):
            time.sleep(3)
            self.btc_call('generate', 1)

        # get new address balance in BTC network
        balance = self.btc_call('getreceivedbyaddress', new_address)
        require_that("'btc network balance'", balance, equal_to(10))

        lcc.log_info("Perform sidechain_btc_create_address_operation for account {}".format(self.echo_acc0))
        operation = self.echo_ops.get_sidechain_btc_create_address_operation(
            echo=self.echo, account=self.echo_acc0, backup_address=backup_address
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        operation_result = \
            self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)["trx"]["operation_results"][0][
                1]
        lcc.log_info("Operation result id: {}".format(operation_result))

        lcc.set_step("Get btc address of {} account".format(self.echo_acc0))
        response_id = self.send_request(
            self.get_request("get_objects", [[operation_result]]), self.__database_api_identifier
        )
        address = self.get_response(response_id)["result"][0]["deposit_address"]["address"]
        lcc.log_info("'{}' account BTC address is '{}'".format(self.echo_acc0, address))

        lcc.set_step("Get {} account btc asset balance".format(self.echo_acc0))
        params = [self.echo_acc0, ["1.3.2"]]
        response_id = self.send_request(
            self.get_request("get_account_balances", params), self.__database_api_identifier
        )
        balance_before_deposit = self.get_response(response_id)["result"][0]["amount"]
        lcc.log_info("'{}' account btc balance = {}".format(self.echo_acc0, balance_before_deposit))

        # transfer 5 btc coins from btc network to echo network
        self.btc_call('sendtoaddress', address, deposit_amount)

        # generate blocks for aggregation in sidechain
        for i in range(0, 5):
            time.sleep(3)
            self.btc_call('generate', 1)

        lcc.log_info("Get {} account btc asset balance".format(self.echo_acc0))
        params = [self.echo_acc0, ["1.3.2"]]
        response_id = self.send_request(
            self.get_request("get_account_balances", params), self.__database_api_identifier
        )
        balance_after_deposit = self.get_response(response_id)["result"][0]["amount"]
        deposit_values.append(balance_after_deposit)
        check_that(
            "account balance", balance_after_deposit,
            equal_to(balance_before_deposit + deposit_amount * SATOSHI_PRECISION - SATOSHI_PER_BYTE * BTC_FEE)
        )

        lcc.log_info("Perform sidechain_btc_create_address_operation for '1.2.6' account")
        operation = self.echo_ops.get_sidechain_btc_create_address_operation(
            echo=self.echo, account="1.2.6", backup_address=backup_address, signer=INIT0_PK
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        operation_result = \
            self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)["trx"]["operation_results"][0][
                1]
        lcc.log_info("Operation result id: {}".format(operation_result))

        lcc.log_info("Get btc address of '1.2.6' account")
        response_id = self.send_request(
            self.get_request("get_objects", [[operation_result]]), self.__database_api_identifier
        )
        new_btc_address = self.get_response(response_id)["result"][0]["deposit_address"]["address"]
        lcc.log_info("'1.2.6' account BTC address is '{}'".format(new_btc_address))

        lcc.log_info("Perform sidechain_btc_withdraw_operation")
        operation = self.echo_ops.get_sidechain_btc_withdraw_operation(
            echo=self.echo,
            account=self.echo_acc0,
            btc_address=new_btc_address,
            value=withdrawal_amount,
            fee_asset_id=self.btc_asset
        )
        collected_operation = self.collect_operations(
            operation, self.__database_api_identifier, fee_asset_id=self.btc_asset
        )
        withdraw_values.append(withdrawal_amount)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=True)

        # generate blocks for aggregation in sidechain
        for i in range(0, 5):
            time.sleep(3)
            self.btc_call('generate', 1)

        lcc.set_step("Get {} account btc asset balance".format(self.echo_acc0))
        params = [self.echo_acc0, ["1.3.2"]]
        response_id = self.send_request(
            self.get_request("get_account_balances", params), self.__database_api_identifier
        )
        balance_after_withdrawal = self.get_response(response_id)["result"][0]["amount"]
        check_that("account balance", balance_after_withdrawal, equal_to(balance_after_deposit - withdrawal_amount))

        lcc.set_step("Get '1.2.6' account btc asset balance")
        params = ["1.2.6", ["1.3.2"]]
        response_id = self.send_request(
            self.get_request("get_account_balances", params), self.__database_api_identifier
        )
        balance = self.get_response(response_id)["result"][0]["amount"]
        check_that("account balance", balance, equal_to(withdrawal_amount - 2 * BTC_FEE * SATOSHI_PER_BYTE))

        lcc.set_step("Get btc deposits of account {}".format(self.echo_acc0))
        params = [self.echo_acc0, "btc"]
        response_id = self.send_request(
            self.get_request("get_account_deposits", params), self.__database_api_identifier
        )
        get_account_deposits_results = self.get_response(response_id)["result"]
        for i, deposit in enumerate(get_account_deposits_results):
            if check_that("'deposit btc'", deposit, has_length(8), quiet=True):
                if not self.type_validator.is_btc_deposit_id(deposit["id"]):
                    lcc.log_error("Wrong format of 'id', got: {}".format(deposit["id"]))
                else:
                    lcc.log_info("'id' has correct format: deposit_btc_object_type")
                if not self.type_validator.is_account_id(deposit["account"]):
                    lcc.log_error("Wrong format of 'account', got: {}".format(deposit["account"]))
                else:
                    lcc.log_info("'account' has correct format: account_id")
                if not self.type_validator.is_btc_intermediate_deposit_id(deposit["intermediate_deposit_id"]):
                    lcc.log_error(
                        "Wrong format of 'intermediate_deposit_id', got: {}".format(deposit["intermediate_deposit_id"])
                    )
                else:
                    lcc.log_info("'intermediate_deposit_id' has correct format: intermediate_deposit_id_object")
                check_that_in(
                    deposit,
                    "is_approved",
                    is_bool(),
                    "is_sent",
                    is_bool(),
                    "approves",
                    is_list(),
                    "extensions",
                    is_list(),
                    quiet=True
                )
                tx_info = deposit["tx_info"]
                if check_that("'deposit btc'", tx_info, is_dict(), quiet=True):
                    check_that_in(tx_info, "block_number", is_integer(), quiet=True)
                    if check_that("'deposit btc'", tx_info["out"], is_dict(), quiet=True):
                        check_that_in(tx_info["out"], "index", is_integer(), "amount", is_integer(), quiet=True)
                        if not self.type_validator.is_hex(tx_info["out"]["tx_id"]):
                            lcc.log_error("Wrong format of 'tx_id', got: {}".format(tx_info["out"]["tx_id"]))
                        else:
                            lcc.log_info("'tx_id' has correct format: hex")

        lcc.set_step("Get btc withdrawals of account {}".format(self.echo_acc0))
        params = ["1.2.12", "btc"]
        response_id = self.send_request(
            self.get_request("get_account_withdrawals", params), self.__database_api_identifier
        )
        get_account_withdrawals_results = self.get_response(response_id)["result"]
        for i, withdraw in enumerate(get_account_withdrawals_results):
            if check_that("'withdraw btc'", withdraw, has_length(9), quiet=True):
                if not self.type_validator.is_btc_withdraw_id(withdraw["id"]):
                    lcc.log_error("Wrong format of 'id', got: {}".format(withdraw["id"]))
                else:
                    lcc.log_info("'id' has correct format: withdraw_btc_object_type")
                if not self.type_validator.is_account_id(withdraw["account"]):
                    lcc.log_error("Wrong format of 'account', got: {}".format(withdraw["account"]))
                else:
                    lcc.log_info("'account' has correct format: account_id")
                if not self.type_validator.is_btc_address(withdraw["btc_addr"]):
                    lcc.log_error("Wrong format of 'btc_address', got: {}".format(withdraw["btc_addr"]))
                else:
                    lcc.log_info("'btc_address' has correct format: btc_address")
                if not self.type_validator.is_SHA3_256(withdraw["transaction_id"]):
                    lcc.log_error("Wrong format of 'transaction_id', got: {}".format(withdraw["transaction_id"]))
                else:
                    lcc.log_info("'transaction_id' has correct format: hex")

                check_that_in(
                    withdraw,
                    "is_approved",
                    is_bool(),
                    "is_sent",
                    is_bool(),
                    "value",
                    equal_to(withdrawal_amount),
                    "echo_block_number",
                    is_integer(),
                    "extensions",
                    is_list(),
                    quiet=True
                )
