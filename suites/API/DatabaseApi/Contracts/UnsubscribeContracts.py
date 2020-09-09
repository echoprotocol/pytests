# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, check_that_in, equal_to, has_length, is_, is_none, is_str, require_that

SUITE = {
    "description":
        "Methods: 'unsubscribe_contract_logs', 'get_objects' (contract balance & contract history"
        " & contract statistics objects)"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags(
    "api", "notice", "database_api", "database_api_contracts", "unsubscribe_contract_logs", "database_api_objects",
    "get_objects"
)
@lcc.suite("Check work of method 'unsubscribe_contract_logs'", rank=1)
class UnsubscribeContracts(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("piggy", "code")
        self.getPennie = self.get_byte_code("piggy", "pennieReturned()")

    def set_subscribe_callback(self, callback, notify_remove_create=False):
        params = [callback, notify_remove_create]
        response_id = self.send_request(
            self.get_request("set_subscribe_callback", params), self.__database_api_identifier
        )
        result = self.get_response(response_id)["result"]
        if result is not None:
            raise Exception("Subscription not issued")
        lcc.log_info("Call method 'set_subscribe_callback', 'notify_remove_create'={}".format(notify_remove_create))

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

    def setup_test(self, test):
        lcc.set_step("Setup for '{}'".format(str(test).split(".")[-1]))
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)
        lcc.log_info("Canceled all subscriptions successfully")

    def teardown_test(self, test, status):
        lcc.set_step("Teardown for '{}'".format(str(test).split(".")[-1]))
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)
        lcc.log_info("Canceled all subscriptions successfully")
        lcc.log_info("Test {}".format(status))

    def teardown_suite(self):
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'unsubscribe_contract_logs'")
    def method_main_check(self, get_random_integer, get_random_integer_up_to_ten):
        subscription_callback_id = get_random_integer
        value_amount = get_random_integer_up_to_ten

        lcc.set_step("Create 'piggy' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(
            self, self.echo_acc0, self.contract, self.__database_api_identifier, value_amount=value_amount
        )

        lcc.set_step("Subscribe to created contract")
        params = [subscription_callback_id, {
            contract_id: []
        }]
        response_id = self.send_request(
            self.get_request("subscribe_contract_logs", params), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        if response["result"]:
            raise Exception("Subscription to contract logs not issued")
        lcc.log_info("Subscription to contract logs successful")

        lcc.set_step("Call contract method getPennie")
        operation = self.echo_ops.get_contract_call_operation(
            echo=self.echo, registrar=self.echo_acc0, bytecode=self.getPennie, callee=contract_id
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        block_num = broadcast_result["block_num"]
        lcc.log_info("Method 'getPennie' performed successfully")

        lcc.set_step("Get notices about updates of created contract")
        contract_logs_notice = self.get_notice(subscription_callback_id, debug_mode=True)["params"][1][0]

        lcc.set_step("Check subscribe contracts log")
        for log in contract_logs_notice:
            if check_that("contract_log", log[1], has_length(6)):
                contract_id_that_called = self.get_contract_id(
                    log[1]["address"], address_format=True, new_contract=False
                )
                require_that("contract_id", contract_id_that_called, equal_to(contract_id), quiet=True)
                log_values = log[1]["log"]
                for log_value in log_values:
                    if not self.type_validator.is_hex(log_value):
                        lcc.log_error("Wrong format of 'log_value', got: {}".format(log_value))
                    else:
                        lcc.log_info("'log_value' has correct format: hex")
                check_that_in(
                    log[1],
                    "data",
                    is_str(),
                    "block_num",
                    is_(block_num),
                    "trx_num",
                    is_(0),
                    "op_num",
                    is_(0),
                    quiet=True
                )

        lcc.set_step("Unsubscribe created contract")
        response_id = self.send_request(
            self.get_request("unsubscribe_contract_logs", [subscription_callback_id]), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        check_that(
            "'unsubscribe contract logs'",
            response["result"],
            is_none(),
        )
        lcc.log_info("Unsubscription from contract logs successful")
