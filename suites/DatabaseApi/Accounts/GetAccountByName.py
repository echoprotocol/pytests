# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, check_that, has_length, is_integer, is_dict, is_list, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_account_by_name'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_accounts", "get_account_by_name")
@lcc.suite("Check work of method 'get_account_by_name'", rank=1)
class GetAccountByName(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.committee_account = "committee-account"

    def check_fields_account_ids_format(self, response, field):
        if not self.type_validator.is_account_id(response[field]):
            lcc.log_error("Wrong format of '{}', got: {}".format(field, response[field]))
        else:
            lcc.log_info("'{}' has correct format: account_object_type".format(field))

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.test("Simple work of method 'get_account_by_name'")
    def method_main_check(self):
        lcc.set_step("Get info about default committee_account")
        response_id = self.send_request(self.get_request("get_account_by_name", [self.committee_account]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_account_by_name' with param: {}".format(self.committee_account))

        lcc.set_step("Checking committee-account")
        account_info = response["result"]
        if check_that("account_info", account_info, has_length(16)):
            account_ids_format = ["id", "registrar"]
            for account_id_format in account_ids_format:
                self.check_fields_account_ids_format(account_info, account_id_format)
            if not self.type_validator.is_account_name(account_info["name"]):
                lcc.log_error("Wrong format of 'name', got: {}".format(account_info["name"]))
            else:
                lcc.log_info("'name' has correct format: account_name")
            if not self.type_validator.is_echorand_key(account_info["echorand_key"]):
                lcc.log_error("Wrong format of 'echorand_key', got: {}".format(account_info["echorand_key"]))
            else:
                lcc.log_info("'echorand_key' has correct format: echo_rand_key")
            if not self.type_validator.is_account_statistics_id(account_info["statistics"]):
                lcc.log_error("Wrong format of 'statistics', got: {}".format(account_info["statistics"]))
            else:
                lcc.log_info("'statistics' has correct format: account_statistics_object_type")
            check_that_in(
                account_info,
                "network_fee_percentage", is_integer(),
                "active", is_dict(),
                "options", is_dict(),
                "whitelisting_accounts", is_list(),
                "blacklisting_accounts", is_list(),
                "whitelisted_accounts", is_list(),
                "blacklisted_accounts", is_list(),
                "active_special_authority", is_list(),
                "top_n_control_flags", is_integer(),
                "accumulated_reward", is_integer(),
                "extensions", is_list(),
                quiet=True
            )

            lcc.set_step("Check 'active' field")
            if check_that("active", account_info["active"], has_length(3)):
                check_that_in(
                    account_info["active"],
                    "weight_threshold", is_integer(),
                    "account_auths", is_list(),
                    "key_auths", is_list(),
                    quiet=True
                )

            lcc.set_step("Check 'options' field")
            if check_that("active", account_info["options"], has_length(6)):
                account_ids_format = ["voting_account", "delegating_account"]
                for account_id_format in account_ids_format:
                    self.check_fields_account_ids_format(account_info["options"], account_id_format)
                check_that_in(
                    account_info["options"],
                    "delegate_share", is_integer(),
                    "num_committee", is_integer(),
                    "votes", is_list(),
                    "extensions", is_list(),
                    quiet=True
                )


@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_accounts", "get_account_by_name")
@lcc.suite("Positive testing of method 'get_account_by_name'", rank=2)
class PositiveTesting(BaseTest):

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
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Create account using account_create operation and get info about them")
    @lcc.depends_on("DatabaseApi.Accounts.GetAccountByName.GetAccountByName.method_main_check")
    def get_info_about_created_account(self, get_random_valid_account_name):
        account_name = get_random_valid_account_name
        public_key = self.generate_keys()

        lcc.set_step("Perform account creation operation")
        operation = self.echo_ops.get_account_create_operation(self.echo, account_name, public_key[1], public_key[1],
                                                               registrar=self.echo_acc0, signer=self.echo_acc0)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception("Account is not created")
        operation_result = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("Account is created, id='{}'".format(operation_result))

        lcc.set_step("Get account by name")
        response_id = self.send_request(self.get_request("get_account_by_name", [account_name]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_account_by_name' with param: {}".format(account_name))

        lcc.set_step("Checking created account")
        performed_operations = collected_operation[0][1]
        account_info = response["result"]
        check_that_in(
            account_info,
            "registrar", equal_to(performed_operations["registrar"]),
            "name", equal_to(performed_operations["name"]),
            "active", equal_to(performed_operations["active"]),
            "echorand_key", equal_to(performed_operations["echorand_key"]),
            "options", equal_to(performed_operations["options"])
        )
