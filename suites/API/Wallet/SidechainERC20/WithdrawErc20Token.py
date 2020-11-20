# -*- coding: utf-8 -*-
import random
import time

from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import INIT4_PK

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, equal_to, greater_than, is_true, require_that

SUITE = {
    "description": "Method 'withdraw_erc20_token'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_sidechain_erc20", "wallet_withdraw_erc20_token")
@lcc.suite("Check work of method 'withdraw_erc20_token'", rank=1)
class GetErc20AccountDeposits(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.init4 = None
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

    def check_erc20_account_withdrawals(self, withdrawals, account_id, erc20_withdrawal_amounts):
        for i, erc20_account_withdraw in enumerate(withdrawals):
            lcc.set_step("Check work of method 'get_erc20_account_withdrawals', withdrawal #'{}'".format(i))
            self.object_validator.validate_erc20_withdraw_object(self, erc20_account_withdraw)
            check_that_in(
                erc20_account_withdraw,
                "account",
                equal_to(account_id),
                "is_approved",
                is_true(),
                "value",
                equal_to(str(erc20_withdrawal_amounts)),
                quiet=False
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
        self.init4 = self.get_account_id('init4', self.__database_api_identifier, self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))
        self.eth_account = self.get_default_ethereum_account()
        lcc.log_info("Ethereum address in the ethereum network: '{}'".format(self.eth_account.address))
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_withdraw_erc20_token'")
    def method_main_check(self, get_random_valid_account_name, get_random_string, get_random_valid_asset_name):
        token_name = "erc20" + get_random_string
        erc20_symbol = get_random_valid_asset_name

        self.unlock_wallet()
        self.import_key('init4')

        try:
            lcc.set_step("Get ethereum address of created account in the ECHO network")
            eth_account_address = self.utils.get_eth_address(self, self.init4,
                                                             self.__database_api_identifier)["result"]["eth_addr"]
            lcc.log_info("Ethereum address of '{}' account is '{}'".format(self.init4, eth_account_address))
        except Exception:
            lcc.set_step("Generate ethereum address for new account")
            self.utils.perform_sidechain_eth_create_address_operation(
                self, self.init4, self.__database_api_identifier, signer=INIT4_PK
            )
            lcc.log_info("Ethereum address generated successfully")
            eth_account_address = self.utils.get_eth_address(self, self.init4,
                                                             self.__database_api_identifier)["result"]["eth_addr"]
            lcc.log_info("Ethereum address of '{}' account is '{}'".format(self.init4, eth_account_address))

        lcc.set_step("Deploy ERC20 contract in the Ethereum network")
        erc20_contract = self.eth_trx.deploy_contract_in_ethereum_network(
            self.web3,
            eth_address=self.eth_account.address,
            contract_abi=self.erc20_abi,
            contract_bytecode=self.erc20_contract_code
        )
        lcc.log_info("ERC20 contract created in Ethereum network, address: '{}'".format(erc20_contract.address))

        lcc.set_step("Get ethereum ERC20 tokens balance in the Ethereum network")
        in_echo_erc20_start_balance = self.eth_trx.get_balance_of(erc20_contract, self.eth_account.address)
        require_that("'in ethereum erc20 contact balance'", in_echo_erc20_start_balance, greater_than(0), quiet=True)

        lcc.set_step("Perform register erc20 token operation")
        broadcast_result = \
            self.utils.perform_sidechain_erc20_register_token_operation(
                self,
                account=self.init4,
                eth_addr=erc20_contract.address,
                name=token_name, symbol=erc20_symbol,
                database_api_id=self.__database_api_identifier,
                signer=INIT4_PK
            )
        erc20_token_id = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        lcc.log_info(
            "Registration of ERC20 token completed successfully, ERC20 token object is '{}'".format(erc20_token_id)
        )

        lcc.set_step("Get created ERC20 token and store contract id in the ECHO network")
        response_id = self.send_request(
            self.get_request("get_erc20_token", [erc20_contract.address[2:]]), self.__database_api_identifier
        )
        erc20_contract_id = self.get_response(response_id)["result"]["contract"]
        lcc.log_info("ERC20 token has contract_id '{}'".format(erc20_contract_id))

        lcc.set_step("First transfer erc20 to ethereum address of created account")
        self.eth_trx.transfer(self.web3, erc20_contract, eth_account_address, in_echo_erc20_start_balance)
        lcc.log_info(
            "Transfer '{}' erc20 tokens to '{}' account completed successfully".format(
                in_echo_erc20_start_balance, eth_account_address
            )
        )

        lcc.set_step("Get ethereum ERC20 tokens balance after transfer in the Ethereum network")
        in_ethereum_erc20_balance_after_transfer = self.eth_trx.get_balance_of(erc20_contract, self.eth_account.address)
        require_that(
            "'in ethereum erc20 contact balance after transfer'",
            in_ethereum_erc20_balance_after_transfer,
            equal_to(0),
            quiet=True
        )

        lcc.set_step("Get ERC20 token balance of account in the ECHO network and check result")
        in_echo_erc20_balance = \
            self.utils.get_erc20_token_balance_in_echo(
                self,
                account_id=self.init4,
                balance_of_method=self.erc20_balanceOf,
                contract_id=erc20_contract_id,
                database_api_id=self.__database_api_identifier,
                previous_balance=0,
                signer=INIT4_PK
            )
        require_that(
            "'in echo account's erc20 balance'",
            in_echo_erc20_balance,
            equal_to(in_echo_erc20_start_balance),
            quiet=True
        )

        lcc.set_step("Perform first withdrawal ERC20 token operation")
        erc20_withdrawal_amounts = str(self.get_random_amount(_to=in_echo_erc20_balance))

        withdraw_erc20_token = self.send_wallet_request(
            "withdraw_erc20_token",
            [self.init4, self.eth_account.address, erc20_token_id, erc20_withdrawal_amounts, True],
            log_response=False
        )['result'][0]
        check_that_in(
            withdraw_erc20_token['operations'][0][1], "account", equal_to(self.init4), 'to',
            equal_to(self.eth_account.address[2:]), 'erc20_token', equal_to(erc20_token_id), 'value',
            equal_to(erc20_withdrawal_amounts)
        )
        lcc.set_step("Check result of withdraw_erc20_token")
        time.sleep(5)
        account_withdrawals = self.send_wallet_request(
            "get_erc20_account_withdrawals", [self.init4], log_response=False
        )['result']
        self.check_erc20_account_withdrawals([account_withdrawals[-1]], self.init4, erc20_withdrawal_amounts)
