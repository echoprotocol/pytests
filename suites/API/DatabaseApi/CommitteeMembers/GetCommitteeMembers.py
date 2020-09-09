# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import (
    check_that, check_that_in, equal_to, has_length, is_none, is_true, not_equal_to, require_that
)

SUITE = {
    "description": "Methods: 'get_committee_members', 'get_objects' (committee member object)"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags(
    "api", "database_api", "database_api_committee_members", "get_committee_members", "database_api_objects",
    "get_objects"
)
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

    @lcc.test("Simple work of method 'get_committee_members'")
    def method_main_check(self):
        active_committee_members_ids = []

        lcc.set_step("Get list of active committee members")
        response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
        active_committee_members = self.get_response(response_id)["result"]["active_committee_members"]
        for member in active_committee_members:
            active_committee_members_ids.append(member[0])
        lcc.log_info("Active committee members ids: '{}'".format(active_committee_members_ids))

        lcc.set_step("Call method 'get_committee_members'")
        params = active_committee_members_ids
        response_id = self.send_request(
            self.get_request("get_committee_members", [params]), self.__database_api_identifier
        )
        get_committee_members_results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_committee_members' with params='{}'".format(params))

        lcc.set_step("Check method 'get_committee_members' result")
        for i, committee_member in enumerate(get_committee_members_results):
            lcc.set_step("Get active committee member #'{}'".format(i))
            self.object_validator.validate_committee_member_object(self, committee_member)


@lcc.prop("positive", "type")
@lcc.tags(
    "api", "database_api", "database_api_committee_members", "get_committee_members", "database_api_objects",
    "get_objects"
)
@lcc.suite("Positive testing of methods: 'get_committee_members', 'get_objects' (committee member object)", rank=2)
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
            "API identifiers are: database='{}', registration='{}',".format(
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

    @lcc.test("Create new committee member")
    @lcc.depends_on("API.DatabaseApi.CommitteeMembers.GetCommitteeMembers.GetCommitteeMembers.method_main_check")
    def create_committee_member(
        self, get_random_valid_account_name, get_random_url, get_random_eth_address, get_random_btc_public_key
    ):
        new_account = get_random_valid_account_name
        url = get_random_url
        eth_account_address = get_random_eth_address
        btc_public_key = get_random_btc_public_key

        lcc.set_step("Create and get new account")
        self.new_account_id = self.get_account_id(
            new_account, self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("New Echo account created, account_id='{}'".format(self.new_account_id))

        lcc.set_step("Create committee member of new account in the ECHO network")
        broadcast_result = self.utils.perform_committee_member_create_operation(
            self,
            self.new_account_id,
            eth_account_address,
            btc_public_key,
            self.__database_api_identifier,
            deposit_amount=100000000000,
            url=url
        )
        self.committee_member_id = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("Successfully created a new committee member, id: '{}'".format(self.committee_member_id))

        lcc.set_step("Get committee member")
        param = [self.committee_member_id]
        response_id = self.send_request(
            self.get_request("get_committee_members", [param]), self.__database_api_identifier
        )
        result = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_committee_members' with params='{}'".format(param))

        lcc.set_step("Check created committee member in the ECHO network")
        for committee_member in result:
            require_that("'committee member object'", committee_member, has_length(6))
            check_that_in(
                committee_member, "id", equal_to(self.committee_member_id), "committee_member_account",
                equal_to(self.new_account_id), "url", equal_to(url)
            )
            check_that("'eth_address'", committee_member["eth_address"].lower(), equal_to(eth_account_address))
            check_that("'btc_public_key'", committee_member["btc_public_key"].lower(), equal_to(btc_public_key))

    @lcc.test("Update committee member")
    @lcc.depends_on("API.DatabaseApi.CommitteeMembers.GetCommitteeMembers.PositiveTesting.create_committee_member")
    def update_committee_member(self, get_random_url, get_random_eth_address, get_random_btc_public_key):
        new_url = get_random_url
        new_eth_address = get_random_eth_address
        new_btc_public_key = get_random_btc_public_key

        lcc.set_step("Get committee member before update")
        param = [self.committee_member_id]
        response_id = self.send_request(
            self.get_request("get_committee_members", [param]), self.__database_api_identifier
        )
        committee_member_before_update = self.get_response(response_id)["result"][0]
        lcc.log_info("Call method 'get_committee_members' with params='{}'".format(param))

        lcc.set_step("Perform committee member update operation")
        self.utils.perform_committee_member_update_operation(
            self,
            self.committee_member_id,
            self.new_account_id,
            self.__database_api_identifier,
            new_eth_address=new_eth_address,
            new_btc_public_key=new_btc_public_key,
            new_url=new_url
        )
        lcc.log_info("Update committee member completed successfully")

        lcc.set_step("Get committee member after update")
        param = [self.committee_member_id]
        response_id = self.send_request(
            self.get_request("get_committee_members", [param]), self.__database_api_identifier
        )
        committee_member_after_update = self.get_response(response_id)["result"][0]
        lcc.log_info("Call method 'get_committee_members' with params='{}'".format(param))

        lcc.set_step("Check updated committee member")
        require_that(
            "'old committee member not equal to updated'",
            committee_member_before_update != committee_member_after_update, is_true()
        )
        check_that_in(
            committee_member_after_update,
            "id",
            equal_to(committee_member_before_update["id"]),
            "committee_member_account",
            equal_to(committee_member_before_update["committee_member_account"]),
            "url",
            not_equal_to(committee_member_before_update["url"]),
            "url",
            equal_to(new_url),
            "eth_address",
            not_equal_to(committee_member_before_update["eth_address"]),
            "btc_public_key",
            not_equal_to(committee_member_before_update["btc_public_key"]),
        )
        check_that("'new_eth_address'", committee_member_after_update["eth_address"].lower(), equal_to(new_eth_address))
        check_that(
            "'new_btc_public_key'", committee_member_after_update["btc_public_key"].lower(),
            equal_to(new_btc_public_key)
        )

    @lcc.test("Create committee member and compare response from 'get_committee_members' and 'get_objects'")
    @lcc.depends_on("API.DatabaseApi.CommitteeMembers.GetCommitteeMembers.GetCommitteeMembers.method_main_check")
    def compare_with_method_get_objects(
        self, get_random_valid_account_name, get_random_url, get_random_eth_address, get_random_btc_public_key
    ):
        new_account = get_random_valid_account_name
        url = get_random_url
        eth_account_address = get_random_eth_address
        btc_public_key = get_random_btc_public_key

        lcc.set_step("Create and get new account")
        self.new_account_id = self.get_account_id(
            new_account, self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("New Echo account created, account_id='{}'".format(self.new_account_id))

        lcc.set_step("Create committee member of new account in the ECHO network")
        broadcast_result = self.utils.perform_committee_member_create_operation(
            self,
            self.new_account_id,
            eth_account_address,
            btc_public_key,
            self.__database_api_identifier,
            deposit_amount=100000000000,
            url=url
        )
        self.committee_member_id = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("Successfully created a new committee member, id: '{}'".format(self.committee_member_id))

        lcc.set_step("Get committee member")
        params = [self.committee_member_id]
        response_id = self.send_request(
            self.get_request("get_committee_members", [params]), self.__database_api_identifier
        )
        get_committee_members_results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_committee_members' with params='{}'".format(params))

        lcc.set_step("Get committee member by id")
        response_id = self.send_request(self.get_request("get_objects", [params]), self.__database_api_identifier)
        get_objects_results = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with params: {}".format(params))

        lcc.set_step("Check length of received objects")
        require_that("'list of received objects'", get_objects_results, has_length(len(params)), quiet=True)

        lcc.set_step("Check the identity of returned results of api-methods: 'get_committee_members', 'get_objects'")
        require_that('results', get_objects_results, equal_to(get_committee_members_results), quiet=True)

    @lcc.test("Use in method call nonexistent committee member id")
    @lcc.depends_on("API.DatabaseApi.CommitteeMembers.GetCommitteeMembers.GetCommitteeMembers.method_main_check")
    def nonexistent_committee_member_id_in_method_call(self):
        lcc.set_step("Generate nonexistent committee_member_id")
        nonexistent_committee_member_id = self.utils.get_nonexistent_committee_member_id(
            self, self.__database_api_identifier
        )
        lcc.log_info('Nonexistent committee member id: {}'.format(nonexistent_committee_member_id))

        lcc.set_step("Get nonexistent committee member")
        param = [nonexistent_committee_member_id]
        response_id = self.send_request(
            self.get_request("get_committee_members", [param]), self.__database_api_identifier
        )
        result = self.get_response(response_id)["result"][0]
        lcc.log_info("Call method 'get_committee_members' with params='{}'".format(param))

        lcc.set_step("Check nonexistent committee member id")
        check_that("'get_committee_members result'", result, is_none())
