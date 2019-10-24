# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, has_length, require_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_accounts'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_accounts", "get_accounts")
@lcc.suite("Check work of method 'get_accounts'", rank=1)
class GetAccounts(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.test("Simple work of method 'get_accounts'")
    def method_main_check(self):
        lcc.set_step("Get info about default accounts")
        params = ["1.2.0", "1.2.1"]
        response_id = self.send_request(self.get_request("get_accounts", [params]), self.__database_api_identifier)
        results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_accounts' with params: {}".format(params))

        lcc.set_step("Check length of received accounts")
        require_that(
            "'list of received accounts'",
            results, has_length(len(params))
        )

        for i, account_info in enumerate(results):
            lcc.set_step("Checking account #{} - '{}'".format(i, params[i]))
            self.object_validator.validate_account_object(self, account_info)


@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_accounts", "get_accounts")
@lcc.suite("Positive testing of method 'get_accounts'", rank=2)
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

    @lcc.test("Create accounts using account_create operation and get info about them")
    @lcc.depends_on("DatabaseApi.Accounts.GetAccounts.GetAccounts.method_main_check")
    def get_info_about_created_accounts(self, get_random_valid_account_name):
        accounts = [get_random_valid_account_name + "0", get_random_valid_account_name + "1"]
        accounts_public_keys = [self.generate_keys(), self.generate_keys()]

        lcc.set_step("Perform two account creation operations and store accounts ids")
        accounts = self.utils.get_account_id(self, accounts, accounts_public_keys, self.__database_api_identifier,
                                             need_operations=True)
        lcc.log_info("Two accounts created, ids: 1='{}', 2='{}'".format(accounts.get("accounts_ids")[0],
                                                                        accounts.get("accounts_ids")[1]))

        lcc.set_step("Get a list of created accounts by ID")
        response_id = self.send_request(self.get_request("get_accounts", [accounts.get("accounts_ids")]),
                                        self.__database_api_identifier)
        results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_accounts' with params: {}".format(accounts.get("accounts_ids")))

        for i, account_info in enumerate(results):
            lcc.set_step("Checking account #{}".format(i))
            performed_operations = accounts.get("list_operations")[i][0][1]
            check_that_in(
                account_info,
                "registrar", equal_to(performed_operations["registrar"]),
                "name", equal_to(performed_operations["name"]),
                "active", equal_to(performed_operations["active"]),
                "echorand_key", equal_to(performed_operations["echorand_key"]),
                "options", equal_to(performed_operations["options"])
            )

    @lcc.test(
        "Create account using account_create operation and compare response from 'get_accounts' and 'get_objects'")
    @lcc.depends_on("DatabaseApi.Accounts.GetAccounts.GetAccounts.method_main_check")
    def compare_with_method_get_objects(self, get_random_valid_account_name):
        account_name = get_random_valid_account_name
        public_key = self.generate_keys()[1]

        lcc.set_step("Perform account creation operation")
        operation = self.echo_ops.get_account_create_operation(self.echo, account_name, public_key, public_key,
                                                               registrar=self.echo_acc0, signer=self.echo_acc0)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception("Account is not created")
        operation_result = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("Account is created, id='{}'".format(operation_result))

        lcc.set_step("Get account by name")
        account_id = self.get_account_by_name(account_name, self.__database_api_identifier).get("result").get("id")
        response_id = self.send_request(self.get_request("get_accounts", [[account_id]]),
                                        self.__database_api_identifier)
        response_1 = self.get_response(response_id)
        lcc.log_info("Call method 'get_account_by_name' with param: {}".format(account_id))

        lcc.set_step("Get account by id")
        response_id = self.send_request(self.get_request("get_objects", [[account_id]]),
                                        self.__database_api_identifier)
        response_2 = self.get_response(response_id)
        lcc.log_info("Call method 'get_objects' with param: {}".format(account_id))

        lcc.set_step("Checking created account")
        account_info_1 = response_1["result"]
        account_info_2 = response_2["result"]
        for i, result in enumerate(account_info_1):
            check_that_in(
                result,
                "registrar", equal_to(account_info_2[i]["registrar"]),
                "name", equal_to(account_info_2[i]["name"]),
                "active", equal_to(account_info_2[i]["active"]),
                "echorand_key", equal_to(account_info_2[i]["echorand_key"]),
                "options", equal_to(account_info_2[i]["options"]),
                "extensions", equal_to(account_info_2[i]["extensions"])
            )
