# -*- coding: utf-8 -*-
import random

from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import (
    check_that, check_that_in, equal_to, has_length, is_list, not_equal_to, require_that
)

SUITE = {
    "description": "Methods: 'get_account_addresses', 'get_objects' (account address object)"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.prop("negative", "type")
@lcc.tags(
    "api", "database_api", "database_api_accounts", "get_account_addresses", "database_api_objects", "get_objects"
)
@lcc.suite("Check work of methods: 'get_account_addresses', 'get_objects' (account address object)", rank=1)
class GetAccountAddresses(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of methods: 'get_account_addresses', 'get_objects' (account address object)")
    def method_main_check(self, get_random_valid_account_name, get_random_string):
        new_account = get_random_valid_account_name
        label = get_random_string
        _from = 0
        limit = 100

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(
            new_account, self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get addresses of created account in the network")
        params = [new_account, _from, limit]
        response_id = self.send_request(
            self.get_request("get_account_addresses", params), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_account_addresses' of new account")

        lcc.set_step("Check simple work of method 'get_account_addresses'")
        check_that("'new account addresses'", response["result"], is_list([]), quiet=True)

        lcc.set_step("Create account address for new account")
        self.utils.perform_account_address_create_operation(self, new_account, label, self.__database_api_identifier)
        lcc.log_info("Account address create operation for new account performed")

        lcc.set_step("Get updated list of addresses of created account in the network")
        params = [new_account, _from, limit]
        response_id = self.send_request(
            self.get_request("get_account_addresses", params), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_account_addresses' of new account")

        lcc.set_step("Check new account address object in method 'get_account_addresses'")
        result = response["result"][0]
        self.object_validator.validate_account_address_object(self, result)
        check_that_in(result, "owner", equal_to(new_account), "label", equal_to(label), quiet=True)

        lcc.set_step("Get account address object by id")
        params = [result["id"]]
        response_id = self.send_request(self.get_request("get_objects", [params]), self.__database_api_identifier)
        get_objects_results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with param: {}".format(params))

        lcc.set_step("Check length of received objects")
        require_that("'list of received objects'", get_objects_results, has_length(len(params)), quiet=True)

        lcc.set_step("Check the identity of returned results of api-methods: 'get_account_addresses', 'get_objects'")
        require_that('results', get_objects_results[0], equal_to(result), quiet=True)


@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_accounts", "get_account_addresses")
@lcc.suite("Positive testing of method 'get_account_addresses'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

    @staticmethod
    def proliferate_label_names(label_name_base, total_label_count):
        return ['{}{}'.format(label_name_base, 'A' * num) for num in range(total_label_count)]

    @staticmethod
    def get_random_amount(_to, _from=0):
        return round(random.uniform(_from, _to))

    def get_account_addresses(self, account_id, _from=0, limit=100):
        params = [account_id, _from, limit]
        response_id = self.send_request(
            self.get_request("get_account_addresses", params), self.__database_api_identifier
        )
        return self.get_response(response_id)

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Create multiple addresses for new account")
    @lcc.depends_on("API.DatabaseApi.Accounts.GetAccountAddresses.GetAccountAddresses.method_main_check")
    def create_multiple_addresses(self, get_random_valid_account_name, get_random_string):
        new_account = get_random_valid_account_name
        total_addresses_count = 2

        lcc.set_step("Generate address labels")
        label_name_base = get_random_string
        generated_labels = self.proliferate_label_names(label_name_base, total_addresses_count)
        lcc.log_info('Generated address labels: {}'.format(generated_labels))

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(
            new_account, self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Create two account address for new account")
        for i in range(total_addresses_count):
            self.utils.perform_account_address_create_operation(
                self, new_account, generated_labels[i], self.__database_api_identifier
            )
            lcc.log_info("Account address create operation #'{}' for new account performed".format(i))

        lcc.set_step("Get list of addresses of created account in the network")
        response = self.get_account_addresses(new_account)
        lcc.log_info("Call method 'get_account_addresses' of new account")

        lcc.set_step("Check that two account addresses objects created")
        result = response["result"]
        require_that("'account address count'", result, has_length(total_addresses_count))

        address_obj1 = result[0]
        address_obj2 = result[1]
        require_that("'account address1 label1'", address_obj1["label"], equal_to(generated_labels[0]))
        require_that("'account address2 label2'", address_obj2["label"], equal_to(generated_labels[1]))
        check_that_in(
            address_obj1,
            "id",
            not_equal_to(address_obj2["id"]),
            "owner",
            equal_to(address_obj2["owner"]),
            "label",
            not_equal_to(address_obj2["label"]),
            "address",
            not_equal_to(address_obj2["address"]),
        )

    @lcc.test("Compare response from 'get_account_addresses' and 'get_objects' impl_account_address_object_type")
    @lcc.depends_on("API.DatabaseApi.Accounts.GetAccountAddresses.GetAccountAddresses.method_main_check")
    def compare_with_method_get_objects(self, get_random_valid_account_name, get_random_string):
        new_account = get_random_valid_account_name
        label = get_random_string

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(
            new_account, self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Create account address for new account. Store account address object")
        broadcast_result = self.utils.perform_account_address_create_operation(
            self, new_account, label, self.__database_api_identifier
        )
        account_address_object = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("Account address create operation for new account performed. Account address object stored")

        lcc.set_step("Get addresses of created account in the network")
        response = self.get_account_addresses(new_account)["result"][0]
        lcc.log_info("Call method 'get_account_addresses' of new account")

        lcc.set_step("Get objects 'impl_account_address_object_type'")
        param = [[account_address_object]]
        response_id = self.send_request(self.get_request("get_objects", param), self.__database_api_identifier)
        response_from_get_objects = self.get_response(response_id)["result"][0]
        lcc.log_info("Call method 'get_objects' with account address object of new account")

        lcc.set_step("Compare address object from 'get_account_addresses' and 'get_objects'")
        if check_that("account_addresses", response, has_length(5)):
            check_that_in(
                response,
                "id",
                equal_to(response_from_get_objects["id"]),
                "owner",
                equal_to(response_from_get_objects["owner"]),
                "label",
                equal_to(response_from_get_objects["label"]),
                "address",
                equal_to(response_from_get_objects["address"]),
                "extensions",
                equal_to(response_from_get_objects["extensions"]),
            )


@lcc.prop("negative", "type")
@lcc.tags("api", "database_api", "database_api_accounts", "get_account_addresses")
@lcc.suite("Negative testing of method 'get_account_addresses'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Check negative int value in get_account_addresses")
    @lcc.depends_on("API.DatabaseApi.Accounts.GetAccountAddresses.GetAccountAddresses.method_main_check")
    def check_negative_int_value_in_get_account_addresses(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name
        error_message = "Assert Exception: result >= 0: Invalid cast from negative number to unsigned"
        _from = -10
        limit = 100

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(
            new_account, self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get 'get_account_addresses' with negative from")
        params = [new_account, _from, limit]
        response_id = self.send_request(
            self.get_request("get_account_addresses", params), self.__database_api_identifier
        )
        message = self.get_response(response_id, negative=True)["error"]["message"]
        check_that("error_message", message, equal_to(error_message), quiet=True)

        _from = 0
        limit = -100

        lcc.set_step("Get 'get_account_addresses' with negative limit")
        params = [new_account, _from, limit]
        response_id = self.send_request(
            self.get_request("get_account_addresses", params), self.__database_api_identifier
        )
        message = self.get_response(response_id, negative=True)["error"]["message"]
        check_that("error_message", message, equal_to(error_message), quiet=True)
