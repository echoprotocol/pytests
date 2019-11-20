# -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, equal_to, is_str, check_that, has_entry, has_length, require_that, \
    is_true, is_integer

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_contract_logs'"
}


@lcc.tags("BUG ECHO-1588")
@lcc.disabled()
@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.prop("negative", "type")
@lcc.tags("api", "database_api", "database_api_contracts", "get_contract_logs")
@lcc.suite("Check work of method 'get_contract_logs'", rank=1)
class GetContractLogs(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.piggy = self.get_byte_code("piggy", "code")
        self.getPennie = self.get_byte_code("piggy", "pennieReturned()")

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'get_contract_logs'")
    def method_main_check(self, get_random_integer_up_to_ten):
        value_amount = get_random_integer_up_to_ten
        max_limit = 1000

        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy, self.__database_api_identifier,
                                                 value_amount=value_amount)

        lcc.set_step("Call contract method getPennie and get trx block number")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        block_num = broadcast_result["block_num"]
        _from = 1
        lcc.log_info("Method 'getPennie' performed successfully, block_num: '{}'".format(block_num))

        lcc.set_step("Get contract logs from '{}' block to max_limit '{}'".format(_from, max_limit))
        params = [{"contracts": [contract_id], "topics": [], "from_block": _from, "to_block": max_limit}]
        response_id = self.send_request(self.get_request("get_contract_logs", params), self.__database_api_identifier)
        response = self.get_response(response_id)
        logs = response["result"]
        lcc.log_info("Call method 'get_contract_logs' with params: '{}'".format(params))

        lcc.set_step("Check contract logs")
        require_that("'log has value'", bool(logs), is_true(), quiet=True)
        for log in logs:
            if check_that("contract_log", log[1], has_length(6)):
                contract_id_that_called = self.get_contract_id(log[1]["address"], address_format=True,
                                                               new_contract=False)
                require_that("contract_id", contract_id_that_called, equal_to(contract_id), quiet=True)
                log_values = log[1]["log"]
                for log_value in log_values:
                    if not self.validator.is_hex(log_value):
                        lcc.log_error("Wrong format of 'log_value', got: {}".format(log_value))
                    else:
                        lcc.log_info("'log_value' has correct format: hex")
                check_that_in(
                    log[1],
                    "data", is_str(),
                    "block_num", is_integer(),
                    "trx_num", is_integer(),
                    "op_num", is_integer(),
                    quiet=True
                )


@lcc.tags("BUG ECHO-1588")
@lcc.disabled()
@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_contracts", "get_contract_logs")
@lcc.suite("Positive testing of method 'get_contract_logs'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.piggy_contract = self.get_byte_code("piggy", "code")
        self.getPennie = self.get_byte_code("piggy", "pennieReturned()")
        self.dynamic_fields_contract = self.get_byte_code("dynamic_fields", "code")
        self.set_all_values = self.get_byte_code("dynamic_fields", "setAllValues(uint256,string)")

    def get_random_int(self, _to, _from=1):
        amount = random.randrange(_from, _to)
        if amount == _to:
            return self.get_random_int(_to=_to, _from=_from)
        return amount

    def get_head_block_number(self):
        self.utils.set_timeout_until_num_blocks_released(self, self.__database_api_identifier, print_log=False)
        response_id = self.send_request(self.get_request("get_dynamic_global_properties"),
                                        self.__database_api_identifier)
        head_block_number = self.get_response(response_id)["result"]["head_block_number"]
        lcc.log_info("head block number: {}".format(head_block_number))
        return head_block_number

    def get_contract_logs(self, contract_id=None, _list=[], _from=None, limit=100, params=None):
        if params is None:
            params = [{"contracts": [contract_id], "topics": _list, "from_block": _from, "to_block": limit}]
        response_id = self.send_request(self.get_request("get_contract_logs", params), self.__database_api_identifier)
        return self.get_response(response_id, log_response=True)["result"]

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

    @lcc.test("Check contract logs two identical contract calls")
    @lcc.depends_on("DatabaseApi.Contracts.GetContractLogs.GetContractLogs.method_main_check")
    def check_contract_logs_two_identical_contract_calls(self, get_random_integer):
        value_amount = get_random_integer
        call_count, _from, max_limit = 2, 1, 100

        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=value_amount)

        lcc.set_step("Call contract method getPennie two times and get trx block number")
        for i in range(call_count):
            operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                  bytecode=self.getPennie, callee=contract_id)
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                       log_broadcast=False)
            block_num = broadcast_result["block_num"]
            _from = 0
            lcc.log_info("Method #'{}' 'getPennie' performed successfully, block_num: '{}'".format(i, block_num))

        lcc.set_step("Get contract logs after two identical contract calls")
        params = [{"contracts": [contract_id], "topics": [], "from_block": _from, "to_block": max_limit}]
        get_contract_logs_results = self.get_contract_logs(params=params)
        lcc.log_info("Call method 'get_contract_logs' with params: '{}'".format(params))

        lcc.set_step("Check contract logs two identical contract calls")
        require_that("'log has value'", bool(get_contract_logs_results), is_true(), quiet=True)
        for i in range(len(get_contract_logs_results))[:-1]:
            check_that("'contract logs two identical contract calls are the same'",
                       get_contract_logs_results[i][1]["address"] == get_contract_logs_results[i + 1][1]["address"],
                       is_true())
            check_that("'contract logs two identical contract calls are the same'",
                       get_contract_logs_results[i][1]["log"] == get_contract_logs_results[i + 1][1]["log"], is_true())
            check_that("'contract logs two identical contract calls are the same'",
                       get_contract_logs_results[i][1]["data"] == get_contract_logs_results[i + 1][1]["data"],
                       is_true())

    @lcc.test("Check contract logs contract call that make two different logs")
    @lcc.depends_on("DatabaseApi.Contracts.GetContractLogs.GetContractLogs.method_main_check")
    def check_contract_logs_contract_call_that_make_two_different_logs(self, get_random_integer, get_random_string):
        int_param = get_random_integer
        string_param = get_random_string
        max_limit = 100

        lcc.set_step("Create 'dynamic_fields' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.dynamic_fields_contract,
                                                 self.__database_api_identifier)

        lcc.set_step("Call method of dynamic_fields contract: 'set_all_values'")
        int_param_code = self.get_byte_code_param(int_param, param_type=int)
        string_param_code = self.get_byte_code_param(string_param, param_type=str, offset="40")
        method_params = int_param_code + string_param_code
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.set_all_values + method_params,
                                                              callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        block_num = broadcast_result["block_num"]
        _from = 1
        lcc.log_info("Method 'set_all_values' performed successfully, block_num: '{}'".format(block_num))

        lcc.set_step("Get contract logs after two different contract calls")
        params = [contract_id, [], _from, max_limit]
        get_contract_logs_results = self.get_contract_logs(params=params)
        lcc.log_info("Call method 'get_contract_logs' with params: '{}'".format(params))

        lcc.set_step("Check contract logs contract call that make two different logs")
        require_that("'log has value'", bool(get_contract_logs_results), is_true(), quiet=True)
        for i in range(len(get_contract_logs_results))[:-1]:
            check_that(
                "'contract logs are not the same'",
                get_contract_logs_results[i] != get_contract_logs_results[i + 1],
                is_true()
            )

    @lcc.test("Check work of method with randomly valid parameters")
    @lcc.depends_on("DatabaseApi.Contracts.GetContractLogs.GetContractLogs.method_main_check")
    def check_contract_logs_from_random_valid_params(self, get_random_integer):
        value_amount = get_random_integer
        max_limit = 100
        contract_log_keys = ["address", "log", "data", "block_num", "trx_num", "op_num"]

        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=value_amount)

        lcc.set_step("Call contract method getPennie")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        lcc.log_info("Method 'getPennie' performed successfully")

        lcc.set_step("Get the head_block number of the next block")
        head_block_number = self.get_head_block_number()

        lcc.set_step("Get contract logs with random valid params")
        _from = self.get_random_int(_from=(head_block_number - max_limit + 1), _to=head_block_number)
        limit = self.get_random_int(_from=head_block_number - _from, _to=max_limit)
        contract_logs = self.get_contract_logs(contract_id=contract_id, _from=_from, limit=limit)
        lcc.log_info("Call method 'get_contract_logs' with params: from='{}', limit='{}'".format(_from, limit))

        lcc.set_step("Check contract logs")
        require_that("'log has value'", bool(contract_logs), is_true(), quiet=True)
        for log in contract_logs:
            if check_that("contract_logs", log[1], has_length(6)):
                for key in contract_log_keys:
                    require_that("contract_logs", log[1], has_entry(key), quiet=True)

    @lcc.test("Check contract logs from 'current_block'")
    @lcc.depends_on("DatabaseApi.Contracts.GetContractLogs.GetContractLogs.method_main_check")
    def check_contract_logs_from_current_block(self, get_random_integer):
        value_amount = get_random_integer
        max_limit = 100
        contract_log_keys = ["address", "log", "data", "block_num", "trx_num", "op_num"]
        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=value_amount)
        lcc.set_step("Call contract method getPennie")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        # todo: remove 'broadcasting of balance_freeze_operation'. Bug: ECHO-1588
        operation = self.echo_ops.get_balance_freeze_operation(echo=self.echo, account=self.echo_acc0,
                                                               value_amount=1, duration=90)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        # todo: remove '-1'. Bug: ECHO-1032
        current_block_num = broadcast_result["block_num"] - 1
        lcc.log_info("Method 'getPennie' performed successfully, current_block_num is '{}'".format(current_block_num))
        lcc.set_step("Get contract logs with 'from' param that equal to current_block_num")
        contract_logs = self.get_contract_logs(contract_id=contract_id, _from=current_block_num, limit=max_limit)
        lcc.log_info(
            "Call method 'get_contract_logs' with params: from='{}', limit='{}'".format(current_block_num, max_limit))
        lcc.set_step("Check contract logs")
        require_that("'log has value'", bool(contract_logs), is_true(), quiet=True)
        for log in contract_logs:
            if check_that("contract_logs", log[1], has_length(6)):
                for key in contract_log_keys:
                    require_that("contract_logs", log[1], has_entry(key), quiet=True)

    @lcc.test("Check work of the method outside the block in which the logs of the contract were recorded'")
    @lcc.depends_on("DatabaseApi.Contracts.GetContractLogs.GetContractLogs.method_main_check")
    def check_contract_logs_outside_block_with_logs(self, get_random_integer):
        value_amount = get_random_integer

        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=value_amount)

        lcc.set_step("Call contract method getPennie")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        # todo: remove '-1'. Bug: ECHO-1032
        current_block_num = broadcast_result["block_num"] - 1
        lcc.log_info("Method 'getPennie' performed successfully, current_block_num is '{}'".format(current_block_num))

        lcc.set_step("Get the head_block number of the next block")
        head_block_number = self.get_head_block_number()

        lcc.set_step("Get contract logs before block with logs")
        # todo: change limit to '1'. Bug: ECHO-1032
        limit = 2
        _from = 1
        contract_logs = self.get_contract_logs(contract_id=contract_id, _from=_from, limit=limit)
        lcc.log_info("Call method 'get_contract_logs' with params: from='{}', limit='{}'".format(_from, limit))

        lcc.set_step("Check contract logs")
        check_that("contract_logs", contract_logs, equal_to([]))

        lcc.set_step("Get contract logs after block with logs")
        _from = 1
        limit = self.get_random_int(_to=100)
        contract_logs = self.get_contract_logs(contract_id=contract_id, _from=_from, limit=limit)
        lcc.log_info("Call method 'get_contract_logs' with params: from='{}', limit='{}'".format(_from, limit))

        lcc.set_step("Check contract logs")
        check_that("contract_logs", contract_logs, equal_to([]))


@lcc.prop("negative", "type")
@lcc.tags("api", "database_api", "database_api_contracts", "get_contract_logs")
@lcc.suite("Negative testing of method 'get_contract_logs'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.piggy_contract = self.get_byte_code("piggy", "code")
        self.getPennie = self.get_byte_code("piggy", "pennieReturned()")

    def get_random_int(self, _to, _from=1):
        amount = random.randrange(_from, _to)
        if amount == _to:
            return self.get_random_int(_to=_to, _from=_from)
        return amount

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

    @lcc.test("Call method with negative parameter 'limit'")
    @lcc.depends_on("DatabaseApi.Contracts.GetContractLogs.GetContractLogs.method_main_check")
    def check_contract_logs_with_negative_parameter_limit(self, get_random_integer):
        value_amount = get_random_integer
        max_limit = 100

        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=value_amount)

        lcc.set_step("Call contract method getPennie")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        block_num = broadcast_result["block_num"]
        _from = 1
        lcc.log_info("Method 'getPennie' performed successfully")

        lcc.set_step("Get negative block number")
        negative_block_num = self.get_random_int(_to=max_limit) * -1
        lcc.log_info("negative block number: {}".format(negative_block_num))

        lcc.set_step("Get contract logs with 'limit' param is negative block number")
        params = [contract_id, _from, negative_block_num]
        response_id = self.send_request(self.get_request("get_contract_logs", params), self.__database_api_identifier)
        response = self.get_response(response_id, negative=True)
        lcc.log_info(
            "Call method 'get_contract_logs' with params: from='{}', limit='{}'".format(_from, negative_block_num))

        lcc.set_step("Check contract logs")
        check_that("'get_contract_logs' return error message with '{}' params".format(params),
                   response, has_entry("error"), quiet=True)

    @lcc.test("Call method with parameter 'limit' more than max value")
    @lcc.depends_on("DatabaseApi.Contracts.GetContractLogs.GetContractLogs.method_main_check")
    def check_contract_logs_with_parameter_limit_more_than_max_value(self, get_random_integer):
        value_amount = get_random_integer
        max_limit = 100

        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=value_amount)

        lcc.set_step("Call contract method getPennie")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        block_num = broadcast_result["block_num"]
        _from = 1
        lcc.log_info("Method 'getPennie' performed successfully")

        lcc.set_step("Get limit param more than max limit")
        more_than_max_limit = self.get_random_int(_from=max_limit, _to=value_amount)
        lcc.log_info("more than limit number: {}".format(more_than_max_limit))

        lcc.set_step("Get contract logs with 'limit' param is more than max limit")
        params = [contract_id, _from, more_than_max_limit]
        response_id = self.send_request(self.get_request("get_contract_logs", params), self.__database_api_identifier)
        response = self.get_response(response_id, negative=True)
        lcc.log_info(
            "Call method 'get_contract_logs' with params: from='{}', limit='{}'".format(_from, more_than_max_limit))

        lcc.set_step("Check contract logs")
        check_that("'get_contract_logs' return error message with '{}' params".format(params),
                   response, has_entry("error"), quiet=True)
