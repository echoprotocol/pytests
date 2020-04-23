# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_none, is_list, is_, has_entry, check_that_in, not_equal_to, \
    require_that, equal_to, greater_than_or_equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'set_subscribe_callback'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_subscriptions", "set_subscribe_callback")
@lcc.suite("Check work of method 'set_subscribe_callback'", rank=1)
class SetSubscribeCallback(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

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

    @lcc.test("Simple work of method 'set_subscribe_callback'")
    def method_main_check(self, get_random_integer):
        lcc.set_step("Set subscribe callback")
        subscription_callback_id = get_random_integer
        params = [subscription_callback_id, True]
        response_id = self.send_request(self.get_request("set_subscribe_callback", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check set subscribe callback")
        check_that(
            "'subscribe callback'",
            response["result"],
            is_none(),
        )


@lcc.tags("Manual testing with wsdump")
@lcc.disabled()
@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_subscriptions", "set_subscribe_callback")
@lcc.suite("Positive testing of method 'set_subscribe_callback'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.piggy_contract = self.get_byte_code("piggy", "code")
        self.break_piggy = self.get_byte_code("piggy", "breakPiggy()")

    def set_subscribe_callback(self, callback, notify_remove_create=False):
        params = [callback, notify_remove_create]
        response_id = self.send_request(self.get_request("set_subscribe_callback", params),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        if result is not None:
            raise Exception("Subscription not issued")
        lcc.log_info("Call method 'set_subscribe_callback', 'notify_remove_create'={}".format(notify_remove_create))

    def get_head_block_num(self):
        return self.echo.api.database.get_dynamic_global_properties()["head_block_number"]

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

    @lcc.test("Check notices of dynamic object '2.1.0'")
    @lcc.depends_on("API.DatabaseApi.Subscriptions.SetSubscribeCallback.SetSubscribeCallback.method_main_check")
    def check_global_property_object(self, get_random_integer):
        lcc.set_step("Set subscribe callback")
        subscription_callback_id = get_random_integer
        self.set_subscribe_callback(subscription_callback_id)

        lcc.set_step("Get object '2.1.0'")
        param = "2.1.0"
        response_id = self.send_request(self.get_request("get_objects", [[param]]), self.__database_api_identifier)
        response = self.get_response(response_id)["result"][0]
        lcc.log_info("Get 'global_property_object' and store info about it")

        lcc.set_step("Subscription check for object updates '2.1.0'")
        object_keys = list(response)[:]
        notice = self.get_notice(subscription_callback_id, object_id=param)

        lcc.set_step("Check object format")
        for i in range(len(notice)):
            check_that(
                "'updated object '{}''".format(param),
                notice,
                has_entry(
                    object_keys[i],
                ),
            )

        lcc.set_step("Get object '2.1.0' again")
        response_id = self.send_request(self.get_request("get_objects", [[param]]), self.__database_api_identifier)
        response = self.get_response(response_id)["result"][0]

        lcc.set_step("Check that updated object does not match previous")
        block_num = self.get_head_block_num()
        notice = self.get_notice(subscription_callback_id, object_id=param)
        response_last_irreversible_block_num = response["last_irreversible_block_num"]
        irreversible_matcher = not_equal_to(response_last_irreversible_block_num) if block_num > 15 \
            else equal_to(response_last_irreversible_block_num)
        check_that_in(
            notice,
            "head_block_number", not_equal_to(response["head_block_number"]),
            "head_block_id", not_equal_to(response["head_block_id"]),
            "time", greater_than_or_equal_to(response["time"]),
            "last_irreversible_block_num", irreversible_matcher,
        )

    @lcc.test("Check notices of created contract")
    @lcc.depends_on("API.DatabaseApi.Subscriptions.SetSubscribeCallback.SetSubscribeCallback.method_main_check")
    def check_contract_notices(self, get_random_integer):
        lcc.set_step("Set subscribe callback")
        subscription_callback_id = get_random_integer
        self.set_subscribe_callback(subscription_callback_id, notify_remove_create=True)

        lcc.set_step("Get notice to eliminate unnecessary")
        self.get_notice(subscription_callback_id, notices_list=True, log_response=False)
        lcc.log_info("Old notice received and skipped")

        lcc.set_step("Create 'piggy' contract in ECHO network")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, need_broadcast_result=True)

        lcc.set_step("Get notice about created contract")
        notice_about_created_contract = self.get_notice(subscription_callback_id,
                                                        object_id=self.get_implementation_object_type(
                                                            self.echo.config.implementation_object_types.TRANSACTION))

        lcc.set_step("Check notice about created contract")
        del contract_id.get("broadcast_result")["trx"]["operation_results"]
        del contract_id.get("broadcast_result")["trx"]["fees_collected"]
        check_that("'received notice'", contract_id.get("broadcast_result").get("trx"),
                   equal_to(notice_about_created_contract.get("trx")), quiet=True)

        lcc.set_step("Destroy the contract. Call 'breakPiggy' method")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.break_piggy,
                                                              callee=contract_id.get("contract_id"))
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        lcc.log_info("Contract method 'breakPiggy' is called successfully")

        lcc.set_step("Get notice about call contract")
        notice_about_contract_call = self.get_notice(subscription_callback_id,
                                                     object_id=self.get_implementation_object_type(
                                                         self.echo.config.implementation_object_types.TRANSACTION))

        lcc.set_step("Check notice about call contract")
        del broadcast_result.get("trx")["operation_results"]
        del broadcast_result.get("trx")["fees_collected"]
        check_that("'received notice'", broadcast_result.get("trx"),
                   equal_to(notice_about_contract_call.get("trx")), quiet=True)
