# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, equal_to, has_length, is_true, check_that

from common.base_test import BaseTest
from fixtures.base_fixtures import get_random_eth_address, get_random_btc_public_key

SUITE = {
    "description": "Method 'lookup_committee_member_accounts'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_committee_members", "lookup_committee_member_accounts")
@lcc.suite("Check work of method 'lookup_committee_member_accounts'", rank=1)
class LookupCommitteeMemberAccounts(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

    def check_lookup_committee_member_accounts_structure(self, lookup_committee_member_account):
        if not self.validator.is_account_name(lookup_committee_member_account[0]):
            lcc.log_error("Wrong format of 'account name', got: {}".format(lookup_committee_member_account[0]))
        else:
            lcc.log_info("'account name' has correct format: account_name")
        if not self.validator.is_committee_member_id(lookup_committee_member_account[1]):
            lcc.log_error("Wrong format of 'account id', got: {}".format(lookup_committee_member_account[1]))
        else:
            lcc.log_info("'account id' has correct format: account_id")

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.test("Simple work of method 'lookup_committee_member_accounts'")
    def method_main_check(self):
        active_committee_members_ids, committee_member_accounts, account_names = [], [], []
        limit = 1

        lcc.set_step("Get list of active committee member ids")
        response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
        active_committee_members = self.get_response(response_id, log_response=True)["result"][
            "active_committee_members"]
        for member in active_committee_members:
            active_committee_members_ids.append(member[0])
        lcc.log_info("Active committee members ids: '{}'".format(active_committee_members_ids))

        lcc.set_step("Get active committee members")
        response_id = self.send_request(self.get_request("get_objects", [active_committee_members_ids]),
                                        self.__database_api_identifier)
        committee_members = self.get_response(response_id)["result"]
        for committee_member in committee_members:
            committee_member_accounts.append(committee_member["committee_member_account"])
        lcc.log_info("Call method 'get_objects' with params='{}'".format(active_committee_members_ids))

        lcc.set_step("Get info about default accounts")
        response_id = self.send_request(self.get_request("get_accounts", [committee_member_accounts]),
                                        self.__database_api_identifier)
        accounts_info = self.get_response(response_id)["result"]
        for account_info in accounts_info:
            account_names.append(account_info["name"])
        lcc.log_info("Call method 'get_accounts' with params='{}'".format(committee_member_accounts))

        for i, account_name in enumerate(account_names):
            lcc.set_step("Call method 'lookup_committee_member_accounts' for active committee member #'{}'".format(i))
            response_id = self.send_request(self.get_request("lookup_committee_member_accounts", [account_name, limit]),
                                            self.__database_api_identifier)
            committee_member_result = self.get_response(response_id)["result"][0]
            lcc.log_info(
                "Call method 'lookup_committee_member_accounts' with params='{}'".format(account_name))

            lcc.set_step("Check lookup committee member account result")
            require_that("'lookup committee member account result'", committee_member_result, has_length(2))
            self.check_lookup_committee_member_accounts_structure(committee_member_result)


@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_committee_members", "lookup_committee_member_accounts")
@lcc.suite("Positive testing of method 'lookup_committee_member_accounts'", rank=2)
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
            "API identifiers are: database='{}', registration='{}',".format(self.__database_api_identifier,
                                                                            self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Lookup new committee member accounts")
    @lcc.depends_on(
        "DatabaseApi.CommitteeMembers.LookupCommitteeMemberAccounts.LookupCommitteeMemberAccounts.method_main_check")
    def lookup_info_about_created_committee_members(self, get_random_valid_account_name):
        eth_account_addresses = [get_random_eth_address(), get_random_eth_address()]
        btc_public_key = [get_random_btc_public_key(), get_random_btc_public_key()]
        valid_account_name = get_random_valid_account_name
        account_count = 2
        committee_member_ids, account_ids = [], []

        lcc.set_step("Generate account names")
        account_names = self.proliferate_account_names(valid_account_name, account_count)
        lcc.log_info("Generated account names: {}".format(account_names))

        lcc.set_step("Create and get new accounts")
        for account_name in account_names:
            new_account_id = self.get_account_id(account_name, self.__database_api_identifier,
                                                 self.__registration_api_identifier)
            account_ids.append(new_account_id)
            lcc.log_info("New Echo account created, account_id='{}'".format(new_account_id))

        for i, accounts_id in enumerate(account_ids):
            lcc.set_step("Create committee member of new account in the ECHO network")
            broadcast_result = self.utils.perform_committee_member_create_operation(self, accounts_id,
                                                                                    eth_account_addresses[i],
                                                                                    btc_public_key[i],
                                                                                    self.__database_api_identifier,
                                                                                    deposit_amount=0)
            committee_member_id = self.get_operation_results_ids(broadcast_result)
            committee_member_ids.append(committee_member_id)
            lcc.log_info("Successfully created a new committee member, id: '{}'".format(committee_member_id))

        lcc.set_step("Lookup created committee member accounts")
        response_id = self.send_request(self.get_request("lookup_committee_member_accounts",
                                                         [valid_account_name, account_count]),
                                        self.__database_api_identifier)
        committee_members_info = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'lookup_committee_member_accounts' with params: lower_bound_name='{}', limit='{}'".
                     format(valid_account_name, account_count))

        for i, committee_member in enumerate(committee_members_info):
            lcc.set_step("Check info of lookup committee member accounts #{}".format(i))
            require_that("'lookup committee member account result'", committee_member, has_length(2))
            check_that("account name", committee_member[0], equal_to(account_names[i]))
            check_that("committee member account", committee_member[1], equal_to(committee_member_ids[i]))

    @lcc.test("Lookup nonexistent committee member accounts")
    @lcc.depends_on(
        "DatabaseApi.CommitteeMembers.LookupCommitteeMemberAccounts.LookupCommitteeMemberAccounts.method_main_check")
    def lookup_more_accounts_than_exists(self):
        lcc.set_step("Get parameters, for lookup committee member accounts more than exists")
        lower_bound_name, limit = self.utils.get_nonexistent_account_name(self, self.__database_api_identifier,
                                                                          committee_member=True)
        lcc.log_info("Got parameters: lower_bound_name='{}', limit='{}'".format(lower_bound_name, limit))

        lcc.set_step("Lookup committee member accounts")
        response_id = self.send_request(self.get_request("lookup_committee_member_accounts", [lower_bound_name, limit]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info(
            "Call method 'lookup_committee_member_accounts' with lower_bound_name='{}', limit='{}' parameters".format(
                lower_bound_name, limit))

        lcc.set_step("Check committee member accounts lookup info")
        accounts = response["result"]
        require_that(
            "'length of listed accounts'",
            accounts, has_length(limit - 1)
        )

    @lcc.test("Check alphabet order in full committee member accounts lookup info")
    @lcc.depends_on(
        "DatabaseApi.CommitteeMembers.LookupCommitteeMemberAccounts.LookupCommitteeMemberAccounts.method_main_check")
    def check_alphabet_order_in_full_committee_members_lookup_info(self):
        lower_bound_name, limit = "", 1000

        lcc.set_step("Lookup committee member accounts")
        response_id = self.send_request(self.get_request("lookup_committee_member_accounts", [lower_bound_name, limit]),
                                        self.__database_api_identifier)
        accounts = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'lookup_committee_member_accounts' with lower_bound_name='{}', limit='{}' parameters"
                     .format(lower_bound_name, limit))

        lcc.set_step("Check alphabet order in full committee member accounts lookup info")
        account_names = [account[0] for account in accounts]
        require_that(
            "'full committee member accounts lookup info in alphabet symbol order'",
            account_names == sorted(account_names.copy()), is_true()
        )

    @lcc.test("Check alphabet order in cut committee member accounts lookup info")
    @lcc.depends_on(
        "DatabaseApi.CommitteeMembers.LookupCommitteeMemberAccounts.LookupCommitteeMemberAccounts.method_main_check")
    def check_alphabet_order_in_cut_committee_members_accounts_lookup_info(self, get_random_valid_account_name):
        valid_account_name = get_random_valid_account_name
        limit = 1000

        lcc.set_step("Perform account creation operation and store accounts ids")
        new_account_id = self.get_account_id(valid_account_name, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account_id))

        lcc.set_step("Lookup committee member accounts")
        response_id = self.send_request(self.get_request("lookup_committee_member_accounts",
                                                         [valid_account_name, limit]), self.__database_api_identifier)
        accounts = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'lookup_committee_member_accounts' with lower_bound_name='{}', limit='{}' parameters"
                     .format(valid_account_name, limit))

        lcc.set_step("Check alphabet order in cut committee member accounts lookup info")
        account_names = [account[0] for account in accounts]
        require_that(
            "'cut committee member accounts lookup info in alphabet symbol order'",
            account_names == sorted(account_names.copy()), is_true()
        )
