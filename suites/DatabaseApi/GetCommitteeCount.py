# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_integer, is_true, has_entry

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_committee_count'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_committee_count")
@lcc.suite("Check work of method 'get_committee_count'", rank=1)
class GetCommitteeCount(BaseTest):
    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_committee_count'")
    def method_main_check(self):
        lcc.set_step("Get the current number of committee members in the ECHO network")
        response_id = self.send_request(self.get_request("get_committee_count"), self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_committee_count', committee_members_count='{}'".format(response["result"]))

        lcc.set_step("Check simple work of method 'get_committee_count'")
        check_that(
            "'committee members count'",
            response["result"],
            is_integer(), quiet=True
        )


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("database_api", "get_committee_count")
@lcc.suite("Positive testing of method 'get_committee_count'", rank=2)
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

    @lcc.prop("type", "method")
    @lcc.test("Register a new account and make it a new committee member in the network")
    @lcc.depends_on("DatabaseApi.GetCommitteeCount.GetCommitteeCount.method_main_check")
    def add_new_committee_member_in_the_network(self, get_random_valid_account_name, get_random_hex_string):
        new_account = get_random_valid_account_name
        eth_account_address = get_random_hex_string

        lcc.set_step("Get the current number of committee members in the ECHO network")
        response_id = self.send_request(self.get_request("get_committee_count"), self.__database_api_identifier)
        committee_count_before = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_committee_count', committee_members_count='{}'".format(committee_count_before))

        lcc.set_step("Register new account in the network")
        new_account_id = self.get_account_id(new_account, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account_id))

        lcc.set_step("Create created account new committee member in the ECHO network")
        self.utils.perform_committee_member_create_operation(self, new_account_id, eth_account_address,
                                                             self.__database_api_identifier)
        lcc.log_info("Successfully created a new committee member")

        lcc.set_step("Get the updated number of committee members in the ECHO network")
        response_id = self.send_request(self.get_request("get_committee_count"), self.__database_api_identifier)
        committee_count_after = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_committee_count', committee_members_count='{}'".format(committee_count_after))

        lcc.set_step("Check that created committee member added")
        check_that(
            "'new committee member added'",
            (committee_count_after - committee_count_before) == 1,
            is_true(),
        )


@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_committee_count")
@lcc.suite("Negative testing of method 'get_committee_count'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Call method with params of all types")
    @lcc.tags("Bug: 'ECHO-680'")
    @lcc.depends_on("DatabaseApi.GetCommitteeCount.GetCommitteeCount.method_main_check")
    def call_method_with_params(self, get_all_random_types):
        lcc.set_step("Call method with all types of params")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            # todo: remove if. Bug: "ECHO-680"
            if i == 4:
                continue
            response_id = self.send_request(self.get_request("get_committee_count", random_values[i]),
                                            self.__api_identifier)
            response = self.get_response(response_id, negative=True)
            check_that(
                "'get_committee_count' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True
            )
