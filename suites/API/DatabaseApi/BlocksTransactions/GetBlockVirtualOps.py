# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, is_not_none, require_that

SUITE = {
    "description": "Method 'get_block_virtual_ops'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.prop("negative", "type")
@lcc.tags("api", "database_api", "database_api_blocks_transactions", "get_block_virtual_ops")
@lcc.suite("Check work of method 'get_block'", rank=1)
class GetBlockVirtualOps(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.contract = self.get_byte_code("piggy", "code")
        self.get_pennie = self.get_byte_code("piggy", "pennieReturned()")

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
        self.contract_id = self.utils.get_contract_id(
            self, self.echo_acc0, self.contract, self.__database_api_identifier
        )

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'get_block_virtual_ops'")
    def method_main_check(self):
        contract_internal_call_operation_id = self.echo.config.operation_ids.CONTRACT_INTERNAL_CALL

        lcc.set_step("Call virtual 'contract_internal_call_operation' in ECHO network")
        contract_id = self.utils.get_contract_id(
            self, self.echo_acc0, self.contract, self.__database_api_identifier, value_amount=10
        )
        operation = self.echo_ops.get_contract_call_operation(
            echo=self.echo, registrar=self.echo_acc0, bytecode=self.get_pennie, callee=contract_id
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        block_num = broadcast_result["block_num"]
        lcc.log_info("Block number with operations is {}".format(block_num))

        lcc.set_step("Get the full first block in the chain")
        response_id = self.send_request(
            self.get_request("get_block_virtual_ops", [block_num]), self.__database_api_identifier
        )
        response = self.get_response(response_id)

        require_that("'result'", response["result"], is_not_none(), quiet=True)
        require_that(
            "'operation id'", response["result"][0]["op"][0], equal_to(contract_internal_call_operation_id), quiet=True
        )


@lcc.prop("negative", "type")
@lcc.tags("api", "database_api", "database_api_blocks_transactions", "get_block_virtual_ops")
@lcc.suite("Negative testing of method 'get_block_virtual_ops'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("API identifier are: database='{}'".format(self.__database_api_identifier))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Check negative int value in get_block_virtual_ops")
    @lcc.depends_on("API.DatabaseApi.BlocksTransactions.GetBlockVirtualOps.GetBlockVirtualOps.method_main_check")
    def check_negative_int_value_in_get_block_virtual_ops(self):
        error_message = "Assert Exception: result >= 0: Invalid cast from negative number to unsigned"

        lcc.set_step("Get 'get_block_virtual_ops' with negative block number")
        response_id = self.send_request(self.get_request("get_block_virtual_ops", [-1]), self.__database_api_identifier)
        message = self.get_response(response_id, negative=True)["error"]["message"]
        check_that("error_message", message, equal_to(error_message), quiet=True)
