# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'get_contract_result'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_contracts", "wallet_get_contract_result")
@lcc.suite("Check work of method 'get_contract_result'", rank=1)
class GetContractResult(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.dynamic_fields_contract = self.get_byte_code("dynamic_fields", "code")
        self.set_string = self.get_byte_code("dynamic_fields", "onStringChanged(string)")
        self.get_string = self.get_byte_code("dynamic_fields", "getString()")

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
        lcc.log_info("Echo account are: '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'wallet_get_contract_result'")
    def method_main_check(self, get_random_string):
        string_param = get_random_string

        lcc.set_step("Create 'dynamic_fields' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(
            self, self.echo_acc0, self.dynamic_fields_contract, self.__database_api_identifier
        )

        lcc.set_step("Call method 'set_string' to add uint field in contract")
        method_bytecode = self.set_string + self.get_byte_code_param(string_param, param_type=str)
        operation = self.echo_ops.get_contract_call_operation(
            echo=self.echo, registrar=self.echo_acc0, bytecode=method_bytecode, callee=contract_id
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        lcc.log_info("Method 'set_string' performed successfully")

        lcc.set_step("Call method 'get_string'")
        operation = self.echo_ops.get_contract_call_operation(
            echo=self.echo, registrar=self.echo_acc0, bytecode=self.get_string, callee=contract_id
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(
            echo=self.echo, list_operations=collected_operation, log_broadcast=False
        )
        lcc.log_info("Method 'get_string' performed successfully")

        lcc.set_step("Check get_contract_result output")
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)['result'][1]
        contract_result_id = self.get_operation_results_ids(broadcast_result)
        contract_result_obj = self.send_wallet_request("get_contract_result", [contract_result_id], log_response=False)['result']
        check_that("contract result", contract_result_obj, equal_to(contract_result), quiet=True)
