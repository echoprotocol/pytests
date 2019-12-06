# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Operation 'sidechain_eth_create_address'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "sidechain", "sidechain_ethereum", "sidechain_eth_create_address")
@lcc.suite("Check work of operation 'sidechain_eth_create_address'", rank=1)
class EthCreateAddress(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of operation 'sidechain_eth_create_address'")
    def sidechain_eth_create_address_operation(self, get_random_valid_account_name):

        new_account = get_random_valid_account_name

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get account balance in ethereum of new account")
        ethereum_balance = self.utils.get_account_balances(self, new_account, self.__database_api_identifier,
                                                           self.eth_asset)["amount"]
        check_that("'balance in ethereum'", ethereum_balance, equal_to(0))

        lcc.set_step("Generate ethereum address for new account")
        operation = self.echo_ops.get_sidechain_eth_create_address_operation(echo=self.echo,
                                                                             account=new_account)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("Ethereum address generated successfully")

        lcc.set_step("Get ethereum address of created account in the network")
        eth_account_address = self.utils.get_eth_address(self, new_account,
                                                         self.__database_api_identifier)["result"]["eth_addr"]
        lcc.log_info("Ethereum address of '{}' account is '{}'".format(new_account, eth_account_address))

        if not self.type_validator.is_eth_address(eth_account_address):
            lcc.log_info("Wrong format of eth address, got: {}".format(eth_account_address))
        else:
            lcc.log_info("Eth address has correct format.")
