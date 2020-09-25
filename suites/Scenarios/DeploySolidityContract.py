# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_

SUITE = {
    "description": "Testing solidity 0.6 contract call"
}


@lcc.prop("main", "type")
@lcc.tags("scenarios", "deploy_solidity_contract")
@lcc.suite("Check scenario 'deploy_solidity_contract'")
class DeploySolidityContract(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("solidity_contract", "code")
        self.method = self.get_byte_code("solidity_contract", "helloWorld()")
        self.expected_string = 'Hello, World!'

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

    @lcc.test("The scenario describes behavior of solidity contact call.")
    def wrong_contract_call(self):

        lcc.set_step("Create 'Solidity 0.6 contract' contract in the Echo network")
        operation = self.echo_ops.get_contract_create_operation(
            echo=self.echo, registrar=self.echo_acc0, bytecode=self.contract, value_asset_id=self.echo_asset
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier, fee_amount=200)
        broadcast_result = self.echo_ops.broadcast(
            echo=self.echo, list_operations=collected_operation, log_broadcast=True
        )
        contract_result = \
            self.get_contract_result(broadcast_result, self.__database_api_identifier, mode="evm")
        contract_id = "1.11.{}".format(int(contract_result["result"][1]["exec_res"]["new_address"][2:], 16))
        lcc.log_info("Created contract id: {}".format(contract_id))

        operation = self.echo_ops.get_contract_call_operation(
            echo=self.echo, registrar=self.echo_acc0, bytecode=self.method, callee=contract_id
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("Hello world method of contract called successfully")

        lcc.set_step("Check that 'Hello World!!!' string in contract output")
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_output = self.get_contract_output(
            contract_result, output_type=str, len_output_string=len(self.expected_string)
        )
        check_that("return of method 'Hello Wolrd'", contract_output, is_(self.expected_string))
