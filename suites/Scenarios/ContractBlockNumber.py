# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, equal_to, not_equal_to, check_that, is_integer, is_true

from common.base_test import BaseTest

SUITE = {
    "description": "Testing x86-64 contract method 'get_block_number'"
}


@lcc.disabled()
@lcc.prop("main", "type")
@lcc.tags("scenarios", "contract_block_number")
@lcc.suite("Check scenario 'Get contract block number'")
class ContractBlockNumber(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract_x86 = self.get_byte_code("contract_x86", "code")
        self.contract_method = self.get_byte_code("contract_x86", "get_block_number()")
        self.contract_evm = self.get_byte_code("contract_evm", "code")
        self.contract_method = self.get_byte_code("contract_evm", "log()")

    def get_head_block_num(self):
        return self.echo.api.database.get_dynamic_global_properties()["head_block_number"]

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
        lcc.log_info("Echo account'{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("The scenario describes the mechanism of using contract method 'get_block_number'")
    def contract_block_number(self):
        lcc.set_step("Create x86 contract in the Echo network and get its contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_x86, self.__database_api_identifier,
                                                 mode="x86")["contract_id"]

        lcc.set_step("Call x86 contact method")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode="get_block_number()", callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier, fee_amount=200)
        operation_results = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)["trx"]["operation_results"][0][1]
        lcc.log_info("Call contract method result id: {}".format(operation_results))

        lcc.set_step("Check contract method result with current block number")
        response_id = self.send_request(self.get_request("get_objects", [[operation_results]]),
                                        self.__database_api_identifier)
        method_result = self.get_response(response_id)["result"][0]["block_num"]
        lcc.log_info("Method result: {}".format(method_result))

        current_block_num = self.get_head_block_num()
        require_that("'block number'", method_result == current_block_num, is_true())

        lcc.set_step("Create evm contract in the Echo network and get its contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_evm, self.__database_api_identifier,
                                                 mode="evm")

        lcc.set_step("Call evm contact method")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.contract_method, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier, fee_amount=200)
        operation_results = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)["trx"]["operation_results"][0][1]
        lcc.log_info("Call contract method result id: {}".format(operation_results))

        lcc.set_step("Check contract method result with current block number")
        response_id = self.send_request(self.get_request("get_objects", [[operation_results]]),
                                        self.__database_api_identifier)
        method_result = self.get_response(response_id)["result"][0]["block_num"]
        lcc.log_info("Method result: {}".format(method_result))

        current_block_num = self.get_head_block_num()
        require_that("'block number'", method_result == current_block_num, is_true())