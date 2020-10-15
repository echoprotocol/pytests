# -*- coding: utf-8 -*-
import random
import time

from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, equal_to, greater_than, has_length, is_true, require_that

SUITE = {
    "description": "Method 'get_erc20_account_deposits'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_sidechain_erc20", "wallet_get_erc20_account_deposits")
@lcc.suite("Check work of method 'get_erc20_account_deposits'", rank=1)
class GetErc20AccountDeposits(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
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

    def check_erc20_account_deposits(self, deposits, account_id, erc20_deposit_amounts, erc20_contract_address):
        require_that("'account deposits count'", deposits, has_length(len(erc20_deposit_amounts)), quiet=True)

        for i, erc20_account_deposit in enumerate(deposits):
            lcc.set_step("Check work of method 'get_erc20_account_deposits', deposit #'{}'".format(i))
            self.object_validator.validate_erc20_deposit_object(self, erc20_account_deposit)
            check_that_in(
                erc20_account_deposit,
                "account",
                equal_to(account_id),
                "erc20_addr",
                equal_to(erc20_contract_address[2:]),
                "value",
                equal_to(str(erc20_deposit_amounts[i])),
                "is_approved",
                is_true(),
                quiet=True
            )

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_ethereum()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(
                self.__database_api_identifier,
                self.__registration_api_identifier,
            )
        )
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))
        self.eth_account = self.get_default_ethereum_account()
        lcc.log_info("Ethereum address in the ethereum network: '{}'".format(self.eth_account.address))
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_get_erc20_account_deposits'")
    def method_main_check(self, get_random_valid_account_name, get_random_string, get_random_valid_asset_name):
        new_account_name = get_random_valid_account_name
        token_name = "erc20" + get_random_string
        erc20_symbol = get_random_valid_asset_name
        erc20_deposit_amounts = []

        lcc.set_step("Create and get new account")
        new_account_id = self.get_account_id(
            new_account_name, self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account_id))

        lcc.set_step("Generate ethereum address for new account")
        self.utils.perform_sidechain_eth_create_address_operation(self, new_account_id, self.__database_api_identifier)
        lcc.log_info("Ethereum address generated successfully")

        lcc.set_step("Get ethereum address of created account in the ECHO network")
        eth_account_address = self.utils.get_eth_address(self, new_account_id,
                                                         self.__database_api_identifier)["result"]["eth_addr"]
        lcc.log_info("Ethereum address of '{}' account is '{}'".format(new_account_id, eth_account_address))

        lcc.set_step("Deploy ERC20 contract in the Ethereum network")
        erc20_contract = self.eth_trx.deploy_contract_in_ethereum_network(
            self.web3,
            eth_address=self.eth_account.address,
            contract_abi=self.erc20_abi,
            contract_bytecode=self.erc20_contract_code
        )
        lcc.log_info("ERC20 contract created in Ethereum network, address: '{}'".format(erc20_contract.address))

        lcc.set_step("Get ethereum ERC20 tokens balance in the Ethereum network")
        in_ethereum_start_erc20_balance = self.eth_trx.get_balance_of(erc20_contract, self.eth_account.address)
        require_that("'in ethereum erc20 contact balance'", in_ethereum_start_erc20_balance, greater_than(0))

        lcc.set_step("Perform register erc20 token operation")
        self.utils.perform_sidechain_erc20_register_token_operation(
            self,
            account=new_account_id,
            eth_addr=erc20_contract.address,
            name=token_name,
            symbol=erc20_symbol,
            database_api_id=self.__database_api_identifier
        )
        lcc.log_info("Registration of ERC20 token completed successfully")

        lcc.set_step("Get created ERC20 token and store contract id in the ECHO network")
        response_id = self.send_request(
            self.get_request("get_erc20_token", [erc20_contract.address[2:]]), self.__database_api_identifier
        )
        erc20_contract_id = self.get_response(response_id)["result"]["contract"]
        lcc.log_info("ERC20 token has contract_id '{}'".format(erc20_contract_id))

        lcc.set_step("First transfer erc20 to ethereum address of created account")
        erc20_deposit_amounts.append(self.get_random_amount(_to=in_ethereum_start_erc20_balance))
        self.eth_trx.transfer(self.web3, erc20_contract, eth_account_address, erc20_deposit_amounts[0])
        lcc.log_info(
            "Transfer '{}' erc20 tokens to '{}' account completed successfully".format(
                erc20_deposit_amounts[0], eth_account_address
            )
        )

        lcc.set_step("Check method get_erc20_account_withdrawals")
        time.sleep(5)
        account_deposits = self.send_wallet_request(
            "get_erc20_account_deposits", [new_account_id], log_response=False
        )['result']
        self.check_erc20_account_deposits(
            account_deposits, new_account_id, erc20_deposit_amounts, erc20_contract.address
        )