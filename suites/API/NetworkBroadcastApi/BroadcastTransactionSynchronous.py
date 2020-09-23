# -*- coding: utf-8 -*-
import json

from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, is_not_none

SUITE = {
    "description": "Method 'broadcast_transaction_synchronous'"
}


@lcc.prop("main", "type")
@lcc.prop("negative", "type")
@lcc.tags("api", "network_broadcast_api", "broadcast_transaction_synchronous")
@lcc.suite("Check work of method 'broadcast_transaction_synchronous'", rank=1)
class BroadcastTransactionSynchronous(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__network_broadcast_identifier = None
        self.echo_acc0 = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__network_broadcast_identifier = self.get_identifier("network_broadcast")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', network_broadcast='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier, self.__network_broadcast_identifier
            )
        )
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )

        lcc.log_info("Echo account are: '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'broadcast_transaction_synchronous'")
    def method_main_check(self, get_random_integer_up_to_ten, get_random_valid_account_name):
        transfer_amount = get_random_integer_up_to_ten
        account_names = get_random_valid_account_name

        lcc.set_step("Create new account")
        account_id = self.get_account_id(
            account_names, self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("New Echo account created, account_id='{}'".format(account_id))

        lcc.set_step("Create signed transaction of transfer operation")
        transfer_operation = self.echo_ops.get_transfer_operation(
            echo=self.echo, from_account_id=self.echo_acc0, amount=transfer_amount, to_account_id=account_id
        )
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        signed_tx = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, no_broadcast=True)
        lcc.log_info("Signed transaction of transfer operation created successfully")

        lcc.set_step("Get account balance before transfer transaction broadcast")
        response_id = self.send_request(
            self.get_request("get_account_balances", [account_id, [self.echo_asset]]), self.__database_api_identifier
        )
        account_balance = self.get_response(response_id)["result"][0]["amount"]
        lcc.log_info("'{}' account has '{}' in '{}' assets".format(account_id, account_balance, self.echo_asset))

        lcc.set_step("Broadcast signed transfer transaction and check that transaction broadcast")
        response_id = self.send_request(
            self.get_request("broadcast_transaction_synchronous", [signed_tx]), self.__network_broadcast_identifier
        )
        result = self.get_response(response_id)["result"]
        check_that("'broadcast_transaction_synchronous' result", result, is_not_none(), quiet=True)

        lcc.set_step("Get account balance after transfer transaction broadcast")
        response_id = self.send_request(
            self.get_request("get_account_balances", [account_id, [self.echo_asset]]), self.__database_api_identifier
        )
        updated_account_balance = self.get_response(response_id)["result"][0]["amount"]
        lcc.log_info(
            "'{}' account has '{}' in '{}' assets".format(account_id, updated_account_balance, self.echo_asset)
        )

        lcc.set_step("Check that transfer operation completed successfully")
        check_that(
            "account balance increased by transfered amount", updated_account_balance - account_balance,
            equal_to(transfer_amount)
        )


@lcc.prop("negative", "type")
@lcc.tags("api", "network_broadcast_api", "broadcast_transaction_synchronous")
@lcc.suite("Negative testing of method 'broadcast_transaction_synchronous'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__network_broadcast_identifier = None
        self.echo_acc0 = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__network_broadcast_identifier = self.get_identifier("network_broadcast")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', network_broadcast='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier, self.__network_broadcast_identifier
            )
        )
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo account are: '{}'".format(self.echo_acc0))

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

    def get_error_message(self, response_id):
        try:
            self.get_response(response_id)
        except Exception as e:
            ans = json.loads(str(e)[26:], strict=False)
            return ans["error"]["message"]

    @lcc.prop("type", "method")
    @lcc.test("Negative test 'broadcast_transaction_synchronous' with wrong signature")
    @lcc.depends_on(
        "API.NetworkBroadcastApi.BroadcastTransactionSynchronous.BroadcastTransactionSynchronous.method_main_check"
    )
    def check_broadcast_transaction_synchronous_with_wrong_signature(
        self, get_random_integer_up_to_ten, get_random_valid_account_name
    ):
        transfer_amount = get_random_integer_up_to_ten
        expected_message = "irrelevant signature included: Unnecessary signature(s) detected"
        account_names = get_random_valid_account_name

        lcc.set_step("Create new account")
        account_id = self.get_account_id(
            account_names, self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("New Echo account created, account_id='{}'".format(account_id))

        lcc.set_step("Create signed transaction of transfer operation")
        transfer_operation = self.echo_ops.get_transfer_operation(
            echo=self.echo,
            from_account_id=self.echo_acc0,
            amount=transfer_amount,
            to_account_id=account_id,
            signer=account_id
        )
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        signed_tx = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, no_broadcast=True)
        lcc.log_info("Signed transaction of 'transfer_operation' with wrong signer created successfully")
        lcc.set_step("Broadcast signed transfer transaction to get error message")
        response_id = self.send_request(
            self.get_request("broadcast_transaction_synchronous", [signed_tx]), self.__network_broadcast_identifier
        )
        error_message = self.get_error_message(response_id)
        check_that("message", error_message, equal_to(expected_message))

    @lcc.prop("type", "method")
    @lcc.test("Negative test 'broadcast_transaction_synchronous' with wrong expiration time")
    @lcc.depends_on(
        "API.NetworkBroadcastApi.BroadcastTransactionSynchronous.BroadcastTransactionSynchronous.method_main_check"
    )
    def check_broadcast_transaction_synchronous_with_wrong_expiration_time(
        self, get_random_integer_up_to_ten, get_random_valid_account_name
    ):
        transfer_amount = get_random_integer_up_to_ten
        expiration_time_offset = 10
        expected_message = "Assert Exception: now <= trx.expiration: "
        account_names = get_random_valid_account_name

        lcc.set_step("Create new account")
        account_id = self.get_account_id(
            account_names, self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("New Echo account created, account_id='{}'".format(account_id))

        lcc.set_step("Create signed transaction of transfer operation")
        transfer_operation = self.echo_ops.get_transfer_operation(
            echo=self.echo, from_account_id=self.echo_acc0, amount=transfer_amount, to_account_id=account_id
        )
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        datetime_str = self.get_datetime(global_datetime=True)
        datetime_str = self.subtract_from_datetime(datetime_str, seconds=expiration_time_offset)
        signed_tx = self.echo_ops.broadcast(
            echo=self.echo, list_operations=collected_operation, expiration=datetime_str, no_broadcast=True
        )
        lcc.log_info("Signed transaction of 'transfer_operation' with expiration time offset created successfully")

        lcc.set_step("Broadcast signed transfer transaction to get error message")
        response_id = self.send_request(
            self.get_request("broadcast_transaction_synchronous", [signed_tx]), self.__network_broadcast_identifier
        )
        error_message = self.get_error_message(response_id)
        check_that("message", error_message, equal_to(expected_message))
