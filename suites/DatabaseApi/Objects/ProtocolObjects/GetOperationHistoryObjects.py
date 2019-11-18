# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_, require_that, has_length, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_account_history_operations'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "database_api", "database_api_objects", "get_objects")
@lcc.suite("Check work of method 'get_objects' (operation history object)", rank=1)
class GetOperationHistoryObjects(BaseTest):

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

    @lcc.test("Simple work of method 'get_account_history_operations'")
    def method_main_check(self):
        operation_id = self.echo.config.operation_ids.ACCOUNT_CREATE
        operation_history_obj = "{}0".format(self.get_object_type(self.echo.config.object_types.OPERATION_HISTORY))
        stop, start = operation_history_obj, operation_history_obj
        limit = 1
        lcc.set_step("Get account history operations")
        params = [self.echo_acc0, operation_id, start, stop, limit]
        response_id = self.send_request(self.get_request("get_account_history_operations", params),
                                        self.__history_api_identifier)
        get_account_history_operations_result = self.get_response(response_id)["result"]
        lcc.log_info(
            "Call method 'get_account_history_operations' with: account='{}', operation_id='{}', stop='{}', start='{}',"
            " limit='{}' parameters".format(self.echo_acc0, operation_id, stop, start, limit))

        lcc.set_step("Check response from method 'get_account_history_operations'")
        check_that(
            "'number of history results'",
            get_account_history_operations_result, has_length(limit),
            quiet=True
        )

        lcc.set_step("Get operation history object (get_objects method)")
        params = [get_account_history_operations_result[0]["id"]]
        response_id = self.send_request(self.get_request("get_objects", [params]),
                                        self.__database_api_identifier)
        get_object_result = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with params: {}".format(params))

        lcc.set_step("Check operation history object")
        for result in get_object_result:
            self.object_validator.validate_operation_history_object(self, result)
            check_that(
                "'operation id'",
                result["op"][0], is_(operation_id),
                quiet=True
            )

        lcc.set_step("Check the identity of returned results of api-methods: 'get_account_history_operations', 'get_objects'")
        require_that(
            'results',
            get_object_result, equal_to(get_account_history_operations_result),
            quiet=True
        )


