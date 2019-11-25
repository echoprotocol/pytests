# -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Operation 'sidechain_eth_withdraw'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "sidechain", "sidechain_ethereum", "sidechain_eth_withdraw")
@lcc.suite("Check work of operation 'sidechain_eth_withdraw'", rank=1)
class SidechainEthWithdraw(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.eth_address = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_ethereum()
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

        self.eth_address = self.get_default_ethereum_account().address
        lcc.log_info("Ethereum address in the ethereum network: '{}'".format(self.eth_address))

    @staticmethod
    def get_random_amount(_from=None, _to=None, amount_type=None):
        if amount_type == float:
            if (_from and _to) is None:
                _from, _to = 0.01, 0.1
            return random.uniform(_from, _to)
        if amount_type == int:
            if _from is None:
                _from = 1
            return random.randrange(_from, _to)
        return random.randrange(_from, _to)

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of operation 'sidechain_eth_withdraw'")
    def SidechainEthApproveAddress(self, get_random_valid_account_name):

        new_account = get_random_valid_account_name

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Generate ethereum address for new account")
        operation = self.echo_ops.get_sidechain_eth_create_address_operation(echo=self.echo,
                                                                             account=new_account)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("Ethereum address generated successfully")

        lcc.set_step("Get ethereum address of created account in the network")
        eth_account_address = self.utils.get_eth_address(self, new_account,
                                                         self.__database_api_identifier)["result"]["eth_addr"]
        lcc.log_info("Created ethereum address: {}".format(eth_account_address))
        eth_amount = self.get_random_amount(amount_type=float)

        lcc.set_step("Send eth to ethereum address of created account")
        transaction = self.eth_trx.get_transfer_transaction(web3=self.web3, _from=self.eth_address,
                                                            _to=eth_account_address,
                                                            value=eth_amount)
        self.eth_trx.broadcast(web3=self.web3, transaction=transaction)

        lcc.set_step("Get account balance in ethereum")
        ethereum_balance = self.utils.get_eth_balance(self, new_account, self.__database_api_identifier)
        lcc.log_info("Account '{}' balance in ethereum is '{}'".format(new_account, ethereum_balance))

        lcc.set_step("Transfer eth from account to recipient")
        transfer_amount = self.get_random_amount(_to=ethereum_balance, amount_type=int)
        self.utils.perform_transfer_operations(self, new_account, self.echo_acc0, self.__database_api_identifier,
                                               transfer_amount=transfer_amount, amount_asset_id=self.eth_asset)
        lcc.log_info(
            "Transfer operation performed, transfer amount: '{}' '{}' assets".format(transfer_amount, self.eth_asset))

        lcc.set_step("Get recipient balance in ethereum after transfer")
        recipient_balance_after_transfer = self.utils.get_eth_balance(self, self.echo_acc0,
                                                                      self.__database_api_identifier,
                                                                      ethereum_balance)
        lcc.log_info("Recipient '{}' balance after "
                     "transfer in ethereum is '{}'".format(self.echo_acc0, recipient_balance_after_transfer))

        lcc.set_step("Withdraw eth from ECHO network to Ethereum network")
        withdraw_amount = self.get_random_amount(_to=recipient_balance_after_transfer, amount_type=int)
        lcc.log_info("Withdrawing '{}' eeth from '{}' account".format(withdraw_amount, self.echo_acc0))

        lcc.set_step("Withdraw eth to ethereum address")
        if self.eth_address[:2] == "0x":
            eth_addr = self.eth_address[2:]
        operation = self.echo_ops.get_sidechain_eth_withdraw_operation(echo=self.echo, account=self.echo_acc0,
                                                                       eth_addr=eth_addr, value=withdraw_amount)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get balance after withdraw and check that withdraw operation broadcasted successfully")
        recipient_balance_after_withdraw = self.utils.get_eth_balance(self, self.echo_acc0,
                                                                      self.__database_api_identifier,
                                                                      ethereum_balance)
        check_that("eth balance", recipient_balance_after_withdraw,
                   equal_to(recipient_balance_after_transfer - withdraw_amount))
