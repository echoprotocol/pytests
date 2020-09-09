# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, has_entry, is_bool, is_false, is_true, require_that

SUITE = {
    "description": "Method 'is_public_key_registered'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.prop("negative", "type")
@lcc.tags("api", "database_api", "database_api_keys", "is_public_key_registered")
@lcc.suite("Check work of method 'is_public_key_registered'", rank=1)
class IsPublicKeyRegistered(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'is_public_key_registered'")
    def method_main_check(self):
        lcc.set_step("Generate public key")
        public_key = self.generate_keys()[1]
        lcc.log_info("Public key generated successfully: '{}'".format(public_key))

        lcc.set_step("Verify generated public key")
        response_id = self.send_request(
            self.get_request("is_public_key_registered", [public_key]), self.__database_api_identifier
        )
        result = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'is_public_key_registered' with param: '{}'".format(public_key))

        lcc.set_step("Check simple work of method 'vested balance'")
        check_that("'public key' result", result, is_bool(), quiet=True)


@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_keys", "is_public_key_registered")
@lcc.suite("Positive testing of method 'is_public_key_registered'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}',".format(
                self.__database_api_identifier, self.__registration_api_identifier
            )
        )

    @lcc.prop("type", "method")
    @lcc.test("Register new account and check it's public key")
    @lcc.depends_on("API.DatabaseApi.Keys.IsPublicKeyRegistered.IsPublicKeyRegistered.method_main_check")
    def register_new_account(self, get_random_valid_account_name, get_random_integer):
        callback = get_random_integer
        new_account = get_random_valid_account_name
        evm_address = None

        lcc.set_step("Generate public key")
        public_key = self.generate_keys()[1]
        lcc.log_info("Public key generated successfully: '{}'".format(public_key))

        lcc.set_step("Verify generated public key before account registration")
        response_id = self.send_request(
            self.get_request("is_public_key_registered", [public_key]), self.__database_api_identifier
        )
        public_key_status_before_registration = self.get_response(response_id)["result"]
        require_that("'public key' result", public_key_status_before_registration, is_false())

        lcc.set_step("Register new account with generated public key")
        response_id = self.send_request(
            self.get_request("request_registration_task"), self.__registration_api_identifier
        )
        pow_algorithm_data = self.get_response(response_id)["result"]
        solution = self.solve_registration_task(
            pow_algorithm_data["block_id"], pow_algorithm_data["rand_num"], pow_algorithm_data["difficulty"]
        )
        account_params = [
            callback, new_account, public_key, public_key, evm_address, solution, pow_algorithm_data["rand_num"]
        ]
        response_id = self.send_request(
            self.get_request("submit_registration_solution", account_params), self.__registration_api_identifier
        )
        response = self.get_response(response_id)
        self.get_notice(callback)
        require_that("'register_account' result", response["result"], is_true(), quiet=False)

        lcc.set_step("Verify generated public key after account registration")
        response_id = self.send_request(
            self.get_request("is_public_key_registered", [public_key]), self.__database_api_identifier
        )
        public_key_status_before_registration = self.get_response(response_id)["result"]
        check_that("'public key' result", public_key_status_before_registration, is_true())

    @lcc.prop("type", "method")
    @lcc.test("Pass an invalid public key to the method")
    @lcc.depends_on("API.DatabaseApi.Keys.IsPublicKeyRegistered.IsPublicKeyRegistered.method_main_check")
    def invalid_key_in_method_call(self, get_random_string_only_letters):
        lcc.set_step("Generate public key and make it not valid")
        public_key = self.generate_keys()[1]
        invalid_public_key = get_random_string_only_letters + public_key[len(get_random_string_only_letters):]
        lcc.log_info("Invalid public key generated successfully: '{}'".format(invalid_public_key))

        lcc.set_step("Verify generated invalid public key")
        response_id = self.send_request(
            self.get_request("is_public_key_registered", [invalid_public_key]), self.__database_api_identifier
        )
        response = self.get_response(response_id, negative=True)
        check_that(
            "'is_public_key_registered' return error message",
            response,
            has_entry("error"),
            quiet=True,
        )


@lcc.prop("negative", "type")
@lcc.tags("database_api", "is_public_key_registered")
@lcc.suite("Negative testing of method 'is_public_key_registered'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def is_public_key_registered(self, key):
        response_id = self.send_request(
            self.get_request("is_public_key_registered", [key]), self.__database_api_identifier
        )
        return self.get_response(response_id, negative=True)

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Call method with private key")
    @lcc.depends_on("API.DatabaseApi.Keys.IsPublicKeyRegistered.IsPublicKeyRegistered.method_main_check")
    def call_method_with_private_key(self):
        lcc.set_step("Generate private key")
        private_key = self.generate_keys()[0]
        lcc.log_info("Private key generated successfully: '{}'".format(private_key))

        lcc.set_step("Verify generated private key")
        response = self.is_public_key_registered(private_key)
        check_that(
            "'is_public_key_registered' return error message",
            response,
            has_entry("error"),
            quiet=True,
        )

    @lcc.prop("type", "method")
    @lcc.test("Call method with wrong params of all types")
    @lcc.depends_on("API.DatabaseApi.Keys.IsPublicKeyRegistered.IsPublicKeyRegistered.method_main_check")
    def call_method_with_wrong_params(self, get_all_random_types):
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())

        for i in range(len(get_all_random_types)):
            lcc.set_step("Wrong asset param, used '{}'".format(random_type_names[i]))
            response = self.is_public_key_registered(random_values[i])
            check_that(
                "'get_asset_holders' return error message with '{}' params".format(random_type_names[i]),
                response,
                has_entry("error"),
                quiet=True,
            )

    @lcc.prop("type", "method")
    @lcc.test("Call method without params")
    @lcc.depends_on("API.DatabaseApi.Keys.IsPublicKeyRegistered.IsPublicKeyRegistered.method_main_check")
    def call_method_without_params(self):
        lcc.set_step("Call method without params")
        response_id = self.send_request(self.get_request("is_public_key_registered"), self.__database_api_identifier)
        response = self.get_response(response_id, negative=True)
        check_that("'is_public_key_registered' return error message", response, has_entry("error"), quiet=True)
