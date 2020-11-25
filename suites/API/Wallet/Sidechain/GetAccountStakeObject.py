# -*- coding: utf-8 -*-
import json
import time

from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import BITCOIN_URL

import lemoncheesecake.api as lcc
import requests
from lemoncheesecake.matching import check_that, check_that_in, equal_to, is_bool, is_dict, is_integer, is_list

SUITE = {
    "description": "Method 'get_account_stake_objects'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_sidechain_bitcoin", "wallet_get_account_stake_objects")
@lcc.suite("Check work of method 'get_account_stake_objects'", rank=1)
class GetAccountStakeObjects(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.init4 = None
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
        self.init4 = self.get_account_id('init4', self.__database_api_identifier, self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.init4))
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

    @lcc.test("Simple work of method 'wallet_get_account_stake_objects'")
    def method_main_check(self, get_random_btc_public_key):

        self.unlock_wallet()
        self.import_key('init4')
        lcc.set_step("Get btc stake address")
        result = self.send_wallet_request("get_btc_stake_address", [self.init4], log_response=False)['result']
        if result is None:
            btc_public_key = get_random_btc_public_key
            result = self.send_wallet_request(
                "create_btc_stake_address", [self.init4, btc_public_key, True], log_response=False
            )['result']

            result = self.send_wallet_request("get_btc_stake_address", [self.init4], log_response=False)['result']

            if self.type_validator.is_btc_address(result['address']):
                lcc.log_info("New btc_stake_address created!")
            else:
                lcc.log_info("Wrong btc_stake_address format")

        new_address = result['address']
        lcc.log_info("Btc stake address: '{}'".format(new_address))
        self.produce_block(self.__database_api_identifier)
        # generate 101 block by new address
        self.btc_call('generatetoaddress', 101, new_address)
        time.sleep(3)
        # generate blocks for aggregation in sidechain
        for i in range(0, 5):
            time.sleep(3)
            self.btc_call('generate', 1)

        result = self.send_wallet_request(
            "get_account_stake_objects", [self.init4, "sbtc"], log_response=False
        )['result'][-1]

        if self.type_validator.is_account_stake_objects_id(result['id']):
            lcc.log_info("Correct format of `account_stake_object_id`, got: {}".format(result['id']))
        else:
            lcc.log_info("Wrong format of `account_stake_object_id`, got: {}".format(result['id']))

        check_that("account", result['account'], equal_to(self.init4))

        check_that("out", result['out'], is_dict())

        if self.type_validator.is_hex(result['out']['tx_id']):
            lcc.log_info("Correct format of `tx_id`, got: {}".format(result['out']['tx_id']))
        else:
            lcc.log_info("Wrong format of `tx_id`, got: {}".format(result['out']['tx_id']))
        check_that("index", result["out"]["index"], is_integer(), quiet=True)
        check_that("amount", int(result["out"]["amount"]), is_integer(), quiet=True)
        check_that_in(
            result,
            "vout_block_number",
            is_integer(),
            "vin_block_number",
            is_integer(),
            "approves_for_vout",
            is_list(),
            "is_vout_approved",
            is_bool(),
            "approves_for_vin",
            is_list(),
            "is_vin_approved",
            is_bool(),
            "extensions",
            is_list(),
            quiet=True
        )
