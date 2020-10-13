# -*- coding: utf-8 -*-
from __future__ import print_function

import json
import time

from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import BITCOIN_URL, BTC_FEE, BTC_WITHDRAWAL_MIN, INIT1_PK, INIT5_PK

import lemoncheesecake.api as lcc
import requests
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'get_account_withdrawals'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_sidechain", "wallet_get_account_withdrawals")
@lcc.suite("Check work of method 'get_account_withdrawals'", rank=1)
class GetAccountWithdrawals(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.init5 = None
        self.echo_acc0 = None
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
        self.init5 = self.get_account_id('init5', self.__database_api_identifier, self.__registration_api_identifier)
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo account is '{}'".format(self.init5))

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

    @lcc.depends_on("API.Wallet.Sidechain.GetAccountDeposits.GetAccountDeposits.method_main_check")
    @lcc.test("Simple work of method 'wallet_get_account_withdrawals'")
    def method_main_check(self, get_random_integer):
        lcc.set_step("Get account withdrawals")
        result = self.send_wallet_request("get_account_withdrawals", [self.init5, ""], log_response=True)['result']

        if result == []:
            lcc.log_info("There no withdrawals of account, performing withdrawal operation")
            backup_address = 'mipcBbFg9gMiCh81Kj8tqqdgoZub1ZJRfn'
            withdrawal_amount = BTC_WITHDRAWAL_MIN * BTC_FEE

            lcc.log_info("Perform sidechain_btc_create_address_operation for '1.2.7' account")
            operation = self.echo_ops.get_sidechain_btc_create_address_operation(
                echo=self.echo, account="1.2.7", backup_address=backup_address, signer=INIT1_PK
            )
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            operation_result = \
                self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)["trx"]["operation_results"][0][
                    1]
            lcc.log_info("Operation result id: {}".format(operation_result))

            lcc.log_info("Get btc address of '1.2.7' account")
            response_id = self.send_request(
                self.get_request("get_objects", [[operation_result]]), self.__database_api_identifier
            )
            new_btc_address = self.get_response(response_id)["result"][0]["deposit_address"]["address"]
            lcc.log_info("'1.2.7' account BTC address is '{}'".format(new_btc_address))

            lcc.log_info("Perform sidechain_btc_withdraw_operation")
            operation = self.echo_ops.get_sidechain_btc_withdraw_operation(
                echo=self.echo,
                account=self.init5,
                btc_address=new_btc_address,
                value=withdrawal_amount,
                fee_asset_id=self.btc_asset,
                signer=INIT5_PK
            )
            collected_operation = self.collect_operations(
                operation, self.__database_api_identifier, fee_asset_id=self.btc_asset
            )
            self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=True)

            # generate blocks for aggregation in sidechain
            for i in range(0, 5):
                time.sleep(3)
                self.btc_call('generate', 1)

            lcc.set_step("Get account withdrawals")
            result = self.send_wallet_request("get_account_withdrawals", [self.init5, ""], log_response=True)['result']
        check_that("account id", result[-1]['account'], equal_to(self.init5))
