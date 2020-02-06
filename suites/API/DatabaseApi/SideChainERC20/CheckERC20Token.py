# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, is_true, is_false

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'check_erc20_token'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags(
    "api", "database_api", "sidechain", "sidechain_erc20", "database_api_sidechain_erc20", "check_erc20_token"
)
@lcc.suite("Check work of method 'check_erc20_token'", rank=1)
class CheckERC20Token(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.eth_account = None
        self.erc20_contract_code = self.get_byte_code("erc20", "code", ethereum_contract=True)
        self.erc20_abi = self.get_abi("erc20")

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

    @lcc.test("Simple work of method 'check_erc20_token'")
    def method_main_check(self, get_random_string, get_random_valid_asset_name):
        contract_name = get_random_string
        erc20_symbol = get_random_valid_asset_name

        lcc.set_step("Deploy ERC20 contract in the Ethereum network")
        erc20_contract = self.eth_trx.deploy_contract_in_ethereum_network(
            self.web3,
            eth_address=self.eth_account.address,
            contract_abi=self.erc20_abi,
            contract_bytecode=self.erc20_contract_code
        )
        lcc.log_info("ERC20 contract created in Ethereum network, address: '{}'".format(erc20_contract.address))

        lcc.set_step("Perform register erc20 token operation")
        self.utils.perform_sidechain_erc20_register_token_operation(
            self,
            account=self.echo_acc0,
            eth_addr=erc20_contract.address,
            name=contract_name,
            symbol=erc20_symbol,
            database_api_id=self.__database_api_identifier
        )
        lcc.log_info("Registration of ERC20 token completed successfully")

        lcc.set_step("Get created ERC20 token and store contract id in the ECHO network")
        response_id = self.send_request(self.get_request("get_erc20_token", [erc20_contract.address[2:]]),
                                        self.__database_api_identifier)
        erc20_contract_id = self.get_response(response_id)["result"]["contract"]

        lcc.set_step("Check that erc20 token created")
        response_id = self.send_request(self.get_request("check_erc20_token", [erc20_contract_id]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        lcc.log_info(
            "Call method 'check_erc20_token' with erc20_contract_id='{}' parameter".format(erc20_contract_id))

        lcc.set_step("Check simple work of method 'check_erc20_token'")
        require_that(
            "'erc20_token'",
            result, is_true(),
            quiet=True
        )


@lcc.prop("positive", "type")
@lcc.tags(
    "api", "database_api", "sidechain", "sidechain_erc20", "database_api_sidechain_erc20", "check_erc20_token"
)
@lcc.suite("Positive testing of method 'check_erc20_token'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.piggy_contract = self.get_byte_code("piggy", "code")

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Call method with simple contract id")
    @lcc.depends_on("API.DatabaseApi.SideChainERC20.CheckERC20Token.CheckERC20Token.method_main_check")
    def call_method_with_ethereum_contract_id(self):
        lcc.set_step("Create 'piggy' contract in ECHO network")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier)

        lcc.set_step("Check that erc20 token created")
        response_id = self.send_request(self.get_request("check_erc20_token", [contract_id]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        lcc.log_info(
            "Call method 'check_erc20_token' with erc20_contract_id='{}' parameter".format(contract_id))

        lcc.set_step("Check simple work of method 'check_erc20_token'")
        require_that(
            "'erc20_token'",
            result, is_false(),
            quiet=True
        )
