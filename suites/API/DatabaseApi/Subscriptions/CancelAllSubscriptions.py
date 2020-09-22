# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_none

SUITE = {
    "description": "Method 'cancel_all_subscriptions'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_subscriptions", "cancel_all_subscriptions")
@lcc.suite("Check work of method 'set_subscribe_callback'", rank=1)
class CancelAllSubscriptions(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'cancel_all_subscriptions'")
    def method_main_check(self):
        lcc.set_step("Cancell all subscriptions")
        response_id = self.send_request(self.get_request("cancel_all_subscriptions"), self.__database_api_identifier)
        response = self.get_response(response_id)

        if "result" not in response or response["result"] is not None:
            raise Exception("Can't cancel all cancel_all_subscriptions, got:\n{}".format(str(response)))
        check_that('response in None', response["result"], is_none())


@lcc.prop("positive", "type")
@lcc.tags("api", "notice", "database_api", "database_api_subscriptions", "cancel_all_subscriptions")
@lcc.suite("Positive testing of method 'cancel_all_subscriptions'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    # todo: uncomment. Manual testing.
    @lcc.disabled()
    @lcc.test("Check that 'cancel_all_subscriptions' cancels method 'set_subscribe_callback'")
    def cancel_set_block_applied_callback(self, get_random_integer):
        lcc.set_step("Set block applied callback")
        subscription_callback_id = get_random_integer
        params = [subscription_callback_id, True]
        response_id = self.send_request(
            self.get_request("set_subscribe_callback", params), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        if "result" not in response or response["result"] is not None:
            raise Exception("Can't cancel all cancel_all_subscriptions, got:\n{}".format(str(response)))
        check_that('response in None', response["result"], is_none())

        lcc.set_step("Check canceling of method 'set_block_applied_callback'")
        self.get_notice(subscription_callback_id, notices_list=True, log_response=True)

        lcc.set_step("Cancel subscriptions")
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)
        lcc.log_info("Canceled all subscriptions successfully")

        lcc.set_step("Check canceling of method 'set_subscribe_callback'")
        self.get_notice(subscription_callback_id, notices_list=True, log_response=True)
