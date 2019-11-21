   # -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc

from lemoncheesecake.matching import require_that, equal_to, greater_than, has_length, check_that_in, is_true, \
    is_list, \
    check_that, is_
from common.validation import Validator
from common.base_test import BaseTest

SUITE = {
    "description": "Operation 'sidechain_erc20_withdraw_token'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "sidechain", "sidechain_ethereum", "sidechain_erc20_withdraw_token")
@lcc.suite("Check work of method 'sidechain_erc20_withdraw_token'", rank=1)
class ERC20(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.validator = Validator()
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
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))
        self.eth_account = self.get_default_ethereum_account()
        lcc.log_info("Ethereum address in the ethereum network: '{}'".format(self.eth_account.address))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'sidechain_erc20_withdraw_token'")
    def erc20_sidechain_pre_run_scenario(self, get_random_valid_account_name, get_random_string,
                                         get_random_valid_asset_name):
        new_account = get_random_valid_account_name
        name = "erc20" + get_random_string
        symbol = get_random_valid_asset_name

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Generate ethereum address for new account")
        self.utils.perform_sidechain_eth_create_address_operation(self, new_account,
                                                                  self.__database_api_identifier)
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
        lcc.log_info(
            "ERC20 contract created in Ethereum network, address: '{}'".format(erc20_contract.address))

        lcc.set_step("Get ethereum account ERC20 tokens balance in the Ethereum network")
        in_ethereum_erc20_balance = self.eth_trx.get_balance_of(erc20_contract, self.eth_account.address)
        self.in_ethereum_start_erc20_balance = in_ethereum_erc20_balance
        require_that("'in ethereum owner's erc20 balance'", in_ethereum_erc20_balance, greater_than(0))

        lcc.set_step("Perform register erc20 token operation")
        if erc20_contract.address[:2] == "0x":
            eth_addr = erc20_contract.address[2:]
        operation = self.echo_ops.get_sidechain_erc20_register_token_operation(echo=self.echo,
                                                                               account=new_account,
                                                                               eth_addr=eth_addr,
                                                                               name=name, symbol=symbol)
        broadcast_result = self.utils.add_balance_for_operations(self, new_account, operation,
                                                                 self.__database_api_identifier)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        erc20_token_id = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        lcc.log_info("Registration of ERC20 token completed successfully, ERC20 token object is '{}'".format(
            erc20_token_id))

        response_id = self.send_request(self.get_request("get_erc20_token", [erc20_contract.address[2:]]),
                                        self.__database_api_identifier)
        erc20_contract_id = self.get_response(response_id)["result"]["contract"]

        lcc.set_step("Transfer erc20 to ethereum address of created account")
        erc20_deposit_amounts = self.get_random_amount(_to=in_ethereum_erc20_balance)
        lcc.log_info(" asdsd {}".format(erc20_deposit_amounts))
        self.eth_trx.transfer(self.web3, erc20_contract, eth_account_address, erc20_deposit_amounts)
        lcc.log_info(
            "Transfer '{}' erc20 tokens to '{}' account completed successfully".format(erc20_deposit_amounts,
                                                                                       eth_account_address))

        lcc.set_step("Get ERC20 balance in the ECHO network")
        in_echo_erc20_balance = \
            self.utils.get_erc20_token_balance_in_echo(self, account_id=new_account,
                                                       balance_of_method=self.erc20_balanceOf,
                                                       contract_id=erc20_contract_id,
                                                       database_api_id=self.__database_api_identifier)
        if in_echo_erc20_balance <= 0:
            raise Exception("No ERC20 balance to withdraw")
        lcc.log_info("ERC20 balance in ECHO network: '{}'".format(in_echo_erc20_balance))
        lcc.log_info("ERC20 balance in Ethereum network: '{}'".format(in_ethereum_erc20_balance))

        lcc.set_step("Perform first withdraw ERC20 token operation")
        erc20_withdraw_amounts = str(self.get_random_amount(_to=in_echo_erc20_balance))

        if self.eth_account.address[:2] == "0x":
            to = self.eth_account.address[2:]
        operation = self.echo_ops.get_sidechain_erc20_withdraw_token_operation(echo=self.echo,
                                                                               account=new_account,
                                                                               to=to,
                                                                               erc20_token=erc20_token_id,
                                                                               value=erc20_withdraw_amounts)

        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        withdraw_erc20_token_ids = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("Withdraw ERC20 token completed successfully, Withdraw ERC20 token object is '{}'".format(
            withdraw_erc20_token_ids))

        lcc.set_step("Get ERC20 account withdrawals")
        withdrawals = \
            self.utils.get_erc20_account_withdrawals(self, new_account, self.__database_api_identifier)["result"]
        check_that_in(
            withdrawals[0],
            "id", equal_to(withdraw_erc20_token_ids),
            "value", equal_to(str(erc20_withdraw_amounts)))
