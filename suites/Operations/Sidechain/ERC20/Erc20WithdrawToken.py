# -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, greater_than, equal_to, has_length, check_that_in, is_list, \
    check_that, is_true, greater_than_or_equal_to, is_bool, is_integer

from common.base_test import BaseTest

SUITE = {
    "description": "Operation 'sidechain_erc20_withdraw_token'"
}


# todo: bug ECHO-2141
@lcc.disabled
@lcc.prop("main", "type")
@lcc.tags("operations", "sidechain", "sidechain_erc20", "sidechain_erc20_withdraw_token")
@lcc.suite("Check work of operation 'sidechain_erc20_withdraw_token'", rank=1)
class GetERC20AccountWithdrawals(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.eth_account = None
        self.erc20_contract_code = self.get_byte_code("erc20", "code", ethereum_contract=True)
        self.erc20_abi = self.get_abi("erc20")
        self.erc20_balanceOf = self.get_byte_code("erc20", "balanceOf(address)", ethereum_contract=True)

    def get_random_amount(self, _to, _from=1):
        amount = random.randrange(_from, _to)
        if amount == _to:
            return self.get_random_amount(_to=_to, _from=_from)
        return amount

    def check_erc20_account_withdrawals(self, withdrawals):
        for i, withdrawal in enumerate(withdrawals):
            lcc.set_step("Check work of method 'get_erc20_account_withdrawals', withdrawal #'{}'".format(i))
            self.object_validator.validate_erc20_withdraw_object(self, withdrawal)

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_ethereum()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}',".format(self.__database_api_identifier,
                                                                            self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))
        self.eth_account = self.get_default_ethereum_account()
        lcc.log_info("Ethereum address in the ethereum network: '{}'".format(self.eth_account.address))
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of operation 'sidechain_erc20_withdraw_token'")
    def method_main_check(self, get_random_valid_account_name, get_random_string, get_random_valid_asset_name):
        new_account_name = get_random_valid_account_name
        token_name = "erc20" + get_random_string
        erc20_symbol = get_random_valid_asset_name

        lcc.set_step("Create and get new account")
        new_account_id = self.get_account_id(new_account_name, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account_id))

        lcc.set_step("Generate ethereum address for new account")
        self.utils.perform_sidechain_eth_create_address_operation(self, new_account_id, self.__database_api_identifier)
        lcc.log_info("Ethereum address generated successfully")
        self.produce_block(self.__database_api_identifier)
        lcc.set_step("Get ethereum address of created account in the ECHO network")
        eth_account_address = self.utils.get_eth_address(self, new_account_id,
                                                         self.__database_api_identifier)["result"]["eth_addr"]
        lcc.log_info("Ethereum address of '{}' account is '{}'".format(new_account_id, eth_account_address))

        lcc.set_step("Deploy ERC20 contract in the Ethereum network")
        erc20_contract = self.eth_trx.deploy_contract_in_ethereum_network(self.web3,
                                                                          eth_address=self.eth_account.address,
                                                                          contract_abi=self.erc20_abi,
                                                                          contract_bytecode=self.erc20_contract_code)
        lcc.log_info("ERC20 contract created in Ethereum network, address: '{}'".format(erc20_contract.address))

        lcc.set_step("Get ethereum ERC20 tokens balance in the Ethereum network")
        in_echo_erc20_start_balance = self.eth_trx.get_balance_of(erc20_contract, self.eth_account.address)
        require_that("'in ethereum erc20 contact balance'", in_echo_erc20_start_balance, greater_than(0))

        lcc.set_step("Perform register erc20 token operation")
        broadcast_result = \
            self.utils.perform_sidechain_erc20_register_token_operation(self, account=new_account_id,
                                                                        eth_addr=erc20_contract.address,
                                                                        name=token_name, symbol=erc20_symbol,
                                                                        database_api_id=self.__database_api_identifier)
        erc20_token_id = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        lcc.log_info("Registration of ERC20 token completed successfully, ERC20 token object is '{}'".format(
            erc20_token_id))

        lcc.set_step("Get created ERC20 token and store contract id in the ECHO network")
        response_id = self.send_request(self.get_request("get_erc20_token", [erc20_contract.address[2:]]),
                                        self.__database_api_identifier)
        erc20_contract_id = self.get_response(response_id)["result"]["contract"]
        lcc.log_info("ERC20 token has contract_id '{}'".format(erc20_contract_id))

        lcc.set_step("First transfer erc20 to ethereum address of created account")
        self.eth_trx.transfer(self.web3, erc20_contract, eth_account_address, in_echo_erc20_start_balance)
        lcc.log_info(
            "Transfer '{}' erc20 tokens to '{}' account completed successfully".format(in_echo_erc20_start_balance,
                                                                                       eth_account_address))

        lcc.set_step("Get ethereum ERC20 tokens balance after transfer in the Ethereum network")
        in_ethereum_erc20_balance_after_transfer = self.eth_trx.get_balance_of(erc20_contract,
                                                                               self.eth_account.address)
        require_that("'in ethereum erc20 contact balance after transfer'", in_ethereum_erc20_balance_after_transfer,
                     equal_to(0))
        self.produce_block(self.__database_api_identifier)
        lcc.set_step("Get ERC20 token balance of account in the ECHO network and check result")
        in_echo_erc20_balance = \
            self.utils.get_erc20_token_balance_in_echo(self, account_id=new_account_id,
                                                       balance_of_method=self.erc20_balanceOf,
                                                       contract_id=erc20_contract_id,
                                                       database_api_id=self.__database_api_identifier,
                                                       previous_balance=0)

        require_that("'in echo account's erc20 balance'", in_echo_erc20_balance, equal_to(in_echo_erc20_start_balance))

        lcc.set_step("Perform withdrawal ERC20 token operation")
        bd_result = \
            self.utils.perform_sidechain_erc20_withdraw_token_operation(self, account=new_account_id,
                                                                        to=self.eth_account.address,
                                                                        erc20_token=erc20_token_id,
                                                                        value=str(in_echo_erc20_balance),
                                                                        database_api_id=self.__database_api_identifier)
        withdrawal_erc20_token_id = self.get_operation_results_ids(bd_result)
        lcc.log_info("Withdrawal ERC20 token completed successfully, withdrawal ERC20 token object is '{}'".format(
            withdrawal_erc20_token_id))

        lcc.set_step("Get ERC20 account withdrawals")
        withdrawals = self.utils.get_erc20_account_withdrawals(self, new_account_id,
                                                               self.__database_api_identifier)["result"]
        self.check_erc20_account_withdrawals(withdrawals)

        lcc.set_step("Get ERC20 token balance of account in the ECHO network and check result")
        in_echo_erc20_balance_after_first_withdrawal = \
            self.utils.get_erc20_token_balance_in_echo(self, account_id=new_account_id,
                                                       balance_of_method=self.erc20_balanceOf,
                                                       contract_id=erc20_contract_id,
                                                       database_api_id=self.__database_api_identifier,
                                                       previous_balance=in_echo_erc20_balance)
        require_that("'in echo account's erc20 balance'", in_echo_erc20_balance_after_first_withdrawal,
                     equal_to(0))
