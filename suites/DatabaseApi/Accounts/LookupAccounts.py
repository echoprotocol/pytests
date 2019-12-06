# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, equal_to, check_that, has_length, starts_with, is_true

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'lookup_accounts'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.prop("negative", "type")
@lcc.tags("api", "database_api", "database_api_accounts", "lookup_accounts")
@lcc.suite("Check work of method 'lookup_accounts'", rank=1)
class LookupAccounts(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.account_name = "nathan"

    def check_lookup_account_object(self, lookup_account):
        if not self.type_validator.is_account_name(lookup_account[0]):
            lcc.log_error("Wrong format of 'account name', got: {}".format(lookup_account[0]))
        else:
            lcc.log_info("'account name' has correct format: account_name")
        if not self.type_validator.is_account_id(lookup_account[1]):
            lcc.log_error("Wrong format of 'account id', got: {}".format(lookup_account[1]))
        else:
            lcc.log_info("'account id' has correct format: account_id")

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.test("Simple work of method 'lookup_accounts'")
    def method_main_check(self):
        lcc.set_step("Lookup nathan account and check result structure")
        limit = 1
        response_id = self.send_request(self.get_request("lookup_accounts", [self.account_name, limit]),
                                        self.__database_api_identifier)
        lookup_accounts = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'lookup_accounts' with lower_bound_name='{}',limit='{}' parameters".format(
            self.account_name, limit))

        lcc.set_step("Check simple work of method 'lookup_accounts'")
        for lookup_account in lookup_accounts:
            require_that(
                "'lookup account",
                lookup_account, has_length(2)
            )

            self.check_lookup_account_object(lookup_account)


@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_accounts", "lookup_accounts")
@lcc.suite("Positive testing of method 'lookup_accounts'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

    @staticmethod
    def proliferate_account_names(account_name_base, total_account_count):
        return ['{}{}'.format(account_name_base, 'a' * num) for num in range(total_account_count)]

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Create accounts using account_create operation and lookup info about them")
    @lcc.depends_on("DatabaseApi.Accounts.LookupAccounts.LookupAccounts.method_main_check")
    def lookup_info_about_created_accounts(self, get_random_valid_account_name):
        lcc.set_step("Generate account names")
        valid_account_name = get_random_valid_account_name
        account_count = 2
        account_names = self.proliferate_account_names(valid_account_name, account_count)
        accounts_public_keys = [self.generate_keys(), self.generate_keys()]
        lcc.log_info("Generated account names: {}, {}".format(account_names[0], account_names[1]))

        lcc.set_step("Perform two account creation operations and store accounts ids")
        accounts_ids = self.utils.get_account_id(self, account_names, accounts_public_keys,
                                                 self.__database_api_identifier)

        require_that("created account count", accounts_ids, has_length(account_count))
        lcc.log_info("Two accounts created, ids: '{}', '{}'".format(accounts_ids[0], accounts_ids[1]))

        lcc.set_step("Lookup created accounts")
        response_id = self.send_request(self.get_request("lookup_accounts", [valid_account_name, account_count]),
                                        self.__database_api_identifier)
        accounts_info = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'lookup_accounts' with params: lower_bound_name='{}', limit='{}'".format(
            valid_account_name, account_count))

        lcc.set_step("Check created accounts lookup info")
        for account in accounts_info:
            require_that("account name", account[0], starts_with(valid_account_name))

        lcc.set_step("Check created accounts by 'get_objects' method, compare with 'lookup_accounts' info")
        for account in accounts_info:
            response_id = self.send_request(self.get_request("get_objects", [[account[1]]]),
                                            self.__database_api_identifier)
            account_by_get_objects = self.get_response(response_id)["result"][0]
            check_that("account name", account[0], equal_to(account_by_get_objects["name"]))
            check_that("account id", account[1], equal_to(account_by_get_objects["id"]))

    @lcc.test("Lookup nonexistent accounts")
    @lcc.depends_on("DatabaseApi.Accounts.LookupAccounts.LookupAccounts.method_main_check")
    def lookup_more_accounts_than_exists(self):
        lcc.set_step("Get parameters, for lookup accounts more than exists")
        lower_bound_name, limit = self.utils.get_nonexistent_account_name(self, self.__database_api_identifier)
        lcc.log_info("Got parameters: lower_bound_name='{}', limit='{}'".format(lower_bound_name, limit))

        lcc.set_step("Lookup accounts")
        response_id = self.send_request(self.get_request("lookup_accounts", [lower_bound_name, limit]),
                                        self.__database_api_identifier)
        accounts = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'lookup_accounts' with lower_bound_name='{}', limit='{}' parameters".format(
            lower_bound_name, limit))

        lcc.set_step("Check accounts lookup info")
        require_that(
            "'length of listed accounts'",
            accounts, has_length(limit - 1)
        )

    @lcc.test("Check alphabet order in full accounts lookup info")
    @lcc.depends_on("DatabaseApi.Accounts.LookupAccounts.LookupAccounts.method_main_check")
    def check_alphabet_order_in_full_accounts_lookup_info(self):
        lower_bound_name, limit = "", 1000

        lcc.set_step("Lookup accounts")
        response_id = self.send_request(self.get_request("lookup_accounts", [lower_bound_name, limit]),
                                        self.__database_api_identifier)
        accounts = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'lookup_accounts' with lower_bound_name='{}', limit='{}' parameters".format(
            lower_bound_name, limit))

        lcc.set_step("Check alphabet order in full accounts lookup info")
        account_names = [account[0] for account in accounts]
        require_that(
            "'alphabet symbol order in full accounts lookup info'",
            account_names, equal_to(sorted(account_names.copy()))
        )

    @lcc.test("Check alphabet order in cut accounts lookup info")
    @lcc.depends_on("DatabaseApi.Accounts.LookupAccounts.LookupAccounts.method_main_check")
    def check_alphabet_order_in_cut_accounts_lookup_info(self, get_random_valid_account_name):
        valid_account_name = get_random_valid_account_name
        limit = 1000
        account_public_key = self.generate_keys()

        lcc.set_step("Perform account creation operation and store accounts ids")
        accounts_id = self.utils.get_account_id(self, valid_account_name, account_public_key,
                                                self.__database_api_identifier)
        lcc.log_info("Account created, ids: '{}'".format(accounts_id))

        lcc.set_step("Lookup accounts")
        response_id = self.send_request(self.get_request("lookup_accounts", [valid_account_name, limit]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'lookup_accounts' with lower_bound_name='{}', limit='{}' parameters".format(
            valid_account_name, limit))

        lcc.set_step("Check alphabet order in cut accounts lookup info")
        accounts = response["result"]
        account_names = [account[0] for account in accounts]
        require_that(
            "'full accounts lookup info in alphabet symbol order'",
            account_names == sorted(account_names.copy()), is_true()
        )


@lcc.prop("negative", "type")
@lcc.tags("api", "database_api", "database_api_accounts", "lookup_accounts")
@lcc.suite("Negative testing of method 'lookup_accounts'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.account_name = "nathan"

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info(
            "API identifier are: database='{}'".format(self.__database_api_identifier))


    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Check negative int value in lookup_accounts")
    @lcc.depends_on("DatabaseApi.Accounts.LookupAccounts.LookupAccounts.method_main_check")
    def check_negative_int_value_in_lookup_accounts(self):
        error_message = "Assert Exception: result >= 0: Invalid cast from negative number to unsigned"
        limit = -1

        lcc.set_step("Get 'lookup_accounts' with negative limit")
        response_id = self.send_request(self.get_request("lookup_accounts", [self.account_name, limit]),
                                        self.__database_api_identifier)
        message = self.get_response(response_id, negative=True)["error"]["message"]
        check_that(
            "error_message",
            message, equal_to(error_message),
            quiet=True
        )
