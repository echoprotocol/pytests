# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import (
    check_that, check_that_in, equal_to, has_length, is_dict, is_false, is_integer, is_list, is_str, require_that
)

SUITE = {
    "description": "Use the contract to create a new contact and see its history"
}


@lcc.prop("main", "type")
@lcc.tags("scenarios", "history_of_contract_created_by_another_contract")
@lcc.suite("Check scenario 'Contract history that was created using another contract'")
class HistoryOfContractCreatedByAnotherContract(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__history_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("contract_create_contract", "code")
        self.deploy_contract = self.get_byte_code("contract_create_contract", "deploy_contract()")
        self.get_creator = self.get_byte_code("contract_create_contract", "created_contract")["creator()"]
        self.tr_asset_to_creator = self.get_byte_code("contract_create_contract",
                                                      "created_contract")["tr_asset_to_creator()"]
        self.contract_internal_create_operation_id = self.echo.config.operation_ids.CONTRACT_INTERNAL_CREATE
        self.contract_internal_call_operation_id = self.echo.config.operation_ids.CONTRACT_INTERNAL_CALL

    def check_contract_internal_create_op(self, contract_id, stop, limit, start, caller, new_contract):
        params = [contract_id, stop, limit, start]
        response_id = self.send_request(self.get_request("get_contract_history", params), self.__history_api_identifier)
        operation = self.get_response(response_id)["result"][0]["op"]
        operation_id, operation_dict = operation[0], operation[1]
        op_keys = [key for key in operation_dict.keys()]
        if require_that("'contract_internal_create_operation keys'", op_keys, has_length(5), quiet=True):
            check_that(
                "'contract_internal_create_operation id'",
                operation_id,
                equal_to(self.contract_internal_create_operation_id),
                quiet=True
            )
            check_that("'caller id'", caller, equal_to(operation_dict["caller"]))
            check_that("'new_contract id'", new_contract, equal_to(operation_dict["new_contract"]))
            check_that("'eth_accuracy'", operation_dict["eth_accuracy"], is_false())
            check_that("'value'", operation_dict["value"], is_dict())
            check_that("'extensions'", operation_dict["extensions"], is_list())

    def check_contract_internal_call_op(self, contract_id, stop, limit, start, caller, new_contract):
        params = [contract_id, stop, limit, start]
        response_id = self.send_request(self.get_request("get_contract_history", params), self.__history_api_identifier)
        operation = self.get_response(response_id)["result"][0]["op"]
        operation_id, operation_dict = operation[0], operation[1]
        op_keys = [key for key in operation_dict.keys()]
        if require_that("'contract_internal_call_operation keys'", op_keys, has_length(5), quiet=True):
            check_that(
                "'contract_internal_call_operation id'",
                operation_id,
                equal_to(self.contract_internal_call_operation_id),
                quiet=True
            )
            check_that("'caller id'", caller, equal_to(operation_dict["caller"]))
            check_that("'new_contract id'", new_contract, equal_to(operation_dict["callee"]))
            check_that("'eth_accuracy'", operation_dict["method"], is_str())
            check_that("'value'", operation_dict["value"], is_dict())
            check_that("'extensions'", operation_dict["extensions"], is_list())

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__history_api_identifier = self.get_identifier("history")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', "
            "history='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier, self.__history_api_identifier
            )
        )
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test(
        "The scenario describes the creation of a contract whose method creates a new contract. "
        "Getting the history of the created contract"
    )
    def history_of_contract_created_by_another_contract(self):
        operation_history_obj = "{}0".format(self.get_object_type(self.echo.config.object_types.OPERATION_HISTORY))
        stop, start = operation_history_obj, operation_history_obj
        limit = 100

        lcc.set_step("Create 'contract_contract_create' contract in the Echo network")
        operation = self.echo_ops.get_contract_create_operation(
            echo=self.echo, registrar=self.echo_acc0, bytecode=self.contract
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_id = self.get_contract_id(contract_result)

        lcc.set_step("Call 'deploy_contract' method")
        operation = self.echo_ops.get_contract_call_operation(
            echo=self.echo, registrar=self.echo_acc0, bytecode=self.deploy_contract, callee=contract_id
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)

        lcc.set_step("Get output with address of deployed contract")
        created_contract_id = self.get_contract_output(contract_result, output_type="contract_address")
        lcc.log_info("Output is '{}'".format(created_contract_id))

        lcc.set_step("Check 'contract_internal_create_operation' in created contract history")
        self.check_contract_internal_create_op(
            created_contract_id, stop, limit, start, contract_id, created_contract_id
        )

        lcc.set_step("Check 'contract_internal_create_operation' in contract history")
        self.check_contract_internal_create_op(contract_id, stop, limit, start, contract_id, created_contract_id)

        lcc.set_step("Call 'get_creator' method of created contract")
        operation = self.echo_ops.get_contract_call_operation(
            echo=self.echo, registrar=self.echo_acc0, bytecode=self.get_creator, callee=created_contract_id
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)

        lcc.set_step("Get output with address of contract creator")
        creator_contract_id = self.get_contract_output(contract_result, output_type="contract_address")
        lcc.log_info("Output is '{}'".format(creator_contract_id))

        lcc.set_step("Check that the correct address of the contract creator is in the response")
        check_that(
            "contract address of contract creator in output",
            creator_contract_id,
            equal_to(contract_id),
        )

        lcc.set_step("Call 'tr_asset_to_creator' method of created contract")
        value_amount = 1
        operation = self.echo_ops.get_contract_call_operation(
            echo=self.echo,
            registrar=self.echo_acc0,
            bytecode=self.tr_asset_to_creator,
            callee=created_contract_id,
            value_amount=value_amount
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get contract balance and store")
        response_id = self.send_request(
            self.get_request("get_contract_balances", [contract_id]), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        check_that_in(response["result"][0], "amount", is_integer(value_amount), "asset_id", is_str(self.echo_asset))
        contract_balance = response["result"][0]["amount"]

        lcc.set_step("Check that contract creator received assets from created contract")
        check_that(
            "balance of contract creator",
            contract_balance,
            equal_to(value_amount),
        )

        lcc.set_step("Check 'contract_internal_call_operation' in created contract history")
        self.check_contract_internal_call_op(created_contract_id, stop, limit, start, created_contract_id, contract_id)

        lcc.set_step("Check 'contract_internal_call_operation' in contract history")
        self.check_contract_internal_call_op(contract_id, stop, limit, start, created_contract_id, contract_id)
