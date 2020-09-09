# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, is_true

SUITE = {
    "description": "Method 'get_btc_address'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "sidechain", "sidechain_bitcoin", "database_api_sidechain_bitcoin", "get_btc_address")
@lcc.suite("Check work of method 'get_btc_address'", rank=1)
class GetBtcAddress(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_ethereum()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier
            )
        )

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'get_btc_address'")
    def method_main_check(self, get_random_valid_account_name):
        new_account_name = get_random_valid_account_name
        backup_address = 'mipcBbFg9gMiCh81Kj8tqqdgoZub1ZJRfn'
        lcc.set_step("Create and get new account")
        new_account_id = self.get_account_id(
            new_account_name, self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account_id))

        lcc.set_step("Perform sidechain_btc_create_address_operation")
        operation = self.echo_ops.get_sidechain_btc_create_address_operation(
            echo=self.echo, account=new_account_id, backup_address=backup_address
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=1):
            lcc.log_error("'sidechain_btc_create_address_operation' fallen while broadcast")
        else:
            lcc.log_info("'sidechain_btc_create_address_operation' broadcasted successfully.")
        lcc.set_step("Call 'Get_btc_address' method and check its result")
        response_id = self.send_request(
            self.get_request("get_btc_address", [new_account_id]), self.__database_api_identifier
        )
        result = self.get_response(response_id)["result"]

        if not self.type_validator.is_btc_address_id(result["id"]):
            lcc.log_error("Wrong format of 'btc_address_id', got: {}".format(result["id"]))
        else:
            lcc.log_info("Correct format of btc_address_id.")

        check_that("account", result["account"], equal_to(new_account_id), quiet=True)

        deposit_address = result["deposit_address"]["address"]
        if not self.type_validator.is_string(deposit_address):
            lcc.log_error("Wrong format of 'deposit_address', got: {}".format(deposit_address))
        else:
            lcc.log_info("Correct format of 'deposit_address', got string")

        for committee_member_info in result["committee_member_ids_in_script"]:
            if not self.type_validator.is_btc_public_key(committee_member_info[1]):
                lcc.log_error("Wrong format of 'btc_public_key', got: {}".format(committee_member_info[1]))
            if not self.type_validator.is_account_id(committee_member_info[0]):
                lcc.log_error("Wrong format of 'committee_member_account_id', got: {}".format(committee_member_info[0]))
        lcc.log_info("All 'btc_public_key' has correct format, got account_id")
        lcc.log_info("All 'committee_member_account_id' has correct format, got btc_public_key")

        check_that("is_relevant", result["is_relevant"], is_true(), quiet=True)

        check_that("backup_address", result["backup_address"], equal_to(backup_address), quiet=True)


@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "sidechain", "sidechain_bitcoin", "database_api_sidechain_bitcoin", "get_btc_address")
@lcc.suite("Positive check work of method 'get_btc_address'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_ethereum()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier
            )
        )

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'get_btc_address'")
    def method_main_check(self, get_random_valid_account_name):
        new_account_name = get_random_valid_account_name
        backup_address = 'mipcBbFg9gMiCh81Kj8tqqdgoZub1ZJRfn'
        lcc.set_step("Create and get new account")
        new_account_id = self.get_account_id(
            new_account_name, self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account_id))

        lcc.set_step("Perform sidechain_btc_create_address_operation")
        operation = self.echo_ops.get_sidechain_btc_create_address_operation(
            echo=self.echo, account=new_account_id, backup_address=backup_address
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=1):
            lcc.log_error("'sidechain_btc_create_address_operation' fallen while broadcast")
        else:
            lcc.log_info("'sidechain_btc_create_address_operation' broadcasted successfully.")
        lcc.set_step("Call 'Get_btc_address' method and check its result")
        response_id = self.send_request(
            self.get_request("get_btc_address", [new_account_name]), self.__database_api_identifier
        )
        result = self.get_response(response_id)["result"]

        if not self.type_validator.is_btc_address_id(result["id"]):
            lcc.log_error("Wrong format of 'btc_address_id', got: {}".format(result["id"]))
        else:
            lcc.log_info("Correct format of btc_address_id.")

        check_that("account", result["account"], equal_to(new_account_id), quiet=True)

        deposit_address = result["deposit_address"]["address"]
        if not self.type_validator.is_string(deposit_address):
            lcc.log_error("Wrong format of 'deposit_address', got: {}".format(deposit_address))
        else:
            lcc.log_info("Correct format of 'deposit_address', got string")

        for committee_member_info in result["committee_member_ids_in_script"]:
            if not self.type_validator.is_btc_public_key(committee_member_info[1]):
                lcc.log_error("Wrong format of 'btc_public_key', got: {}".format(committee_member_info[1]))
            if not self.type_validator.is_account_id(committee_member_info[0]):
                lcc.log_error("Wrong format of 'committee_member_account_id', got: {}".format(committee_member_info[0]))
        lcc.log_info("All 'btc_public_key' has correct format, got account_id")
        lcc.log_info("All 'committee_member_account_id' has correct format, got btc_public_key")

        check_that("is_relevant", result["is_relevant"], is_true(), quiet=True)

        check_that("backup_address", result["backup_address"], equal_to(backup_address), quiet=True)
