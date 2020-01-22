# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, require_that

from common.base_test import BaseTest

SUITE = {
    "description": "Operation 'evm_address_register'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "sidechain", "sidechain_ethereum", "evm_address_register")
@lcc.suite("Check work of operation 'evm_address_register'", rank=1)
class EvmCreateRegister(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of operation 'evm_address_register'")
    def evm_address_register_operation(self, get_random_valid_account_name, get_random_eth_address):
        new_account = get_random_valid_account_name
        evm_address = get_random_eth_address

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get account balance in ethereum of new account")
        ethereum_balance = self.utils.get_account_balances(self, new_account, self.__database_api_identifier,
                                                           self.eth_asset)["amount"]
        check_that("'balance in ethereum'", ethereum_balance, equal_to(0))

        lcc.set_step("Register EVM address for new account")
        operation = self.echo_ops.get_evm_address_register_operation(echo=self.echo, account=new_account,
                                                                     evm_address=evm_address)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception("Error: can't register evm address, response:\n{}".format(broadcast_result))
        operation_result = broadcast_result["trx"]["operation_results"][0][1]
        lcc.log_info("EVM address registred successfully")

        lcc.set_step("Get EVM address of {} account".format(new_account))
        response_id = self.send_request(self.get_request("get_evm_addresses", [new_account]),
                                        self.__database_api_identifier)
        evm_address_account = self.get_response(response_id)["result"][0]["evm_address"]

        response_id = self.send_request(self.get_request("get_objects", [[operation_result]]),
                                        self.__database_api_identifier)
        evm_address_object = self.get_response(response_id)["result"][0]["evm_address"]
        require_that("evm_address", evm_address_account, equal_to(evm_address_object))





