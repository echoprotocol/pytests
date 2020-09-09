# -*- coding: utf-8 -*-
import random

from common.base_test import BaseTest

import lemoncheesecake.api as lcc

SUITE = {
    "description": "Operation 'sidechain_erc20_register_token'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "sidechain", "sidechain_erc20", "sidechain_erc20_register_token")
@lcc.suite("Check work of operation 'sidechain_erc20_register_token'", rank=1)
class ERC20(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.eth_account = None
        self.erc20_contract_code = self.get_byte_code("erc20", "code", ethereum_contract=True)
        self.erc20_abi = self.get_abi("erc20")
        self.erc20_balanceOf = self.get_byte_code("erc20", "balanceOf(address)", ethereum_contract=True)

    @staticmethod
    def get_random_amount(_to, _from=0):
        return random.randrange(_from, _to)

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
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))
        self.eth_account = self.get_default_ethereum_account()
        lcc.log_info("Ethereum address in the ethereum network: '{}'".format(self.eth_account.address))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of operation 'sidechain_erc20_register_token'")
    def erc20_sidechain_pre_run_scenario(
        self, get_random_valid_account_name, get_random_string, get_random_valid_asset_name
    ):
        new_account = get_random_valid_account_name
        name = "erc20" + get_random_string
        symbol = get_random_valid_asset_name

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(
            new_account, self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Generate ethereum address for new account")
        self.utils.perform_sidechain_eth_create_address_operation(self, new_account, self.__database_api_identifier)
        lcc.log_info("Ethereum address generated successfully")

        lcc.set_step("Get updated ethereum address of created account in the ECHO network")
        eth_account_address = self.utils.get_eth_address(self, new_account,
                                                         self.__database_api_identifier)["result"]["eth_addr"]
        lcc.log_info("Ethereum address of '{}' account is '{}'".format(new_account, eth_account_address))

        lcc.set_step("Deploy ERC20 contract in the Ethereum network")
        erc20_contract = \
            self.eth_trx.deploy_contract_in_ethereum_network(self.web3, eth_address=self.eth_account.address,
                                                             contract_abi=self.erc20_abi,
                                                             contract_bytecode=self.erc20_contract_code)
        lcc.log_info("ERC20 contract created in Ethereum network, address: '{}'".format(erc20_contract.address))

        lcc.set_step("Perform register erc20 token operation")
        if erc20_contract.address[:2] == "0x":
            eth_addr = erc20_contract.address[2:]
        operation = self.echo_ops.get_sidechain_erc20_register_token_operation(
            echo=self.echo, account=new_account, eth_addr=eth_addr, name=name, symbol=symbol
        )
        broadcast_result = self.utils.add_balance_for_operations(
            self, new_account, operation, self.__database_api_identifier
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        erc20_token_id = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        lcc.log_info(
            "Registration of ERC20 token completed successfully, ERC20 token object is '{}'".format(erc20_token_id)
        )

        lcc.set_step("Check that ERC20 has correct format")
        if not self.type_validator.is_erc20_object_id(erc20_token_id):
            lcc.log_error("Wrong format of erc20 token id, got: {}".format(erc20_token_id))
        else:
            lcc.log_info("Erc20 token has correct format.")
