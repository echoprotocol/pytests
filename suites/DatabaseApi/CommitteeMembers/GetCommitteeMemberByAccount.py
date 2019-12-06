import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, has_length, check_that_in, equal_to, check_that, \
    not_equal_to, is_true, is_none

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_committee_member_by_account'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_committee_members", "get_committee_member_by_account")
@lcc.suite("Check work of method 'get_committee_member_by_account'", rank=1)
class GetCommitteeMemberByAccount(BaseTest):

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

    @lcc.test("Simple work of method 'get_committee_member_by_account'")
    def method_main_check(self):
        active_committee_members_ids, account_ids = [], []

        lcc.set_step("Get list of active committee members")
        response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
        active_committee_members = self.get_response(response_id, log_response=True)["result"]["active_committee_members"]
        for member in active_committee_members:
            active_committee_members_ids.append(member[0])
        lcc.log_info("Active committee members ids: '{}'".format(active_committee_members_ids))

        lcc.set_step("Call method 'get_objects'")
        response_id = self.send_request(self.get_request("get_objects", [active_committee_members_ids]),
                                        self.__database_api_identifier)
        committee_members = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with params='{}'".format(active_committee_members_ids))

        lcc.set_step("Get account ids list of active committee members")
        for committee_member in committee_members:
            account_ids.append(committee_member["committee_member_account"])
        lcc.log_info("Got list of account ids: {}".format(account_ids))

        for i, account_id in enumerate(account_ids):
            lcc.set_step("Call method 'get_committee_member_by_account' for active committee member #'{}'".format(i))
            response_id = self.send_request(self.get_request("get_committee_member_by_account", [account_id]),
                                            self.__database_api_identifier, debug_mode=True)
            committee_member = self.get_response(response_id, log_response=True)["result"]
            lcc.log_info("Call method 'get_committee_member_by_account' with param='{}'".format(account_id))

            lcc.set_step("Check method 'get_committee_members_by_account' result")
            self.object_validator.validate_committee_member_object(self, committee_member)


@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_committee_members", "get_committee_member_by_account")
@lcc.suite("Positive testing of method 'get_committee_member_by_account'", rank=2)
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

    @lcc.test("Create new committee member")
    @lcc.depends_on(
        "DatabaseApi.CommitteeMembers.GetCommitteeMemberByAccount.GetCommitteeMemberByAccount.method_main_check")
    def create_committee_member(self, get_random_valid_account_name, get_random_url, get_random_eth_address,
                                get_random_btc_public_key):
        new_account = get_random_valid_account_name
        url = get_random_url
        eth_account_address = get_random_eth_address
        btc_public_key = get_random_btc_public_key

        lcc.set_step("Create and get new account")
        self.new_account_id = self.get_account_id(new_account, self.__database_api_identifier,
                                                  self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(self.new_account_id))

        lcc.set_step("Create committee member of new account in the ECHO network")
        broadcast_result = self.utils.perform_committee_member_create_operation(self, self.new_account_id,
                                                                                eth_account_address, btc_public_key,
                                                                                self.__database_api_identifier,
                                                                                deposit_amount=100000000000, url=url,
                                                                                log_broadcast=True)
        self.committee_member_id = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("Successfully created a new committee member, id: '{}'".format(self.committee_member_id))

        lcc.set_step("Get created committee member")
        response_id = self.send_request(self.get_request("get_committee_member_by_account", [self.new_account_id]),
                                        self.__database_api_identifier, debug_mode=True)
        committee_member = self.get_response(response_id, log_response=True)["result"]
        lcc.log_info("Call method 'get_committee_member_by_account' with param='{}'".format(self.new_account_id))

        lcc.set_step("Check created committee member in the ECHO network")
        require_that("'committee member object'", committee_member, has_length(6))
        check_that_in(
            committee_member,
            "id", equal_to(self.committee_member_id),
            "committee_member_account", equal_to(self.new_account_id),
            "url", equal_to(url)
        )
        check_that("'eth_address'", committee_member["eth_address"].lower(), equal_to(eth_account_address))
        check_that("'btc_public_key'", committee_member["btc_public_key"].lower(), equal_to(btc_public_key))

    @lcc.test("Update new committee member")
    @lcc.depends_on("DatabaseApi.CommitteeMembers.GetCommitteeMemberByAccount.PositiveTesting.create_committee_member")
    def update_committee_member(self, get_random_url, get_random_eth_address, get_random_btc_public_key):
        new_url = get_random_url
        new_eth_address = get_random_eth_address
        new_btc_public_key = get_random_btc_public_key

        lcc.set_step("Get committee member before update")
        response_id = self.send_request(self.get_request("get_committee_member_by_account", [self.new_account_id]),
                                        self.__database_api_identifier)
        committee_member_before_update = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_committee_member_by_account' with params='{}'".format(self.new_account_id))

        lcc.set_step("Perform committee member update operation")
        self.utils.perform_committee_member_update_operation(self, self.committee_member_id, self.new_account_id,
                                                             self.__database_api_identifier,
                                                             new_eth_address=new_eth_address,
                                                             new_btc_public_key=new_btc_public_key,
                                                             new_url=new_url)
        lcc.log_info("Update committee member completed successfully")

        lcc.set_step("Get committee member after update")
        response_id = self.send_request(self.get_request("get_committee_member_by_account", [self.new_account_id]),
                                        self.__database_api_identifier)
        committee_member_after_update = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_committee_member_by_account' with param='{}'".format(self.new_account_id))

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
            "btc_public_key", not_equal_to(committee_member_before_update["btc_public_key"]),
        )
        check_that("'new_eth_address'", committee_member_after_update["eth_address"].lower(), equal_to(new_eth_address))
        check_that("'new_btc_public_key'", committee_member_after_update["btc_public_key"].lower(),
                   equal_to(new_btc_public_key))

    @lcc.test("Get nonexistent committee member")
    @lcc.depends_on(
        "DatabaseApi.CommitteeMembers.GetCommitteeMemberByAccount.GetCommitteeMemberByAccount.method_main_check")
    def get_nonexistent_committee_member(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name

        lcc.set_step("Create and get new account")
        self.new_account_id = self.get_account_id(new_account, self.__database_api_identifier,
                                                  self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(self.new_account_id))

        lcc.set_step("Get nonexistent committee member")
        response_id = self.send_request(self.get_request("get_committee_member_by_account", [self.new_account_id]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_committee_member_by_account' with params='{}'".format(self.new_account_id))

        lcc.set_step("Check nonexistent committee member result")
        require_that("'get_committee_member_by_account result'", result, is_none())
