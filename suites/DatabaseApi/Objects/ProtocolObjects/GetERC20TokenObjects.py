# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import has_length, require_that, require_that_in, equal_to

from common.base_test import BaseTest
SUITE = {
    "description": "Method 'get_objects' (erc20 token object)"
}


@lcc.prop("main", "type")
@lcc.tags("api", "database_api", "database_api_objects", "get_objects", "aaa")
@lcc.suite("Check work of method 'get_objects' (erc20 token object)", rank=1)
class GetERC20TokenObjects(BaseTest):

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

    @lcc.test("Simple work of method 'get_objects' (erc20 token object)")
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
        get_erc20_token_result = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_erc20_token' with eth_erc20_contract_address='{}' parameter".format(
            erc20_contract.address[2:]))

        lcc.set_step("Get ERC20 token object")
        params = [get_erc20_token_result["id"]]
        response_id = self.send_request(self.get_request("get_objects", [params]), self.__database_api_identifier)
        results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with params: {}".format(params))

        lcc.set_step("Check length of received objects")
        require_that(
            "'list of received objects'",
            results,
            has_length(len(params)),
            quiet=True
        )

        for i, result in enumerate(results):
            lcc.set_step("Checking erc20 token object #{} - '{}'".format(i, params[i]))
            self.object_validator.validate_erc20_token_object(self, result)

        lcc.set_step("Check the identity of returned results of api-methods: 'get_erc20_token', 'get_objects'")
        require_that(
            'result',
            results[0], equal_to(get_erc20_token_result),
            quiet=True
        )
