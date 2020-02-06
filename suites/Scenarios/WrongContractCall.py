# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, is_

from common.base_test import BaseTest

SUITE = {
    "description": "Testing wrong contract call"
}


@lcc.prop("main", "type")
@lcc.tags("scenarios", "wrong_contract_call")
@lcc.suite("Check scenario 'Wrong contract call'")
class WrongContractCall(BaseTest):
    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("wrong_contract", "code")
        self.value_amount = 10

    def setup_suite(self):
        super().setup_suite()
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

    @lcc.test("The scenario describes behavior of wrong contact call.")
    def wrong_contract_call(self):
        wrong_bytecodes = ['get_balance(\"1.2.10\", \"1.3.0\"', 'greet(\"1.2.10\", \"1.3.0\"']
        correct_bytecodes = ['get_balance(\"1.2.10\", \"1.3.0\")', 'greet(\"1.2.10\", \"1.3.0\")']
        error_massage = "incorrect_parameters"

        lcc.set_step("Create 'Wrong call' contract in the Echo network")
        operation = self.echo_ops.get_contract_create_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                bytecode=self.contract,
                                                                value_amount=self.value_amount,
                                                                value_asset_id=self.echo_asset)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_id = \
            self.get_contract_result(broadcast_result, self.__database_api_identifier, mode="x86")["result"][1][
                "contract_id"]
        lcc.log_info("Created contract id: {}".format(contract_id))

        lcc.set_step("Call method of 'Wrong call' contract with wrong bytecode")
        for bytecode in wrong_bytecodes:
            operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                  bytecode=bytecode, callee=contract_id)
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
            call_result = self.get_contract_result(broadcast_result, self.__database_api_identifier, mode="x86"
                                                   )["result"][1]["result"]["error"]
            require_that("'wrong contract call error'", call_result, is_(error_massage))

        lcc.set_step("Call method of 'Wrong call' contract with correct bytecode")
        for bytecode in correct_bytecodes:
            operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                  bytecode=bytecode, callee=contract_id)
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
            call_result = self.get_contract_result(broadcast_result, self.__database_api_identifier, mode="x86"
                                                   )["result"][1]["result"]["error"]
            require_that("'wrong contract call error'", call_result, is_("none"))


