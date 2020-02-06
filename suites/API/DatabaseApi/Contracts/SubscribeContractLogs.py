# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, check_that_in, equal_to, is_str, has_length, require_that, is_true, \
    has_entry, is_

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'subscribe_contract_logs'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.prop("negative", "type")
@lcc.tags("api", "notice", "database_api", "database_api_contracts", "subscribe_contract_logs")
@lcc.suite("Check work of method 'subscribe_contract_logs'", rank=1)
class SubscribeContractLogs(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("piggy", "code")
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
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)
        lcc.log_info("Canceled all subscriptions successfully")

    def teardown_suite(self):
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)
        lcc.log_info("Canceled all subscriptions successfully")
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'subscribe_contract_logs'")
    def method_main_check(self, get_random_integer, get_random_integer_up_to_ten):
        subscription_callback_id = get_random_integer
        value_amount = get_random_integer_up_to_ten

        lcc.set_step("Create 'piggy' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier,
                                                 value_amount=value_amount)

        lcc.set_step("Subscribe to created contract")
        params = [subscription_callback_id, {contract_id: []}]
        response_id = self.send_request(self.get_request("subscribe_contract_logs", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        if response["result"]:
            raise Exception("Subscription to contract logs not issued")
        lcc.log_info("Subscription to contract logs successful")

        lcc.set_step("Call contract method getPennie")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        block_num = broadcast_result["block_num"]
        lcc.log_info("Method 'getPennie' performed successfully")

        lcc.set_step("Get notices about updates of created contract")
        contract_logs_notice = self.get_notice(subscription_callback_id, debug_mode=True)["params"][1][0]

        lcc.set_step("Check subscribe contracts log")
        for log in contract_logs_notice:
            if check_that("contract_log", log[1], has_length(6)):
                contract_id_that_called = self.get_contract_id(log[1]["address"], address_format=True,
                                                               new_contract=False)
                require_that("contract_id", contract_id_that_called, equal_to(contract_id), quiet=True)
                log_values = log[1]["log"]
                for log_value in log_values:
                    if not self.type_validator.is_hex(log_value):
                        lcc.log_error("Wrong format of 'log_value', got: {}".format(log_value))
                    else:
                        lcc.log_info("'log_value' has correct format: hex")
                check_that_in(
                    log[1], "data", is_str(),
                    "block_num", is_(block_num),
                    "trx_num", is_(0),
                    "op_num", is_(0),
                    quiet=True
                )


@lcc.prop("positive", "type")
@lcc.tags("api", "notice", "database_api", "database_api_contracts", "subscribe_contract_logs")
@lcc.suite("Positive testing of method 'subscribe_contract_logs'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.piggy_contract = self.get_byte_code("piggy", "code")
        self.getPennie = self.get_byte_code("piggy", "pennieReturned()")
        self.greet = self.get_byte_code("piggy", "greet()")
        self.setAllValues_method_name = "setAllValues(uint256,string)"
        self.setString_method_name = "onStringChanged(string)"
        self.setUint256_method_name = "onUint256Changed(uint256)"
        self.dynamic_fields_contract = self.get_byte_code("dynamic_fields", "code")
        self.set_all_values = self.get_byte_code("dynamic_fields", self.setAllValues_method_name)

    def subscribe_contract_logs(self, callback, contract_id):
        params = [callback, {contract_id: []}]
        response_id = self.send_request(self.get_request("subscribe_contract_logs", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        if response["result"]:
            raise Exception("Subscription to contract logs not issued")
        lcc.log_info("Subscription to contract logs successful")

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
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    # todo: uncomment and add checks. BUG -1473
    @lcc.test("Check contract logs in notice with two transactions")
    @lcc.disabled()
    @lcc.depends_on("API.DatabaseApi.Contracts.SubscribeContractLogs.SubscribeContractLogs.method_main_check")
    def check_contract_logs_in_notices_with_two_transactions(self, get_random_integer):
        subscription_callback_id = value_amount = get_random_integer

        lcc.set_step("Create 'piggy' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=value_amount)

        lcc.set_step("Subscribe to created contract")
        self.subscribe_contract_logs(subscription_callback_id, contract_id)

        lcc.set_step("Perform twice calling contract method getPennie")
        operation_getpennie = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                        bytecode=self.getPennie, callee=contract_id)
        operation_greet = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                    bytecode=self.greet, callee=contract_id)
        for operation in [operation_getpennie, operation_greet]:
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=True,
                                    broadcast_with_callback=True)
        lcc.log_info("Method 'getPennie' performed successfully")

        lcc.set_step("First: Get notices about updates of created contract")
        notice = self.get_notice(subscription_callback_id)
        notice = self.get_notice(subscription_callback_id)

    @lcc.test("Check contract logs in notices two identical contract calls")
    @lcc.depends_on("API.DatabaseApi.Contracts.SubscribeContractLogs.SubscribeContractLogs.method_main_check")
    def check_contract_logs_in_notices_two_identical_contract_calls(self, get_random_integer):
        subscription_callback_id = value_amount = get_random_integer

        lcc.set_step("Create 'piggy' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=value_amount)

        lcc.set_step("Subscribe to created contract")
        self.subscribe_contract_logs(subscription_callback_id, contract_id)

        lcc.set_step("Call contract method getPennie")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        lcc.log_info("Method 'getPennie' performed successfully")

        lcc.set_step("First: Get notices about updates of created contract")
        contract_logs_notice_1 = self.get_notice(subscription_callback_id)
        id_notice_1 = contract_logs_notice_1[0][0]
        data_notice_1 = contract_logs_notice_1[0][1]

        lcc.set_step("Call contract method getPennie")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        lcc.log_info("Method 'getPennie' performed successfully")

        lcc.set_step("Second: Get notices about updates of created contract")
        contract_logs_notice_2 = self.get_notice(subscription_callback_id)
        id_notice_2 = contract_logs_notice_2[0][0]
        data_notice_2 = contract_logs_notice_2[0][1]

        lcc.set_step("Check that first and second notices are the same")
        check_that("'notices id'", id_notice_1, equal_to(id_notice_2))
        check_that("'notices address'", data_notice_1["address"], equal_to(data_notice_2["address"]))
        check_that("'notices log'", data_notice_1["log"], equal_to(data_notice_2["log"]))
        check_that("'notices data'", data_notice_1["data"], equal_to(data_notice_2["data"]))

    # todo: uncomment and add checks. BUG -1473
    @lcc.test("Check contract logs in notices contract call that make two different logs")
    @lcc.disabled()
    @lcc.depends_on("API.DatabaseApi.Contracts.SubscribeContractLogs.SubscribeContractLogs.method_main_check")
    def check_contract_logs_in_notice_contract_call_that_make_two_different_logs(self, get_random_integer,
                                                                                 get_random_string):
        subscription_callback_id = int_param = get_random_integer
        string_param = get_random_string

        lcc.set_step("Create 'dynamic_fields' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.dynamic_fields_contract,
                                                 self.__database_api_identifier)

        lcc.set_step("Subscribe to created contract")
        self.subscribe_contract_logs(subscription_callback_id, contract_id)

        lcc.set_step("Call method of dynamic_fields contract: 'set_all_values'")
        int_param_code = self.get_byte_code_param(int_param, param_type=int)
        string_param_code = self.get_byte_code_param(string_param, param_type=str, offset="40")
        method_params = int_param_code + string_param_code
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.set_all_values + method_params,
                                                              callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        lcc.log_info("Method 'set_all_values' performed successfully")

        lcc.set_step("Get notices about updates of created contract")
        contract_logs_notice_params = self.get_notice(subscription_callback_id)

        lcc.set_step("Check contract logs in notice with several logs")
        for i, log in enumerate(contract_logs_notice_params):
            lcc.log_info("Check log#'{}'".format(i))
            contract_id_that_called = self.get_contract_id(log[1]["address"], address_format=True, new_contract=False)
            require_that("contract_id", contract_id_that_called, equal_to(contract_id), quiet=True)
            log_values = log[1]["log"]
            for log_value in log_values:
                if not self.type_validator.is_hex(log_value):
                    lcc.log_error("Wrong format of 'log_value', got: {}".format(log_value))
                else:
                    lcc.log_info("'log_value' has correct format: hex")
            if not self.type_validator.is_hex(log[1]["data"]):
                lcc.log_error("Wrong format of 'data', got: {}".format(log[1]["data"]))
            else:
                lcc.log_info("'data' has correct format: hex")
        for i in range(len(contract_logs_notice_params))[:-1]:
            check_that(
                "'addresses in contract call result are the same'",
                contract_logs_notice_params[i][1]["address"] == contract_logs_notice_params[i + 1][1]["address"],
                is_true()
            )

        lcc.set_step("Check contract log value in notice")
        method_names_in_keccak_std = [self.get_keccak_standard_value(self.setUint256_method_name),
                                      self.get_keccak_standard_value(self.setString_method_name)]
        for i, log in enumerate(contract_logs_notice_params):
            check_that("'log value'", log[1]["log"][0], equal_to(method_names_in_keccak_std[i]), quiet=True)

        lcc.set_step("Check contract log data in notice")
        call_contract_params = [int_param, string_param]
        output_types = [int, str]
        log_data = self.get_contract_log_data(contract_logs_notice_params, output_types, log_format=True,
                                              debug_mode=True)
        for i, data in enumerate(log_data):
            lcc.log_info("Check data#'{}'".format(i))
            check_that("'converted 'data' from hex'", data, equal_to(call_contract_params[i]))


@lcc.prop("negative", "type")
@lcc.tags("api", "database_api", "database_api_contracts", "subscribe_contract_logs")
@lcc.suite("Negative testing of method 'subscribe_contract_logs'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("piggy", "code")

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
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Call method without parameters")
    @lcc.depends_on("API.DatabaseApi.Contracts.SubscribeContractLogs.SubscribeContractLogs.method_main_check")
    def check_contract_logs_without_params(self):
        lcc.set_step("Call method without params")
        response_id = self.send_request(self.get_request("subscribe_contract_logs"),
                                        self.__database_api_identifier)
        response = self.get_response(response_id, negative=True)
        check_that(
            "'subscribe_contract_logs' return error message",
            response, has_entry("error"), quiet=True,
        )

    @lcc.test("Call method with wrong parameters")
    @lcc.depends_on("API.DatabaseApi.Contracts.SubscribeContractLogs.SubscribeContractLogs.method_main_check")
    def check_contract_logs_with_wrong_paramss(self, get_random_integer, get_all_random_types):
        subscription_callback_id = value_amount = get_random_integer

        lcc.set_step("Create 'piggy' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier,
                                                 value_amount=value_amount)

        lcc.set_step("Call method with wrong amount of params")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            # todo: remove if. Bug: "ECHO-680"
            if i == 4:
                continue
            response_id = self.send_request(
                self.get_request("subscribe_contract_logs", [random_values[i]]),
                self.__database_api_identifier)
            response = self.get_response(response_id, negative=True)
            check_that(
                "'subscribe_contract_logs' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True
            )

        lcc.set_step("Call method with wrong param 'subscription_callback_id'")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            # todo: remove if. Bug: "ECHO-680"
            if i == 4:
                continue
            if type(random_values[i]) is int or type(random_values[i]) is float or type(random_values[i]) is bool:
                continue
            response_id = self.send_request(
                self.get_request("subscribe_contract_logs", [random_values[i], contract_id]),
                self.__database_api_identifier)
            response = self.get_response(response_id, negative=True)
            check_that(
                "'subscribe_contract_logs' return error message with '{}', '{}' params".format(random_type_names[i],
                                                                                               contract_id),
                response, has_entry("error"), quiet=True
            )

        lcc.set_step("Call method with wrong param 'contract_id'")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            # todo: remove if. Bug: "ECHO-680"
            if i == 4:
                continue
            if type(random_values[i]) is  dict:
                continue
            response_id = self.send_request(
                self.get_request("subscribe_contract_logs", [subscription_callback_id, random_values[i]]),
                self.__database_api_identifier)
            response = self.get_response(response_id, negative=True)
            check_that(
                "'subscribe_contract_logs' return error message with '{}', '{}' params".format(random_type_names[i],
                                                                                               contract_id),
                response, has_entry("error"), quiet=True
            )
