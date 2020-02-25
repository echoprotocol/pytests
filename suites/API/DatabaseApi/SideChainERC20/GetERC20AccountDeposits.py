# -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, greater_than, has_length, check_that_in,\
    equal_to, is_true

from common.base_test import BaseTest

SUITE = {
    "description": "Methods: 'get_erc20_account_deposits', 'get_objects' (deposit erc20 token object)"
}


@lcc.prop("main", "type")
@lcc.tags(
    "api", "database_api", "sidechain", "sidechain_erc20",
    "database_api_sidechain_erc20", "get_erc20_account_deposits",
    "database_api_objects", "get_objects"
)
@lcc.suite("Check work of methods: 'get_erc20_account_deposits', 'get_objects (deposit erc20 token object)'", rank=1)
class GetERC20AccountDeposits(BaseTest):

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

    def check_erc20_account_deposits(self, deposits, account_id, erc20_deposit_amounts, erc20_contract_address):
        require_that(
            "'account deposits count'",
            deposits, has_length(len(erc20_deposit_amounts)),
            quiet=True
        )

        for i, erc20_account_deposit in enumerate(deposits):
            lcc.set_step("Check work of method 'get_erc20_account_deposits', deposit #'{}'".format(i))
            self.object_validator.validate_erc20_deposit_object(self, erc20_account_deposit)
            check_that_in(
                erc20_account_deposit,
                "account", equal_to(account_id),
                "erc20_addr", equal_to(erc20_contract_address[2:]),
                "value", equal_to(str(erc20_deposit_amounts[i])),
                "is_approved", is_true(),
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
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier,
                                                                           ))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))
        self.eth_account = self.get_default_ethereum_account()
        lcc.log_info("Ethereum address in the ethereum network: '{}'".format(self.eth_account.address))
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of methods: : 'get_erc20_account_deposits', 'get_objects (deposit erc20 token object)'")
    def method_main_check(self, get_random_valid_account_name, get_random_string, get_random_valid_asset_name):
        new_account_name = get_random_valid_account_name
        token_name = "erc20" + get_random_string
        erc20_symbol = get_random_valid_asset_name
        erc20_deposit_amounts = []

        lcc.set_step("Create and get new account")
        new_account_id = self.get_account_id(new_account_name, self.__database_api_identifier,
                                             self.__registration_api_identifier)
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
            name=token_name, symbol=erc20_symbol,
            database_api_id=self.__database_api_identifier
        )
        lcc.log_info("Registration of ERC20 token completed successfully")

        lcc.set_step("Get created ERC20 token and store contract id in the ECHO network")
        response_id = self.send_request(self.get_request("get_erc20_token", [erc20_contract.address[2:]]),
                                        self.__database_api_identifier)
        erc20_contract_id = self.get_response(response_id)["result"]["contract"]
        lcc.log_info("ERC20 token has contract_id '{}'".format(erc20_contract_id))

        lcc.set_step("First transfer erc20 to ethereum address of created account")
        erc20_deposit_amounts.append(self.get_random_amount(_to=in_ethereum_start_erc20_balance))
        self.eth_trx.transfer(self.web3, erc20_contract, eth_account_address, erc20_deposit_amounts[0])
        lcc.log_info(
            "Transfer '{}' erc20 tokens to '{}' account completed successfully".format(erc20_deposit_amounts[0],
                                                                                       eth_account_address))

        lcc.set_step("First: Get ERC20 account deposits")
        get_erc20_account_deposits_results = self.utils.get_erc20_account_deposits(
            self,
            new_account_id,
            self.__database_api_identifier
        )["result"]

        self.check_erc20_account_deposits(
            get_erc20_account_deposits_results,
            new_account_id,
            erc20_deposit_amounts,
            erc20_contract.address
        )

        lcc.set_step("Get ethereum ERC20 tokens balance after first transfer in the Ethereum network")
        in_ethereum_erc20_balance_after_first_transfer = self.eth_trx.get_balance_of(
            erc20_contract,
            self.eth_account.address
        )
        require_that(
            "'in ethereum erc20 contact balance after first transfer'",
            in_ethereum_erc20_balance_after_first_transfer,
            equal_to(in_ethereum_start_erc20_balance - erc20_deposit_amounts[0]),
            quiet=True
        )

        lcc.set_step("Second transfer erc20 to ethereum address of created account")
        erc20_deposit_amounts.append(in_ethereum_erc20_balance_after_first_transfer)
        self.eth_trx.transfer(self.web3, erc20_contract, eth_account_address, erc20_deposit_amounts[1])
        lcc.log_info(
            "Transfer '{}' erc20 tokens to '{}' account completed successfully".format(erc20_deposit_amounts[1],
                                                                                       eth_account_address))

        lcc.set_step("Get ethereum ERC20 tokens balance after second transfer in the Ethereum network")
        in_ethereum_erc20_balance_after_second_transfer = self.eth_trx.get_balance_of(erc20_contract,
                                                                                      self.eth_account.address)
        require_that(
            "'in ethereum erc20 contact balance after second transfer'",
            in_ethereum_erc20_balance_after_second_transfer,
            equal_to(in_ethereum_erc20_balance_after_first_transfer - erc20_deposit_amounts[1]),
            quiet=True
        )

        import time
        time.sleep(5)
        lcc.set_step("Second: Get ERC20 account deposits")
        get_erc20_account_deposits_results = self.utils.get_erc20_account_deposits(
            self,
            new_account_id,
            self.__database_api_identifier,
            previous_account_deposits=get_erc20_account_deposits_results
        )["result"]

        self.check_erc20_account_deposits(
            get_erc20_account_deposits_results,
            new_account_id,
            erc20_deposit_amounts,
            erc20_contract.address
        )

        lcc.set_step("Get ERC20 token balance of account in the ECHO network and check result")
        in_echo_erc20_balance = \
            self.utils.get_erc20_token_balance_in_echo(
                self,
                account_id=new_account_id,
                balance_of_method=self.erc20_balanceOf,
                contract_id=erc20_contract_id,
                database_api_id=self.__database_api_identifier
            )
        require_that(
            "'final balance equal to start balance'",
            in_echo_erc20_balance == in_ethereum_start_erc20_balance, is_true(),
            quiet=True
        )

        lcc.set_step("Get erc20 deposits by id using 'get_objects'")
        params = [deposit["id"] for deposit in get_erc20_account_deposits_results]
        response_id = self.send_request(self.get_request("get_objects", [params]), self.__database_api_identifier)
        get_objects_results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with params: {}".format(params))

        lcc.set_step("Check length of received objects")
        require_that(
            "'list of received objects'",
            get_objects_results, has_length(len(params)),
            quiet=True
        )
        lcc.set_step("Compare erc20 deposits in 'get_erc20_deposits' with method 'get_objects'")
        for i, deposit in enumerate(get_erc20_account_deposits_results):
            del deposit["approves"]
            del get_objects_results[i]["approves"]
            lcc.set_step("Compare #{}: deposit in 'get_erc20_deposits' with method 'get_objects'".format(i))
            require_that(
                "result",
                get_objects_results[i], equal_to(deposit),
                quiet=True
            )
