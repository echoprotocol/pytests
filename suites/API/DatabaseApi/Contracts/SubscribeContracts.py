# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_none, check_that_in, has_length, is_integer, is_, equal_to, \
    is_list, require_that

from common.base_test import BaseTest

SUITE = {
    "description": "Methods: 'subscribe_contracts', 'get_objects' (contract balance & contract history"
    " & contract statistics objects)"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags(
    "api", "notice", "database_api", "database_api_contracts", "subscribe_contracts",
    "database_api_objects", "get_objects"
)
@lcc.suite("Check work of method 'subscribe_contracts'", rank=1)
class SubscribeContracts(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet()")

    def set_subscribe_callback(self, callback, notify_remove_create=False):
        params = [callback, notify_remove_create]
        response_id = self.send_request(self.get_request("set_subscribe_callback", params),
                                        self.__database_api_identifier)
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
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'subscribe_contracts'")
    def method_main_check(self, get_random_integer):
        lcc.set_step("Set subscribe callback")
        subscription_callback_id = get_random_integer
        self.set_subscribe_callback(subscription_callback_id)

        lcc.set_step("Create 'Piggy' contract in the Echo network")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier,
                                                 value_amount=10)

        lcc.set_step("Subscribe created contract")
        response_id = self.send_request(self.get_request("subscribe_contracts", [[contract_id]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check subscribe contracts")
        check_that(
            "'subscribe contracts'",
            response["result"],
            is_none(),
        )

        lcc.set_step("Call 'greet' method")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.greet, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get notices about updates of created contract")
        notice = self.get_notice(subscription_callback_id, object_id=self.get_implementation_object_type(
            self.echo.config.implementation_object_types.CONTRACT_HISTORY))

        lcc.set_step("Check notice 'subscribe_contracts'")
        self.object_validator.validate_contract_history_object(self, notice)
        check_that_in(
            notice,
            "sequence", is_integer(),
            "next", is_("{}{}".format(
                self.get_implementation_object_type(
                    self.echo.config.implementation_object_types.CONTRACT_HISTORY),
                str((int(notice["id"].split('.')[2]) - 1)))),
            "extensions", is_list(),
            quiet=True
        )


@lcc.prop("positive", "type")
@lcc.tags(
    "api", "notice", "database_api", "database_api_contracts", "subscribe_contracts",
    "database_api_objects", "get_objects"
)
@lcc.suite("Positive testing of methods: 'subscribe_contracts', 'get_objects'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__history_api_identifier = None
        self.echo_acc0 = None
        self.piggy_contract = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet()")
        self.get_pennie = self.get_byte_code("piggy", "pennieReturned()")
        self.break_piggy = self.get_byte_code("piggy", "breakPiggy()")
        self.create_contract = self.get_byte_code("contract_create_contract", "code")
        self.deploy_contract = self.get_byte_code("contract_create_contract", "deploy_contract()")
        self.get_creator = self.get_byte_code("contract_create_contract", "created_contract")["creator()"]
        self.tr_asset_to_creator = self.get_byte_code("contract_create_contract", "created_contract")[
            "tr_asset_to_creator()"]

    def set_subscribe_callback(self, callback, notify_remove_create=False):
        params = [callback, notify_remove_create]
        response_id = self.send_request(self.get_request("set_subscribe_callback", params),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        if result is not None:
            raise Exception("Subscription not issued")
        lcc.log_info("Call method 'set_subscribe_callback', 'notify_remove_create'={}".format(notify_remove_create))

    def get_contract_history(self, contract_id, stop="1.6.0", start="1.6.0", limit=1, log_response=False):
        params = [contract_id, stop, limit, start]
        response_id = self.send_request(self.get_request("get_contract_history", params), self.__history_api_identifier)
        response = self.get_response(response_id, log_response=log_response)
        lcc.log_info("Call method 'get_contract_history' with: contract_id='{}', stop='{}', limit='{}', start='{}' "
                     "parameters".format(contract_id, stop, limit, start))
        return response

    @staticmethod
    def check_contract_history_objs_in_notice(response, notice, contract_id):
        counter = 0
        for i, operation_history in enumerate(response):
            operation_history_id = operation_history["id"]
            notice_id = notice[i]["id"]
            if "contract" not in notice[i]:
                if counter != len(notice):
                    counter += 1
                    continue
                lcc.log_error("No needed operation in the notice, got: '{}'".format(notice))
            notice_contract_id = notice[i]["contract"]
            notice_operation_history_id = notice[i]["operation_id"]
            if notice_operation_history_id != operation_history_id:
                if counter != len(response):
                    counter += 1
                    continue
                lcc.log_error("No '{}' operation in the notice".format(operation_history_id))
            if notice_contract_id != contract_id:
                lcc.log_error("Notice has incorrect contract id, got '{}', but need '{}'".format(notice_contract_id,
                                                                                                 contract_id))
            lcc.log_info("Received and check notice with id '{}'".format(notice_id))
            lcc.log_info("Notice has correct contract id: '{}'".format(notice_contract_id))
            lcc.log_info("Operations are the same: notice has operation '{}' like contract history='{}'".format(
                notice_operation_history_id, operation_history_id))
            break

    def check_balance_and_statistic_objs_in_notice(self, notices, contract_id, contract_balance, asset_type,
                                                   expected_statistic=True):
        counter = 0
        expected_objs = [
            self.get_implementation_object_type(self.echo.config.implementation_object_types.CONTRACT_BALANCE),
            self.get_implementation_object_type(self.echo.config.implementation_object_types.CONTRACT_STATISTICS)]
        if not expected_statistic:
            expected_objs = expected_objs[0]
        for i, notice in enumerate(notices):
            if "owner" not in notice:
                if counter != len(notices):
                    counter += 1
                    continue
            lcc.log_info("Check notice #'{}' with id='{}'".format(str(i), notice["id"]))
            require_that(
                "'owner'",
                notice["owner"], equal_to(contract_id),
                quiet=True
            )
            if not notice["id"].startswith(expected_objs[i]):
                if counter != len(notice):
                    counter += 1
                    continue
                lcc.log_error("No '{}' object in the notice".format(notice["id"]))
            if notice["id"].startswith(expected_objs[0]):
                check_that_in(
                    notice,
                    "asset_type", equal_to(asset_type),
                    "balance", equal_to(contract_balance),
                    quiet=True
                )

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

    @lcc.test("Check notices of contract and compare with get_objects method")
    @lcc.depends_on("API.DatabaseApi.Contracts.SubscribeContracts.SubscribeContracts.method_main_check")
    def check_different_types_of_contract_notices(self, get_random_integer):
        value_amount = 10
        value_asset_id = self.echo_asset

        lcc.set_step("Set subscribe callback")
        subscription_callback_id = get_random_integer
        self.set_subscribe_callback(subscription_callback_id)

        lcc.set_step("Create 'Piggy' contract in the Echo network")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=value_amount,
                                                 value_asset_id=value_asset_id)

        lcc.set_step("Subscribe created contract")
        response_id = self.send_request(self.get_request("subscribe_contracts", [[contract_id]]),
                                        self.__database_api_identifier)
        self.get_response(response_id)

        lcc.set_step("Call 'greet' method")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.greet, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get notices about updates of created contract")
        notice = self.get_notice(subscription_callback_id, object_id=self.get_implementation_object_type(
            self.echo.config.implementation_object_types.CONTRACT_HISTORY))

        lcc.set_step("Get contract history")
        operation_history_id = self.get_contract_history(contract_id)["result"][0]["id"]

        lcc.set_step("Check notice about updated contract history")
        check_that_in(
            notice,
            "contract", equal_to(contract_id),
            "operation_id", equal_to(operation_history_id),
            quiet=True
        )

        lcc.set_step("Call 'getPennie' method")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.get_pennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        expected_contract_balance = value_amount - 1

        lcc.set_step("Get notices about updates of created contract")
        notice_1 = self.get_notice(subscription_callback_id, notices_list=True)
        notice_2 = self.get_notice(subscription_callback_id, notices_list=True)

        lcc.set_step("Get contract history")
        limit = 2
        response = self.get_contract_history(contract_id, limit=limit)["result"]

        lcc.set_step("Check notice about updated contract history")
        self.check_contract_history_objs_in_notice(response, notice_1, contract_id)

        lcc.set_step("Check notice about updated contract balance and statistics")
        self.check_balance_and_statistic_objs_in_notice(notice_2, contract_id, expected_contract_balance,
                                                        value_asset_id)

        lcc.set_step("Get contract balance and contract statistics objects by id")
        params = [notice_part["id"] for notice_part in notice_2]
        response_id = self.send_request(self.get_request("get_objects", [params]),
                                        self.__database_api_identifier)
        get_objects_results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with param: {}".format(params))

        lcc.set_step("Check length of received objects")
        require_that(
            "'list of received objects'",
            get_objects_results, has_length(len(params)),
            quiet=True
        )
        contract_balance_id_pattern = self.get_implementation_object_type(
            self.echo.config.implementation_object_types.CONTRACT_BALANCE)
        for i, contract_balance_statistics in enumerate(get_objects_results):
            if contract_balance_statistics["id"].startswith(contract_balance_id_pattern):
                lcc.set_step("Check contract balance object : {}".format(params[i]))
                self.object_validator.validate_contract_balance_object(self, contract_balance_statistics)
            else:
                lcc.set_step("Check contract statistics object: {}".format(params[i]))
                self.object_validator.validate_contract_statistics_object(self, contract_balance_statistics)

        lcc.set_step("Check the identity of returned results of api-methods: 'subscribe_contracts', 'get_objects'")
        require_that(
            'results',
            get_objects_results, equal_to(notice_2),
            quiet=True
        )

        lcc.set_step("Call 'breakPiggy' method")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.break_piggy, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get notices about updates of created contract")
        notice = self.get_notice(subscription_callback_id, notices_list=True)

        lcc.set_step("Get contract history")
        limit = 2
        response = self.get_contract_history(contract_id, limit=limit)["result"]

        lcc.set_step("Check notice about updated contract history")
        self.check_contract_history_objs_in_notice(response, notice, contract_id)

        lcc.set_step("Get contract history object by id")
        params = [notice_part["id"] for notice_part in notice]
        response_id = self.send_request(self.get_request("get_objects", [params]),
                                        self.__database_api_identifier)
        get_objects_results = self.get_response(response_id, log_response=True)["result"]
        lcc.log_info("Call method 'get_objects' with param: {}".format(params))

        lcc.set_step("Check length of received objects")
        require_that(
            "'list of received objects'",
            get_objects_results, has_length(len(params)),
            quiet=True
        )

        for i, contract_history_object in enumerate(get_objects_results):
            lcc.set_step("Check contract history object #{}: {}".format(i, params[i]))

            self.object_validator.validate_contract_history_object(self, contract_history_object)

        lcc.set_step("Check the identity of returned results of api-methods: 'subscribe_contracts', 'get_objects'")
        require_that(
            'results',
            get_objects_results, equal_to(notice),
            quiet=True
        )

    @lcc.test("Check notices of contract created by another contract")
    @lcc.depends_on("API.DatabaseApi.Contracts.SubscribeContracts.SubscribeContracts.method_main_check")
    def check_notices_of_contract_created_by_another_contract(self, get_random_integer):
        lcc.set_step("Set subscribe callback")
        subscription_callback_id = get_random_integer
        self.set_subscribe_callback(subscription_callback_id)

        lcc.set_step("Create 'contract_create_contract' contract in the Echo network")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.create_contract,
                                                 self.__database_api_identifier)

        lcc.set_step("Call 'deploy_contract' method")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.deploy_contract, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        created_contract_id = self.get_contract_output(contract_result, output_type="contract_address")
        lcc.log_info("Output is '{}'".format(created_contract_id))

        lcc.set_step("Subscribe contract created by another contract")
        response_id = self.send_request(self.get_request("subscribe_contracts", [[created_contract_id]]),
                                        self.__database_api_identifier)
        self.get_response(response_id)

        lcc.set_step("Call 'get_creator' method of contract created by another contract")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.get_creator, callee=created_contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get notices about updates of contract created by another contract")
        notice = self.get_notice(subscription_callback_id, object_id=self.get_implementation_object_type(
            self.echo.config.implementation_object_types.CONTRACT_HISTORY))

        lcc.set_step("Get contract history")
        operation_history_id = self.get_contract_history(created_contract_id)["result"][0]["id"]

        lcc.set_step("Check notice about updated contract history created by another contract")
        check_that_in(
            notice,
            "contract", equal_to(created_contract_id),
            "operation_id", equal_to(operation_history_id),
            quiet=True
        )

        lcc.set_step("Call 'tr_asset_to_creator' method of created contract")
        value_amount = 1
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.tr_asset_to_creator,
                                                              callee=created_contract_id, value_amount=value_amount)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get notices about updates of contract created by another contract")
        notice = self.get_notice(subscription_callback_id, notices_list=True)

        lcc.set_step("Get contract history")
        limit = 2
        response = self.get_contract_history(created_contract_id, limit=limit)["result"]

        lcc.set_step("Check notice about updated contract history created by another contract")
        self.check_contract_history_objs_in_notice(response, notice, created_contract_id)

        lcc.set_step("Check notice about contract balance")
        expected_contract_balance = value_amount
        value_asset_id = self.echo_asset
        self.check_balance_and_statistic_objs_in_notice(notice, created_contract_id, expected_contract_balance,
                                                        value_asset_id, expected_statistic=False)
