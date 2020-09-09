# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, has_length, is_none, require_that

SUITE = {
    "description": "Methods: 'get_eth_address', 'get_objects' (eth_address object)"
}


@lcc.prop("main", "type")
@lcc.tags(
    "api", "database_api", "sidechain", "sidechain_ethereum", "database_api_sidechain_ethereum", "get_eth_address",
    "database_api_objects", "get_objects"
)
@lcc.suite("Check work of methods: 'get_eth_address', 'get_objects' (eth address object)", rank=1)
class GetEthAddress(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

    def setup_suite(self):
        super().setup_suite()
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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of methods: 'get_eth_address', 'get_objects' (eth address object)")
    def method_main_check(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(
            new_account, self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get address of created account in the network")
        response_id = self.send_request(
            self.get_request("get_eth_address", [new_account]), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_eth_address' of new account '{}'".format(new_account))

        lcc.set_step("Check simple work of method 'get_eth_address'")
        check_that("'new account eth address'", response["result"], is_none(), quiet=True)

        lcc.set_step("Generate ethereum address for new account")
        self.utils.perform_sidechain_eth_create_address_operation(self, new_account, self.__database_api_identifier)
        lcc.log_info("Ethereum address generated successfully")

        lcc.set_step("Get updated ethereum address of created account in the network")
        eth_account_address = self.utils.get_eth_address(self, new_account,
                                                         self.__database_api_identifier)["result"]["eth_addr"]
        lcc.log_info("Ethereum address of '{}' account is '{}'".format(new_account, eth_account_address))

        lcc.set_step("Check new eth address in method 'get_eth_address'")
        response_id = self.send_request(
            self.get_request("get_eth_address", [new_account]), self.__database_api_identifier
        )
        get_eth_address_result = self.get_response(response_id)["result"]
        self.object_validator.validate_eth_address_object(self, get_eth_address_result)

        lcc.set_step("Get eth address by id using 'get_objects'")
        params = [get_eth_address_result["id"]]
        response_id = self.send_request(self.get_request("get_objects", [params]), self.__database_api_identifier)
        get_objects_results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with params: {}".format(params))

        lcc.set_step("Check length of received objects")
        require_that("'list of received objects'", get_objects_results, has_length(len(params)), quiet=True)

        lcc.set_step("Check the identity of returned results of api-methods: 'get_eth_address', 'get_objects'")
        require_that('result', get_objects_results[0], equal_to(get_eth_address_result), quiet=True)
