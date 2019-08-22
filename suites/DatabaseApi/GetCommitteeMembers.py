# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, has_length, check_that_in, is_str, is_list, equal_to, is_true, \
    not_equal_to, check_that, is_none

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_committee_members'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_committee_members")
@lcc.suite("Check work of method 'get_committee_members'", rank=1)
class GetCommitteeMembers(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_committee_members'")
    def method_main_check(self):
        lcc.set_step("Get list of active committee members")
        response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
        active_committee_members = self.get_response(response_id)["result"]["active_committee_members"]
        lcc.log_info("Active committee members: '{}'".format(active_committee_members))

        lcc.set_step("Call method 'get_committee_members'")
        response_id = self.send_request(self.get_request("get_committee_members", [active_committee_members]),
                                        self.__database_api_identifier)
        committee_members = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_committee_members' with params='{}'".format(active_committee_members))

        lcc.set_step("Check method 'get_committee_members' result")
        for i, committee_member in enumerate(committee_members):
            lcc.set_step("Get active committee member #'{}'".format(i))
            # todo: leave only  has_length to (7), after field "pay_vb" will be removed from committee members object
            if "pay_vb" in committee_member:
                require_that("'committee member'", committee_member, has_length(8))
            else:
                require_that("'committee member'", committee_member, has_length(7))
            if not self.validator.is_committee_member_id(committee_member["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(committee_member["id"]))
            else:
                lcc.log_info("'id' has correct format: committee_member_object_type")
            if not self.validator.is_account_id(committee_member["committee_member_account"]):
                lcc.log_error("Wrong format of 'committee_member_account', got: {}".format(
                    committee_member["committee_member_account"]))
            else:
                lcc.log_info("'committee_member_account' has correct format: account_object_type")
            if not self.validator.is_vote_id(committee_member["vote_id"]):
                lcc.log_error("Wrong format of 'vote_id', got: {}".format(
                    committee_member["vote_id"]))
            else:
                lcc.log_info("'vote_id' has correct format: vote_id_type")
            if not self.validator.is_hex(committee_member["eth_address"]):
                lcc.log_error(
                    "Wrong format of 'eth_address', got: {}".format(committee_member["eth_address"]))
            else:
                lcc.log_info("'eth_address' has correct format: hex")
            self.check_uint256_numbers(committee_member, "total_votes", quiet=True)
            check_that_in(
                committee_member,
                "url", is_str(),
                "extensions", is_list(),
                quiet=True
            )


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("database_api", "get_committee_members")
@lcc.suite("Positive testing of method 'get_committee_members'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.new_account_id = None
        self.committee_member_id = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}',".format(self.__database_api_identifier,
                                                                            self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Create new committee member")
    @lcc.depends_on("DatabaseApi.GetCommitteeMembers.GetCommitteeMembers.method_main_check")
    def create_committee_member(self, get_random_valid_account_name, get_random_url, get_random_hex_string):
        new_account = get_random_valid_account_name
        url = get_random_url
        eth_account_address = get_random_hex_string

        lcc.set_step("Create and get new account")
        self.new_account_id = self.get_account_id(new_account, self.__database_api_identifier,
                                                  self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(self.new_account_id))

        lcc.set_step("Create committee member of new account in the ECHO network")
        broadcast_result = self.utils.perform_committee_member_create_operation(self, self.new_account_id,
                                                                                eth_account_address,
                                                                                self.__database_api_identifier, url=url)
        self.committee_member_id = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("Successfully created a new committee member, id: '{}'".format(self.committee_member_id))

        lcc.set_step("Get committee member")
        param = [self.committee_member_id]
        response_id = self.send_request(self.get_request("get_committee_members", [param]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_committee_members' with params='{}'".format(param))

        lcc.set_step("Check created committee member in the ECHO network")
        for committee_member in result:
            require_that("'committee member object'", committee_member, has_length(7))
            check_that_in(
                committee_member,
                "id", equal_to(self.committee_member_id),
                "committee_member_account", equal_to(self.new_account_id),
                "url", equal_to(url)
            )
            check_that("'eth_address'", committee_member["eth_address"].lower(),
                       equal_to(eth_account_address))

    @lcc.prop("type", "method")
    @lcc.test("Update committee member")
    @lcc.depends_on("DatabaseApi.GetCommitteeMembers.PositiveTesting.create_committee_member")
    def update_committee_member(self, get_random_url, get_random_hex_string):
        new_url = get_random_url
        new_eth_address = get_random_hex_string

        lcc.set_step("Get committee member before update")
        param = [self.committee_member_id]
        response_id = self.send_request(self.get_request("get_committee_members", [param]),
                                        self.__database_api_identifier)
        committee_member_before_update = self.get_response(response_id)["result"][0]
        lcc.log_info("Call method 'get_committee_members' with params='{}'".format(param))

        lcc.set_step("Perform committee member update operation")
        self.utils.perform_committee_member_update_operation(self, self.committee_member_id, self.new_account_id,
                                                             self.__database_api_identifier,
                                                             new_eth_address=new_eth_address, new_url=new_url)
        lcc.log_info("Update committee member completed successfully")

        lcc.set_step("Get committee member after update")
        param = [self.committee_member_id]
        response_id = self.send_request(self.get_request("get_committee_members", [param]),
                                        self.__database_api_identifier)
        committee_member_after_update = self.get_response(response_id)["result"][0]
        lcc.log_info("Call method 'get_committee_members' with params='{}'".format(param))

        lcc.set_step("Check updated committee member")
        require_that("'old committee member not equal to updated'",
                     committee_member_before_update != committee_member_after_update, is_true())
        check_that_in(
            committee_member_after_update,
            "id", equal_to(committee_member_before_update["id"]),
            "committee_member_account", equal_to(committee_member_before_update["committee_member_account"]),
            "url", not_equal_to(committee_member_before_update["url"]),
            "url", equal_to(new_url),
            "eth_address", not_equal_to(committee_member_before_update["eth_address"]),
        )
        check_that("'new_eth_address'", committee_member_after_update["eth_address"].lower(), equal_to(new_eth_address))

    @lcc.prop("type", "method")
    @lcc.test("Create committee member and compare response from 'get_committee_members' and 'get_objects'")
    @lcc.depends_on("DatabaseApi.GetCommitteeMembers.GetCommitteeMembers.method_main_check")
    def compare_with_method_get_objects(self, get_random_valid_account_name, get_random_url, get_random_hex_string):
        new_account = get_random_valid_account_name
        url = get_random_url
        eth_account_address = get_random_hex_string

        lcc.set_step("Create and get new account")
        self.new_account_id = self.get_account_id(new_account, self.__database_api_identifier,
                                                  self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(self.new_account_id))

        lcc.set_step("Create committee member of new account in the ECHO network")
        broadcast_result = self.utils.perform_committee_member_create_operation(self, self.new_account_id,
                                                                                eth_account_address,
                                                                                self.__database_api_identifier, url=url)
        self.committee_member_id = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("Successfully created a new committee member, id: '{}'".format(self.committee_member_id))

        lcc.set_step("Get committee member")
        param = [self.committee_member_id]
        response_id = self.send_request(self.get_request("get_committee_members", [param]),
                                        self.__database_api_identifier)
        committee_member_result = self.get_response(response_id)["result"][0]
        lcc.log_info("Call method 'get_committee_members' with params='{}'".format(param))

        lcc.set_step("Get committee member by id")
        response_id = self.send_request(self.get_request("get_objects", [param]), self.__database_api_identifier)
        committee_member_info = self.get_response(response_id)["result"][0]
        lcc.log_info("Call method 'get_objects' with param: {}".format(param))

        lcc.set_step("Compare results of method 'get_objects' and 'get_committee_members'")
        require_that("'results of method 'get_committee_members' and 'get_objects' is equal",
                     committee_member_result == committee_member_info, is_true())

    @lcc.prop("type", "method")
    @lcc.test("Use in method call nonexistent committee member id")
    @lcc.depends_on("DatabaseApi.GetCommitteeMembers.GetCommitteeMembers.method_main_check")
    def nonexistent_committee_member_id_in_method_call(self):
        lcc.set_step("Generate nonexistent committee_member_id")
        nonexistent_committee_member_id = self.utils.get_nonexistent_committee_member_id(self,
                                                                                         self.__database_api_identifier)
        lcc.log_info('Nonexistent committee member id: {}'.format(nonexistent_committee_member_id))

        lcc.set_step("Get nonexistent committee member")
        param = [nonexistent_committee_member_id]
        response_id = self.send_request(self.get_request("get_committee_members", [param]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][0]
        lcc.log_info("Call method 'get_committee_members' with params='{}'".format(param))

        lcc.set_step("Check nonexistent committee member id")
        check_that("'get_committee_members result'", result, is_none())
