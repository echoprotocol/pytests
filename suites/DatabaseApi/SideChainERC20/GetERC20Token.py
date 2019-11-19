# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_erc20_token'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags(
    "api", "database_api", "sidechain", "sidechain_erc20",
    "database_api_sidechain_erc20", "get_erc20_token"
)
@lcc.suite("Check work of method 'get_erc20_token'", rank=1)
class GetERC20Token(BaseTest):

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

    @lcc.test("Simple work of method 'get_erc20_token'")
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
        result = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_erc20_token' with eth_erc20_contract_address='{}' parameter".format(
            erc20_contract.address[2:]))

        lcc.set_step("Check simple work of method 'get_erc20_token'")
        self.object_validator.validate_erc20_token_object(self, result)


@lcc.prop("positive", "type")
@lcc.tags(
    "api", "database_api", "sidechain", "sidechain_erc20",
    "database_api_sidechain_erc20", "get_erc20_token"
)
@lcc.suite("Positive testing of method 'get_erc20_token'", rank=2)
class PositiveTesting(BaseTest):

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

    @lcc.test("Create contract using register_erc20_token operation and get info about it")
    @lcc.depends_on("DatabaseApi.SideChainERC20.GetERC20Token.GetERC20Token.method_main_check")
    def get_info_about_created_erc20_contract(self, get_random_string, get_random_valid_asset_name,
                                              get_random_integer_up_to_ten):
        contract_name = get_random_string
        erc20_symbol = get_random_valid_asset_name
        erc20_token_decimals = get_random_integer_up_to_ten

        lcc.set_step("Deploy ERC20 contract in the Ethereum network")
        erc20_contract = self.eth_trx.deploy_contract_in_ethereum_network(
            self.web3,
            eth_address=self.eth_account.address,
            contract_abi=self.erc20_abi,
            contract_bytecode=self.erc20_contract_code
        )
        lcc.log_info("ERC20 contract created in Ethereum network, address: '{}'".format(erc20_contract.address))

        lcc.set_step("Perform register erc20 token operation")
        bd_result = \
            self.utils.perform_sidechain_erc20_register_token_operation(
                self,
                account=self.echo_acc0,
                eth_addr=erc20_contract.address,
                name=contract_name,
                symbol=erc20_symbol,
                decimals=erc20_token_decimals,
                database_api_id=self.__database_api_identifier
            )
        erc20_token_id = self.get_contract_result(bd_result, self.__database_api_identifier)
        lcc.log_info("Registration of ERC20 token completed successfully, ERC20 token object is '{}'".format(
            erc20_token_id))

        lcc.set_step("Get created ERC20 token and store contract id in the ECHO network")
        response_id = self.send_request(self.get_request("get_erc20_token", [erc20_contract.address[2:]]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_erc20_token' with eth_erc20_contract_address='{}' parameter".format(
            erc20_contract.address[2:]))

        check_that_in(
            result,
            "id", equal_to(erc20_token_id),
            "owner", equal_to(self.echo_acc0),
            "eth_addr", equal_to(erc20_contract.address[2:]),
            "name", equal_to(contract_name),
            "symbol", equal_to(erc20_symbol),
            "decimals", equal_to(erc20_token_decimals),
            quiet=True
        )

    @lcc.test("Create contract using register_erc20_token operation and compare response from 'get_erc20_token' "
              "and 'get_objects'")
    @lcc.depends_on("DatabaseApi.SideChainERC20.GetERC20Token.GetERC20Token.method_main_check")
    def compare_with_method_get_objects(self, get_random_string, get_random_valid_asset_name):
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
        bd_result = \
            self.utils.perform_sidechain_erc20_register_token_operation(
                self,
                account=self.echo_acc0,
                eth_addr=erc20_contract.address,
                name=contract_name,
                symbol=erc20_symbol,
                database_api_id=self.__database_api_identifier
            )
        erc20_token_id = self.get_contract_result(bd_result, self.__database_api_identifier)
        lcc.log_info("Registration of ERC20 token completed successfully, ERC20 token object is '{}'".format(
            erc20_token_id))

        lcc.set_step("Get created ERC20 token and store contract id in the ECHO network")
        response_id = self.send_request(self.get_request("get_erc20_token", [erc20_contract.address[2:]]),
                                        self.__database_api_identifier)
        response_1 = self.get_response(response_id)
        lcc.log_info("Call method 'get_erc20_token' with eth_erc20_contract_address='{}' parameter".format(
            erc20_contract.address[2:]))

        lcc.set_step("Get account by id")
        response_id = self.send_request(self.get_request("get_objects", [[erc20_token_id]]),
                                        self.__database_api_identifier)
        response_2 = self.get_response(response_id)
        lcc.log_info("Call method 'get_objects' with param: {}".format(erc20_token_id))

        lcc.set_step("Checking created account")
        erc20_object_info_1 = response_1["result"]
        erc20_object_info_2 = response_2["result"][0]
        check_that_in(
            erc20_object_info_1,
            "id", equal_to(erc20_object_info_2["id"]),
            "owner", equal_to(erc20_object_info_2["owner"]),
            "eth_addr", equal_to(erc20_object_info_2["eth_addr"]),
            "contract", equal_to(erc20_object_info_2["contract"]),
            "name", equal_to(erc20_object_info_2["name"]),
            "symbol", equal_to(erc20_object_info_2["symbol"]),
            "decimals", equal_to(erc20_object_info_2["decimals"]),
            quiet=True
        )
