# -*- coding: utf-8 -*-
import random
import string

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_integer, has_entry, is_none, is_not_none, has_length, is_true, \
    is_false

from common.base_test import BaseTest
from common.receiver import Receiver

SUITE = {
    "description": "Registration Api"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.prop("negative", "type")
@lcc.tags("api", "registration_api")
@lcc.suite("Registration API", rank=1)
class RegistrationApi(object):

    @lcc.tags("connection_to_registration_api", "connection_to_apis")
    @lcc.test("Check connection to RegistrationApi")
    def connection_to_registration_api(self, get_random_valid_account_name, get_random_integer):
        base = BaseTest()
        base.ws = base.create_connection_to_echo()
        base.receiver = Receiver(web_socket=base.ws)
        lcc.set_step("Requesting Access to a Registration API")
        api_identifier = base.get_identifier("registration")
        check_that("'registration api identifier'", api_identifier, is_integer())

        lcc.set_step("Check node status, if empty run pre-deploy")
        base.check_node_status()

        lcc.set_step("Check Registration api identifier. Call registration api method 'register_account'")
        generate_keys = base.generate_keys()
        public_key = generate_keys[1]
        callback = get_random_integer
        account_params = [callback, get_random_valid_account_name, public_key, public_key]
        response_id = base.send_request(base.get_request("register_account", account_params), api_identifier)
        response = base.get_response(response_id)
        base.get_notice(callback)

        check_that(
            "'call method 'register_account''",
            response["result"], is_none(), quiet=False
        )

        lcc.set_step("Check that Registration api identifier is unique")
        generate_keys = base.generate_keys()
        public_key = generate_keys[1]
        account_params = [callback, get_random_valid_account_name, public_key, public_key]
        response_id = base.send_request(base.get_request("register_account", account_params), api_identifier + 1)
        response = base.get_response(response_id, negative=True)

        check_that(
            "'using another identifier gives an error'",
            response, has_entry("error"), quiet=True
        )

        base.ws.close()


@lcc.prop("positive", "type")
@lcc.tags("api", "registration_api")
@lcc.suite("Positive testing of method 'register_account'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    def _register_account(self, callback, new_account, public_key=None, echorand_key=None):
        generate_keys = self.generate_keys()
        if public_key is None:
            public_key = generate_keys[1]
        if echorand_key is None:
            echorand_key = generate_keys[1]
        account_params = [callback, new_account, public_key, echorand_key]
        response_id = self.send_request(self.get_request("register_account", account_params),
                                        self.__registration_api_identifier)
        return self.get_response(response_id, negative=True)

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))

    @lcc.test("Registration with valid credential")
    @lcc.depends_on("RegistrationApi.RegistrationApi.connection_to_registration_api")
    def registration_with_valid_credential(self, get_random_valid_account_name, get_random_integer):
        lcc.set_step("Registration an account")
        new_account = get_random_valid_account_name
        callback = get_random_integer
        response = self._register_account(callback, new_account)
        self.get_notice(callback)
        check_that(
            "register account '{}'".format(new_account),
            response["result"], is_none(), quiet=False
        )

        lcc.set_step("Check that the account is registered on the network. Call method 'get_account_by_name'")
        response_id = self.send_request(self.get_request("get_account_by_name", [new_account]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)

        check_that(
            "'call method 'get_account_by_name''",
            response["result"], is_not_none(), quiet=True
        )

    @lcc.test("Registration with unequal public keys")
    @lcc.depends_on("RegistrationApi.RegistrationApi.connection_to_registration_api")
    def registration_with_unequal_public_keys(self, get_random_valid_account_name, get_random_integer):
        new_account = get_random_valid_account_name
        callback = get_random_integer
        public_keys_active = self.generate_keys()[1]
        public_keys_echorand = self.generate_keys()[1]

        lcc.set_step("Registration an account")
        response = self._register_account(callback, new_account, public_keys_active, public_keys_echorand)
        lcc.log_info("Call method 'register_account' with active public key: {}, echorand public key: {}"
                     "".format(public_keys_active, public_keys_echorand))
        self.get_notice(callback)
        check_that("register account '{}'".format(new_account), response["result"], is_none(), quiet=True)

        lcc.set_step("Check that the account is registered in the network. Call method 'get_account_by_name'")
        response_id = self.send_request(self.get_request("get_account_by_name", [new_account]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        check_that("'active public key'", result["active"]["key_auths"][0][0] == public_keys_active, is_true())
        check_that("'echorand public key'", result["echorand_key"] == public_keys_echorand, is_true())
        check_that("'keys are unequal'", public_keys_active == public_keys_echorand, is_false())

    @lcc.test("Get callback: notification whenever transaction for registration account broadcast")
    @lcc.depends_on("RegistrationApi.RegistrationApi.connection_to_registration_api")
    def get_callback_about_registration_account(self, get_random_integer, get_random_valid_account_name):
        callback = get_random_integer
        new_account = get_random_valid_account_name

        lcc.set_step("Call registration api method 'register_account'")
        response = self._register_account(callback, new_account)
        check_that("'call method 'register_account''", response["result"], is_none(), quiet=True)

        lcc.set_step("Get notification about broadcast of registered account with name: ''".format(new_account))
        notice = self.get_notice(callback)
        check_that("notification", notice, has_length(2))

        lcc.set_step("Get transaction of registration account'")
        tx_id = notice["tx_id"]
        response_id = self.send_request(
            self.get_request("get_recent_transaction_by_id", [tx_id]), self.__database_api_identifier)
        transaction = self.get_response(response_id)["result"]["operations"][0]
        lcc.log_info("Call method 'get_recent_transaction_by_id' with transaction_id='{}' parameter".format(tx_id))

        lcc.set_step("Get block with transaction of registration account'")
        block_num = notice["block_num"]
        response_id = self.send_request(
            self.get_request("get_block", [block_num]), self.__database_api_identifier)
        transaction_in_block = self.get_response(response_id)["result"]["transactions"][0][
            "operations"][0]
        lcc.log_info("Call method 'get_block' with block_num='{}' parameter".format(block_num))

        lcc.set_step("Check transactions from 'get_recent_transaction_by_id' and 'get_block'")
        check_that("'transactions are equal'", transaction == transaction_in_block, is_true())


@lcc.prop("negative", "type")
@lcc.tags("api", "registration_api")
@lcc.suite("Negative testing of method 'register_account'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__registration_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "Registration API identifiers is '{}'".format(self.__registration_api_identifier))

    @staticmethod
    def get_random_character(random_def, not_hyphen_or_point=False):
        character = random_def
        if not_hyphen_or_point and (character == "-" or character == "."):
            return "*"
        return character

    @staticmethod
    def get_account_name(_from=1, _to=64):
        random_num = random.randrange(_from, _to)
        random_string = ''.join(
            random.SystemRandom().choice(string.ascii_lowercase) for _ in range(random_num))
        return random_string

    def get_registration_parameters(self, callback, new_account):
        public_key = self.generate_keys()[1]
        return [callback, new_account, public_key, public_key], ["callback", "account_name", "active_key",
                                                                 "echorand_key"]

    def _register_account(self, callback, new_account, public_key=None, echorand_key=None):
        generate_keys = self.generate_keys()
        if public_key is None:
            public_key = generate_keys[1]
        if echorand_key is None:
            echorand_key = generate_keys[1]
        account_params = [callback, new_account, public_key, echorand_key]
        response_id = self.send_request(self.get_request("register_account", account_params),
                                        self.__registration_api_identifier)
        return self.get_response(response_id, negative=True)

    @lcc.test("Empty account name")
    @lcc.depends_on("RegistrationApi.RegistrationApi.connection_to_registration_api")
    def empty_account_name(self, get_random_integer):
        lcc.set_step("Registration empty account")
        callback = get_random_integer
        new_account = ""
        response = self._register_account(callback, new_account)

        check_that(
            "'register_account' return error message",
            response, has_entry("error"), quiet=True
        )

    @lcc.test("Account name length longer than 63")
    @lcc.depends_on("RegistrationApi.RegistrationApi.connection_to_registration_api")
    def account_name_length_longer_than_63(self, get_random_integer):
        lcc.set_step("Register an account with a name longer than 63")
        callback = get_random_integer
        new_account = self.get_account_name(64, 100)
        response = self._register_account(callback, new_account)

        check_that(
            "'register_account' return error message",
            response, has_entry("error"), quiet=True
        )

    @lcc.test("Account name start with digit")
    @lcc.depends_on("RegistrationApi.RegistrationApi.connection_to_registration_api")
    def account_name_start_with_digit(self, get_random_integer):
        lcc.set_step("Register an account with a name that start with digit")
        callback = get_random_integer
        new_account = "1" + self.get_account_name(_to=63)
        response = self._register_account(callback, new_account)

        check_that(
            "'register_account' return error message",
            response, has_entry("error"), quiet=True
        )

    @lcc.test("Account name is digits")
    @lcc.depends_on("RegistrationApi.RegistrationApi.connection_to_registration_api")
    def account_name_is_digits(self, get_random_integer):
        lcc.set_step("Register an account with a name from digits")
        callback = get_random_integer
        new_account = 123456
        response = self._register_account(callback, new_account)

        check_that(
            "'register_account' return error message",
            response, has_entry("error"), quiet=True
        )

    @lcc.test("Account name with a special character, not hyphen")
    @lcc.depends_on("RegistrationApi.RegistrationApi.connection_to_registration_api")
    def account_name_with_special_character(self, get_random_integer, get_random_character):
        lcc.set_step("Register an account with a name that have a special character, not hyphen")
        callback = get_random_integer
        part1 = self.get_account_name(_to=4)
        part2 = self.get_account_name(_to=4)
        new_account = part1 + self.get_random_character(get_random_character, not_hyphen_or_point=True) + part2
        response = self._register_account(callback, new_account)

        check_that(
            "'register_account' return error message",
            response, has_entry("error"), quiet=True
        )

    @lcc.test("Account name end with a special character")
    @lcc.depends_on("RegistrationApi.RegistrationApi.connection_to_registration_api")
    def account_name_end_with_special_character(self, get_random_integer, get_random_character):
        lcc.set_step("Register an account with a name that end with a special character")
        callback = get_random_integer
        new_account = self.get_account_name() + self.get_random_character(get_random_character)
        response = self._register_account(callback, new_account)

        check_that(
            "'register_account' return error message",
            response, has_entry("error"), quiet=True
        )

    @lcc.test("Account name is uppercase")
    @lcc.depends_on("RegistrationApi.RegistrationApi.connection_to_registration_api")
    def account_name_is_uppercase(self, get_random_integer):
        lcc.set_step("Register an account with a name that all letters are uppercase")
        callback = get_random_integer
        new_account = self.get_account_name().upper()
        response = self._register_account(callback, new_account)

        check_that(
            "'register_account' return error message",
            response, has_entry("error"), quiet=True
        )

    @lcc.test("Registration with wrong public keys")
    @lcc.depends_on("RegistrationApi.RegistrationApi.connection_to_registration_api")
    def registration_with_wrong_public_keys(self, get_random_valid_account_name, get_random_integer,
                                            get_random_string_only_letters):
        lcc.set_step("Registration an account")
        new_account = get_random_valid_account_name
        callback = get_random_integer

        lcc.set_step("Generate public key and make it not valid")
        public_key = self.generate_keys()[1]
        invalid_public_key = get_random_string_only_letters + public_key[len(get_random_string_only_letters):]
        lcc.log_info("Invalid public key generated successfully: '{}'".format(invalid_public_key))

        lcc.set_step("Call 'register_account' with invalid active key")
        response = self._register_account(callback, new_account, public_key=invalid_public_key)
        check_that(
            "'register_account' return error message with invalid active key: '{}'".format(invalid_public_key),
            response, has_entry("error"), quiet=True)

        lcc.set_step("Call 'register_account' with invalid echorand key")
        response = self._register_account(callback, new_account, echorand_key=invalid_public_key)
        check_that(
            "'register_account' return error message with invalid echorand key: '{}'".format(invalid_public_key),
            response, has_entry("error"), quiet=True)

    @lcc.test("Registration with wrong params")
    @lcc.depends_on("RegistrationApi.RegistrationApi.connection_to_registration_api")
    def registration_with_with_wrong_params(self, get_random_integer, get_random_valid_account_name,
                                            get_all_random_types):
        lcc.set_step("Prepare registration account params")
        registration_params, param_names = self.get_registration_parameters(get_random_integer,
                                                                            get_random_valid_account_name)
        params = registration_params.copy()
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(params)):
            for j, random_value in enumerate(random_values):
                params[i] = random_value

                if i == 0 and (isinstance(params[i], int) or isinstance(params[i], float)):
                    continue
                if i == 1 and isinstance(params[i], (str, bool)):
                    continue

                lcc.set_step("Call 'register_account' with invalid credential: {}={}".format(param_names[i],
                                                                                             random_type_names[j]))
                response_id = self.send_request(self.get_request("register_account", params),
                                                self.__registration_api_identifier)
                response = self.get_response(response_id, negative=True)
                check_that(
                    "'register_account' return error message with '{}' params".format(params),
                    response, has_entry("error"), quiet=True)
            params = registration_params.copy()

    @lcc.test("Registration with wrong amount of params")
    @lcc.depends_on("RegistrationApi.RegistrationApi.connection_to_registration_api")
    def registration_with_wrong_count_of_params(self, get_random_integer, get_random_valid_account_name):
        registration_params, param_names = self.get_registration_parameters(get_random_integer,
                                                                            get_random_valid_account_name)
        for i in range(1, len(registration_params)):
            params = registration_params[:-i]

            lcc.set_step("Call 'register_account' with wrong count of params = {}".format(len(params)))
            response_id = self.send_request(self.get_request("register_account", params),
                                            self.__registration_api_identifier)
            response = self.get_response(response_id, negative=True)
            check_that("'register_account' return error message with wrong amount of params: {}".format(params),
                       response, has_entry("error"), quiet=True)

        params_with_none = registration_params.copy()
        for i in range(1, len(params_with_none)):
            params_with_none[i] = None
            lcc.set_step("Call 'register_account' with {} = None ".format(param_names[i]))
            response_id = self.send_request(self.get_request("register_account", params_with_none),
                                            self.__registration_api_identifier)
            response = self.get_response(response_id, negative=True)
            check_that(
                "'register_account' return error message with None in params: {}".format(params_with_none),
                response, has_entry("error"), quiet=True)
            params_with_none = registration_params.copy()
