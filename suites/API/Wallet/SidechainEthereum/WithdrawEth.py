# -*- coding: utf-8 -*-
import random

from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import INIT5_PK, MIN_ETH_WITHDRAW

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'withdraw_eth'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_sidechain_ethereum", "wallet_withdraw_eth")
@lcc.suite("Check work of method 'withdraw_eth'", rank=1)
class WithdrawEth(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.init4 = None

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
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        self.init5 = self.get_account_id('init5', self.__database_api_identifier, self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.init5))

        self.eth_address = self.get_default_ethereum_account().address
        lcc.log_info("Ethereum address in the ethereum network: '{}'".format(self.eth_address))

    @staticmethod
    def get_random_amount(_from=None, _to=None, amount_type=None):
        if amount_type == float:
            if (_from and _to) is None:
                _from, _to = MIN_ETH_WITHDRAW, MIN_ETH_WITHDRAW + 0.1
            return random.uniform(_from, _to)
        if amount_type == int:
            if _from is None:
                _from = 1
            return random.randrange(_from, _to)
        return random.randrange(_from, _to)

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_withdraw_eth'")
    def method_main_check(self):
        self.unlock_wallet()
        self.import_key('init5')

        result = self.send_wallet_request('create_eth_address', [self.init5, True], log_response=False)['result']
        eth_address_object = self.utils.get_eth_address(self, self.init5,
                                                        self.__database_api_identifier)["result"]['eth_addr']
        lcc.log_info("{}".format(eth_address_object))
        lcc.set_step("Check get_eth_address method")
        eth_account_address = self.send_wallet_request(
            'get_eth_address', [self.init5], log_response=False
        )['result']['eth_addr']

        eth_amount = self.get_random_amount(amount_type=float)
        lcc.set_step("Send eth to ethereum address of created account")
        transaction = self.eth_trx.get_transfer_transaction(
            web3=self.web3, _from=self.eth_address, _to=eth_account_address, value=eth_amount
        )
        self.eth_trx.broadcast(web3=self.web3, transaction=transaction)

        lcc.set_step("Get account balance in ethereum")
        ethereum_balance = self.utils.get_eth_balance(self, self.init5, self.__database_api_identifier)
        lcc.log_info("Account '{}' balance in ethereum is '{}'".format(self.init5, ethereum_balance))

        lcc.set_step("Transfer eth from account to recipient")
        transfer_amount = self.get_random_amount(_from=MIN_ETH_WITHDRAW, _to=int(ethereum_balance), amount_type=int)
        self.utils.perform_transfer_operations(
            self,
            self.init5,
            self.echo_acc0,
            self.__database_api_identifier,
            transfer_amount=transfer_amount,
            amount_asset_id=self.eth_asset,
            signer=INIT5_PK
        )
        lcc.log_info(
            "Transfer operation performed, transfer amount: '{}' '{}' assets".format(transfer_amount, self.eth_asset)
        )
        result = self.send_wallet_request(
            "withdraw_eth", [self.init5, eth_account_address, transfer_amount, True], log_response=False
        )['result']
        check_that("withdraw eth amount", int(result['operations'][0][1]["value"]), equal_to(int(transfer_amount)))
        check_that("eth address", result['operations'][0][1]['eth_addr'], equal_to(eth_account_address))
