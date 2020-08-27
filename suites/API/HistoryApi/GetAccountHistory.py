# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_, is_str, is_list, require_that, \
    require_that_in, has_length, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_account_history'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.prop("negative", "type")
@lcc.tags("api", "history_api", "get_account_history")
@lcc.suite("Check work of method 'get_account_history'", rank=1)
class GetAccountHistory(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__history_api_identifier = None
        self.echo_acc0 = None

    def setup_suite(self):
        super().setup_suite()
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

    @lcc.test("Simple work of method 'get_account_history'")
    def method_main_check(self):
        operation_history_obj = "{}0".format(self.get_object_type(self.echo.config.object_types.OPERATION_HISTORY))
        stop, start = operation_history_obj, operation_history_obj
        limit = 1
        lcc.set_step("Get account history")
        params = [self.echo_acc0, stop, limit, start]
        response_id = self.send_request(self.get_request("get_account_history", params), self.__history_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info(
            "Call method 'get_account_history' with: account='{}', stop='{}', limit='{}', start='{}' parameters".format(
                self.echo_acc0, stop, limit, start))

        lcc.set_step("Check response from method 'get_account_history'")
        results = response["result"]
        check_that(
            "'number of history results'",
            results, has_length(limit)
        )
        for result in results:
            self.object_validator.validate_operation_history_object(self, result)


@lcc.prop("positive", "type")
@lcc.tags("api", "history_api", "get_account_history")
@lcc.suite("Positive testing of method 'get_account_history'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__history_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None

    def get_account_history(self, account, stop, limit, start, negative=False):
        lcc.log_info("Get '{}' account history".format(account))
        params = [account, stop, limit, start]
        response_id = self.send_request(self.get_request("get_account_history", params), self.__history_api_identifier)
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

    @lcc.test("Check new account history")
    @lcc.depends_on("API.HistoryApi.GetAccountHistory.GetAccountHistory.method_main_check")
    def new_account_history(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name
        operation_history_obj = "{}0".format(self.get_object_type(self.echo.config.object_types.OPERATION_HISTORY))
        stop, start = operation_history_obj, operation_history_obj
        limit = 100
        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get new account history")
        response = self.get_account_history(new_account, stop, limit, start)

        lcc.set_step("Check new account history")
        expected_number_of_operations = 1
        require_that(
            "'new account history'",
            response["result"], has_length(expected_number_of_operations)
        )
        check_that(
            "'id single operation'",
            response["result"][0]["op"][0],
            is_(self.echo.config.operation_ids.ACCOUNT_CREATE)
        )

    @lcc.test("Check limit number of operations to retrieve")
    @lcc.depends_on("API.HistoryApi.GetAccountHistory.GetAccountHistory.method_main_check")
    def limit_operations_to_retrieve(self, get_random_valid_account_name, get_random_integer_up_to_hundred):
        new_account = get_random_valid_account_name
        operation_history_obj = "{}0".format(self.get_object_type(self.echo.config.object_types.OPERATION_HISTORY))
        stop, start = operation_history_obj, operation_history_obj
        min_limit = 1
        max_limit = 100
        default_account_create_operation, default_get_assets_operation = 1, 1
        operation_count = get_random_integer_up_to_hundred
        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Perform operations using a new account. Operation count equal to limit")
        self.utils.perform_transfer_operations(self, new_account, self.echo_acc0, self.__database_api_identifier,
                                               operation_count=operation_count, only_in_history=True)
        lcc.log_info("Fill account history with '{}' number of transfer operations".format(operation_count))

        lcc.set_step(
            "Check that count of new account history with the maximum limit is equal to operation_count")
        response = self.get_account_history(new_account, stop, max_limit, start)
        if operation_count == 1:
            operation_count = operation_count + default_get_assets_operation
        check_that(
            "'number of history results'",
            response["result"], has_length(operation_count + default_account_create_operation)
        )

        lcc.set_step("Check minimum list length account history")
        response = self.get_account_history(new_account, stop, min_limit, start)
        check_that(
            "'number of history results'",
            response["result"], has_length(min_limit)
        )

        lcc.set_step("Perform operations using a new account to create max_limit operations")
        operation_count = max_limit - operation_count - default_account_create_operation
        self.utils.perform_transfer_operations(self, new_account, self.echo_acc0, self.__database_api_identifier,
                                               operation_count=operation_count, only_in_history=True)
        lcc.log_info(
            "Fill account history with '{}' number of transfer operations".format(operation_count))

        lcc.set_step(
            "Check that count of new account history with the limit = max_limit is equal to max_limit")
        response = self.get_account_history(new_account, stop, max_limit, start)
        check_that(
            "'number of history results'",
            response["result"], has_length(max_limit)
        )

    @lcc.test("Check stop and start IDs of the operations in account history")
    @lcc.depends_on("API.HistoryApi.GetAccountHistory.GetAccountHistory.method_main_check")
    def stop_and_start_operations(self, get_random_integer, get_random_integer_up_to_hundred):
        transfer_amount_1 = get_random_integer
        transfer_amount_2 = get_random_integer_up_to_hundred
        operation_history_obj = "{}0".format(self.get_object_type(self.echo.config.object_types.OPERATION_HISTORY))
        stop, start = operation_history_obj, operation_history_obj
        operations = []
        operation_ids = []

        lcc.set_step("Perform one operation")
        operation_count = 1
        broadcast_result = self.utils.perform_transfer_operations(self, self.echo_acc0, self.echo_acc1,
                                                                  self.__database_api_identifier,
                                                                  transfer_amount=transfer_amount_1,
                                                                  operation_count=operation_count, only_in_history=True)
        lcc.log_info("Fill account history with '{}' number of transfer operations".format(operation_count))

        operations.append(broadcast_result["trx"]["operations"][0])

        limit = operation_count
        lcc.set_step("Get account history. Limit: '{}'".format(limit))
        response = self.get_account_history(self.echo_acc0, stop, limit, start)

        lcc.set_step("Check account history to see added operation and store operation id")
        require_that(
            "'account history'",
            response["result"][0]["op"], is_list(operations[0])
        )
        operation_id = response["result"][0]["id"]

        lcc.set_step("Perform another operations")
        operation_count = 3
        broadcast_result = self.utils.perform_transfer_operations(self, self.echo_acc0, self.echo_acc1,
                                                                  self.__database_api_identifier,
                                                                  transfer_amount=transfer_amount_2,
                                                                  operation_count=operation_count, only_in_history=True)
        lcc.log_info("Fill account history with '{}' number of transfer operations".format(operation_count))

        for i in range(operation_count):
            operations.append(broadcast_result["trx"]["operations"][i])

        limit = operation_count
        stop = operation_id
        lcc.set_step("Get account history. Stop: '{}', limit: '{}'".format(stop, limit))
        response = self.get_account_history(self.echo_acc0, stop, limit, start)

        lcc.set_step("Check account history to see added operations and store operation ids")
        operations.reverse()
        for i in range(limit):
            require_that(
                "'account history'",
                response["result"][i]["op"], is_list(operations[i])
            )
            operation_ids.append(response["result"][i]["id"])

        limit = operation_count + 1
        stop = operation_id
        start = operation_ids[0]
        lcc.set_step("Get account history. Stop: '{}', limit: '{}' and start: '{}'".format(stop, limit, start))
        results = self.get_account_history(self.echo_acc0, stop, limit, start)["result"]

        lcc.set_step("Check account history to see operations from the selected ids interval")
        for i, result in enumerate(results):
            lcc.log_info("Check operation #{}:".format(i))
            require_that_in(
                result,
                ["id"], is_str(operation_ids[i]),
                ["op"], is_list(operations[i])
            )


@lcc.prop("negative", "type")
@lcc.tags("api", "history_api", "get_account_history")
@lcc.suite("Negative testing of method 'get_account_history'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.echo_acc0 = None

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Check negative int value in get_account_history")
    @lcc.depends_on("API.HistoryApi.GetAccountHistory.GetAccountHistory.method_main_check")
    def check_negative_int_value_in_get_account_history(self):
        error_message = "Assert Exception: result >= 0: Invalid cast from negative number to unsigned"
        operation_history_obj = "{}0".format(self.get_object_type(self.echo.config.object_types.OPERATION_HISTORY))
        stop, start = operation_history_obj, operation_history_obj
        limit = -1
        lcc.set_step("Get 'get_account_history' with negative limit")
        params = [self.echo_acc0, stop, limit, start]
        response_id = self.send_request(self.get_request("get_account_history", params), self.__history_api_identifier)
        message = self.get_response(response_id, negative=True)["error"]["message"]
        check_that(
            "error_message",
            message, equal_to(error_message),
            quiet=True
        )
