# -*- coding: utf-8 -*-
from __future__ import print_function

import json
import time

from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import BITCOIN_URL, BTC_FEE, BTC_WITHDRAWAL_MIN, INIT4_PK, INIT5_PK

import lemoncheesecake.api as lcc
import requests
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'withdraw_btc'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_sidechain_bitcoin", "wallet_withdraw_btc")
@lcc.suite("Check work of method 'withdraw_btc'", rank=1)
class WithdrawBtc(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.init5 = None
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
        self.init5 = self.get_account_id('init5', self.__database_api_identifier, self.__registration_api_identifier)
        self.init4 = self.get_account_id('init4', self.__database_api_identifier, self.__registration_api_identifier)
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

    @lcc.depends_on("API.Wallet.SidechainBitcoin.CreateBtcAddress.CreateBtcAddress.method_main_check")
    @lcc.test("Simple work of method 'wallet_withdraw_btc'")
    def method_main_check(self, get_random_integer):
        withdrawal_amount = BTC_WITHDRAWAL_MIN * BTC_FEE

        btc_address = self.send_wallet_request("get_btc_address", [self.init4], log_response=False)['result']
        if btc_address is None:
            lcc.log_error("Account {} has no btc address, method does not checked".format(self.init4))
        else:
            self.unlock_wallet()
            lcc.set_step("Import key")
            self.send_wallet_request("import_key", ['init4', INIT4_PK], log_response=False)
            self.send_wallet_request("import_key", ['init5', INIT5_PK], log_response=False)
            lcc.log_info("Key imported")

            lcc.set_step("Create new address in BTC network")
            new_address = self.btc_call('getnewaddress')

            # generate 101 block by new address
            self.btc_call('generatetoaddress', 101, new_address)

            # send 10 btc coins to new address
            self.btc_call('sendtoaddress', btc_address['deposit_address']['address'], 10.00)
            for i in range(0, 5):
                time.sleep(3)
                self.btc_call('generate', 1)

            lcc.set_step("Check withdraw_btc method")
            result = self.send_wallet_request(
                "withdraw_btc", [self.init4, btc_address['deposit_address']['address'], withdrawal_amount, True],
                log_response=False
            )['result']
            for i in range(0, 5):
                time.sleep(3)
                self.btc_call('generate', 1)
            lcc.log_info("Check that account has withdrawals")
            result = self.send_wallet_request("get_account_withdrawals", [self.init4, ""], log_response=True)['result']
            check_that("account id", result[-1]['account'], equal_to(self.init4))
            check_that("btc_addr", result[-1]['btc_addr'], equal_to(btc_address['deposit_address']['address']))
