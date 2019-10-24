# -*- coding: utf-8 -*-
import math

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, check_that_in, is_str, is_list, is_integer, require_that, \
    require_that_in, has_length

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_contract_history'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("api", "history_api", "get_contract_history")
@lcc.suite("Check work of method 'get_contract_history'", rank=1)
class GetContractHistory(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__history_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("piggy", "code")

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__history_api_identifier = self.get_identifier("history")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', "
            "history='{}'".format(self.__database_api_identifier, self.__registration_api_identifier,
                                  self.__history_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'get_contract_history'")
    def method_main_check(self):
        operation_history_obj = "{}0".format(self.get_object_type(self.echo.config.object_types.OPERATION_HISTORY))
        stop, start = operation_history_obj, operation_history_obj
        limit = 1

        lcc.set_step("Perform create contract operation")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier)

        lcc.set_step("Get contract history")
        params = [contract_id, stop, limit, start]
        response_id = self.send_request(self.get_request("get_contract_history", params), self.__history_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_contract_history' with: contract_id='{}', stop='{}', limit='{}', start='{}' "
                     "parameters".format(contract_id, stop, limit, start))

        lcc.set_step("Check response from method 'get_contract_history'")
        results = response["result"]
        check_that(
            "'number of history results'",
            results, has_length(limit)
        )
        for result in results:
            if not self.type_validator.is_operation_history_id(result["id"]):
                lcc.log_error("Wrong format of 'operation id', got: {}".format(result["id"]))
            else:
                lcc.log_info("'operation_id' has correct format: operation_history_id")
            check_that_in(
                result,
                "op", is_list(),
                "result", is_list(),
                "block_num", is_integer(),
                "trx_in_block", is_integer(),
                "op_in_trx", is_integer(),
                "virtual_op", is_integer(),
                quiet=True
            )


@lcc.prop("positive", "type")
@lcc.tags("api", "history_api", "get_contract_history")
@lcc.suite("Positive testing of method 'get_contract_history'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__history_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None
        self.contract = self.get_byte_code("piggy", "code")
        self.get_pennie = self.get_byte_code("piggy", "pennieReturned()")
        self.broadcast_result = None

    def get_contract_history(self, contract_id, stop, limit, start, negative=False):
        lcc.log_info("Get '{}' contract history".format(contract_id))
        params = [contract_id, stop, limit, start]
        response_id = self.send_request(self.get_request("get_contract_history", params), self.__history_api_identifier)
        return self.get_response(response_id, negative=negative)

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__history_api_identifier = self.get_identifier("history")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', "
            "history='{}'".format(self.__database_api_identifier, self.__registration_api_identifier,
                                  self.__history_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc1 = self.get_account_id(self.accounts[1], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Check contract history of new account")
    @lcc.depends_on("HistoryApi.GetContractHistory.GetContractHistory.method_main_check")
    def new_contract_history(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name
        operation_history_obj = "{}0".format(self.get_object_type(self.echo.config.object_types.OPERATION_HISTORY))
        stop, start = operation_history_obj, operation_history_obj
        limit = 100
        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Perform create contract operation")
        contract_id = self.utils.get_contract_id(self, new_account, self.contract, self.__database_api_identifier)

        lcc.set_step("Get new contract history")
        response = self.get_contract_history(contract_id, stop, limit, start)

        lcc.set_step("Check new contract history")
        require_that(
            "'new contract history'",
            response["result"], has_length(1)
        )
        check_that(
            "'operation id'",
            response["result"][0]["op"][0], is_integer(self.echo.config.operation_ids.CONTRACT_CREATE)
        )

    # todo: uncomment when bug ECHO-1462 will be fixed
    # @lcc.test("Check limit number of operations to retrieve")
    # @lcc.depends_on("HistoryApi.GetContractHistory.GetContractHistory.method_main_check")
    def limit_operations_to_retrieve(self, get_random_valid_account_name, get_random_integer_up_to_fifty):
        new_account = get_random_valid_account_name
        operation_history_obj = "{}0".format(self.get_object_type(self.echo.config.object_types.OPERATION_HISTORY))
        stop, start = operation_history_obj, operation_history_obj
        min_limit = 1
        max_limit = 100
        contract_create_op_count = 1
        contract_call_op_count = transfer_op_count = 5
        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)

        lcc.set_step("Perform create contract operation")
        contract_id = self.utils.get_contract_id(self, new_account, self.contract, self.__database_api_identifier,
                                                 value_amount=max_limit)

        lcc.set_step("Perform operations using a new account. Call contract operation count equal to limit")
        self.utils.perform_contract_call_operation(self, new_account, self.get_pennie,
                                                   self.__database_api_identifier, contract_id, transfer_op_count)
        lcc.log_info("Fill contract history with '{}' number of contract transfer operations".format(transfer_op_count))

        lcc.set_step(
            "Check that count of new contract history with the maximum limit")
        response = self.get_contract_history(contract_id, stop, max_limit, start)
        check_that(
            "'number of history results'",
            response["result"], has_length(contract_call_op_count + contract_create_op_count)
        )

        lcc.set_step("Check minimum list length contract history")
        response = self.get_contract_history(contract_id, stop, min_limit, start)
        check_that(
            "'number of history results'",
            response["result"], has_length(min_limit)
        )

        lcc.set_step("Perform operations using a new account to create max_limit operations")
        limit = max_limit - contract_call_op_count - contract_create_op_count
        self.utils.perform_contract_call_operation(self, new_account, self.get_pennie,
                                                   self.__database_api_identifier, contract_id, limit)
        lcc.log_info("Fill contract history with '{}' number of contract transfer operations".format(limit))

        lcc.set_step(
            "Check that count of new contract history with the limit = max_limit is equal to max_limit")
        response = self.get_contract_history(contract_id, stop, max_limit, start)
        check_that(
            "'number of history results'",
            response["result"], has_length(max_limit)
        )
    # todo: uncomment when bug ECHO-1462 will be fixed
    # @lcc.test("Check stop and start IDs of the operations in contract history")
    # @lcc.depends_on("HistoryApi.GetContractHistory.GetContractHistory.method_main_check")
    def stop_and_start_operations(self, get_random_integer, get_random_integer_up_to_fifty):
        value_amount = get_random_integer
        operation_history_obj = "{}0".format(self.get_object_type(self.echo.config.object_types.OPERATION_HISTORY))
        stop, start = operation_history_obj, operation_history_obj
        operations = []
        operation_ids = []

        lcc.set_step("Perform create contract operation")
        bd_result = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier,
                                               value_amount=value_amount, need_broadcast_result=True)
        contract_id = bd_result.get("contract_id")
        contract_create_operation = bd_result.get("broadcast_result")["trx"]["operations"][0]

        lcc.set_step("Perform one call contract operation")
        contract_create_op_count = contract_call_op_count = transfer_op_count = 1
        bd_result = self.utils.perform_contract_call_operation(self, self.echo_acc0, self.get_pennie,
                                                               self.__database_api_identifier, contract_id,
                                                               transfer_op_count)
        lcc.log_info("Fill contract history with '{}' number of contract transfer operations".format(transfer_op_count))

        contract_call_operation = bd_result["trx"]["operations"][0]
        operations.append(contract_call_operation)
        operations.append(contract_create_operation)

        limit = contract_call_op_count + contract_create_op_count
        lcc.set_step("Get contract history. Limit: '{}'".format(limit))
        response = self.get_contract_history(contract_id, stop, limit, start)

        lcc.set_step("Check contract history to see added operation and store operation id")
        for i in range(limit):
            operation = operations[i]
            lcc.log_info("Check operation #{}:".format(i))
            require_that(
                "'contract history'",
                response["result"][i]["op"], is_list(operation)
            )

        lcc.set_step("Store operation id for 'stop' parameter")
        operation_id = response["result"][limit - 1]["id"]
        lcc.log_info("Stop operation id is '{}'".format(operation_id))

        lcc.set_step("Perform another operations")
        contract_call_op_count = transfer_op_count = get_random_integer_up_to_fifty
        bd_result = self.utils.perform_contract_call_operation(self, self.echo_acc0, self.get_pennie,
                                                               self.__database_api_identifier, contract_id,
                                                               transfer_op_count)
        lcc.log_info("Fill contract history with '{}' number of contract transfer operations".format(transfer_op_count))

        operations.remove(contract_create_operation)
        for i in range(transfer_op_count):
            contract_call_operation = bd_result["trx"]["operations"][0]
            operations.append(contract_call_operation)

        limit = contract_call_op_count + limit - contract_create_op_count
        stop = operation_id
        lcc.set_step("Get contract history. Stop: '{}', limit: '{}'".format(stop, limit))
        response = self.get_contract_history(contract_id, stop, limit, start)

        lcc.set_step("Check contract history to see added operations and store operation ids")
        for i in range(limit):
            lcc.log_info("Check operation #{}:".format(i))
            require_that(
                "'contract history'",
                response["result"][i]["op"], is_list(operations[i])
            )
            operation_ids.append(response["result"][i]["id"])

        stop = operation_id
        start = operation_ids[0]
        lcc.set_step("Get contract history. Stop: '{}', limit: '{}' and start: '{}'".format(stop, limit, start))
        results = self.get_contract_history(contract_id, stop, limit, start)["result"]

        lcc.set_step("Check contract history to see operations from the selected ids interval")
        for i, result in enumerate(results):
            lcc.log_info("Check operation #{}:".format(i))
            require_that_in(
                result,
                ["id"], is_str(operation_ids[i]),
                ["op"], is_list(operations[i])
            )
