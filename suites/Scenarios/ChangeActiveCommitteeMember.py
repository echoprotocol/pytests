# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_false, is_true, require_that, not_equal_to, equal_to

from common.base_test import BaseTest
from project import ROPSTEN

SUITE = {
    "description": "Check for updating the list of active committee members"
}


# todo: test fails at second time running
@lcc.prop("main", "type")
@lcc.tags("scenarios", "sidechain", "sidechain_ethereum", "change_active_committee_member")
@lcc.suite("Check scenario 'Change active committee members'")
class ChangeActiveCommitteeMember(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

    def get_active_committee_members_ids(self):
        response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
        return self.get_response(response_id, log_response=True)["result"]["active_committee_members"]

    def get_active_committee_members_eth_addresses(self, active_committee_members_ids=None, print_log=True):
        if active_committee_members_ids is not None:
            active_committee_members_ids = [active_committee_members_ids]
        else:
            active_committee_members_ids = self.get_active_committee_members_ids()
        eth_addresses = []
        response_id = self.send_request(self.get_request("get_committee_members", [active_committee_members_ids]),
                                        self.__database_api_identifier)
        committee_members_objs = self.get_response(response_id)["result"]
        for i, committee_member_obj in enumerate(committee_members_objs):
            if committee_member_obj["id"] == active_committee_members_ids[i]:
                eth_addresses.append(committee_member_obj["eth_address"])
                if print_log:
                    lcc.log_info(
                        "'{}' active committee members has '{}' eth_address".format(active_committee_members_ids[i],
                                                                                    eth_addresses[i]))
        if len(eth_addresses) == 1:
            return eth_addresses[0]
        return eth_addresses

    def get_active_committee_members(self):
        return {"ids": self.get_active_committee_members_ids(),
                "eth_addresses": self.get_active_committee_members_eth_addresses()}

    def setup_suite(self):
        if not ROPSTEN:
            super().setup_suite()
            self._connect_to_ethereum()
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
        else:
            lcc.log_warning(
                "Tests did not run in the local network. Scenario 'change_active_committee_member' was skipped.")

    def teardown_suite(self):
        if not ROPSTEN:
            self._disconnect_to_echopy_lib()
            super().teardown_suite()

    @lcc.test("The scenario describes the mechanism of updating the list of active addresses of committee members")
    def change_committee_eth_address_scenario(self):
        if not ROPSTEN:
            committee_member_name = "init5"

            lcc.set_step("Get active committee members ids, ethereum addresses and store")
            active_committee_members = self.get_active_committee_members()
            active_committee_members_ids = active_committee_members["ids"]

            lcc.set_step("Get all committee members statuses. Store active committee members")
            for eth_address in active_committee_members["eth_addresses"]:
                committee_member_status = self.eth_trx.get_status_of_committee_member(self, self.web3, eth_address)
                if not committee_member_status:
                    raise Exception("Active committee member with '{}' eth_address in the ECHO network "
                                    "do not compare with members in the Ethereum network".format(eth_address))
                lcc.log_info("Address '{}' is active: '{}'".format(eth_address, committee_member_status))

            lcc.set_step("Get committee member account id")
            response_id = self.send_request(self.get_request("get_account_by_name", [committee_member_name]),
                                            self.__database_api_identifier)
            committee_member_account_id = self.get_response(response_id)["result"]["id"]
            lcc.log_info("Account id of committee member: '{}'".format(committee_member_account_id))

            lcc.set_step("Get committee member id")
            response_id = self.send_request(
                self.get_request("get_committee_member_by_account", [committee_member_account_id]),
                self.__database_api_identifier)
            committee_member_id = self.get_response(response_id)["result"]["id"]
            lcc.log_info("Committee member id: '{}'".format(committee_member_id))

            lcc.set_step("Get info about object committee member account id")
            response_id = self.send_request(self.get_request("get_objects", [[committee_member_id]]),
                                            self.__database_api_identifier)
            vote_id = self.get_response(response_id)["result"][0]["vote_id"]
            lcc.log_info("Vote id of new committee member: '{}'".format(vote_id))

            lcc.set_step("Get info about account and store")
            response_id = self.send_request(self.get_request("get_accounts", [[self.echo_acc0]]),
                                            self.__database_api_identifier)
            account_info = self.get_response(response_id)["result"][0]
            lcc.log_info("Information about current '{}' account stored".format(self.echo_acc0))

            lcc.set_step("Perform 'account_update_operation' to vote for new committee member")
            account_info["options"]["votes"].append(vote_id)
            self.utils.perform_account_update_operation(self, self.echo_acc0, account_info,
                                                        self.__database_api_identifier)
            lcc.log_info(
                "'{}' account vote for new '{}' committee member".format(self.echo_acc0, committee_member_account_id))

            lcc.set_step("Waiting for maintenance and release of two blocks")
            self.wait_for_next_maintenance(self.__database_api_identifier, print_log=True)
            self.utils.set_timeout_until_num_blocks_released(self, self.__database_api_identifier, wait_block_count=2,
                                                             print_log=False)

            lcc.set_step("Get updated active committee members ids, ethereum addresses and store")
            updated_active_committee_members = self.get_active_committee_members()
            updated_active_committee_members_ids = updated_active_committee_members["ids"]

            lcc.set_step("Check that new committee member added. Store old and new committee members ids")
            require_that("'updated list of active committee members'", updated_active_committee_members_ids,
                         not_equal_to(active_committee_members_ids))
            old_member_id = set(active_committee_members_ids).difference(
                set(updated_active_committee_members_ids)).pop()
            new_member_id = set(updated_active_committee_members_ids).difference(
                set(active_committee_members_ids)).pop()
            require_that("'new committee member'", new_member_id, equal_to(committee_member_id))
            lcc.log_info(
                "Old committee member id: '{}', new committee member id: '{}'".format(old_member_id, new_member_id))

            lcc.set_step("Check that new committee member became active committee member, old - not active")
            old_member_address = self.get_active_committee_members_eth_addresses(old_member_id, print_log=False)
            new_member_address = self.get_active_committee_members_eth_addresses(new_member_id, print_log=False)
            lcc.log_info("'{}' old committee member address: '{}', '{}' new committee member address: '{}'"
                         "".format(old_member_id, old_member_address, new_member_id, new_member_address))

            new_committee_member_status = self.eth_trx.get_status_of_committee_member(self, self.web3,
                                                                                      new_member_address)
            check_that("'status of new committee member '{}''".format(new_member_address),
                       new_committee_member_status,
                       is_true())

            old_committee_member_status = self.eth_trx.get_status_of_committee_member(self, self.web3,
                                                                                      old_member_address)
            check_that("'status of old committee member '{}''".format(old_member_address),
                       old_committee_member_status,
                       is_false())

            lcc.set_step("Get info about object old committee member account id")
            old_committee_member_account_id = old_member_id
            param = [old_committee_member_account_id]
            response_id = self.send_request(self.get_request("get_objects", [param]), self.__database_api_identifier)
            vote_id = self.get_response(response_id)["result"][0]["vote_id"]
            lcc.log_info("Vote id of old committee member: '{}'".format(vote_id))

            lcc.set_step("Get info about account and store")
            response_id = self.send_request(self.get_request("get_accounts", [[self.echo_acc0]]),
                                            self.__database_api_identifier)
            account_info = self.get_response(response_id)["result"][0]
            lcc.log_info("Information about current '{}' account stored".format(self.echo_acc0))

            lcc.set_step("Perform 'account_update_operation' to vote for old committee member")
            account_info["options"]["votes"] = [vote_id]
            self.utils.perform_account_update_operation(self, self.echo_acc0, account_info,
                                                        self.__database_api_identifier)
            lcc.log_info("'{}' account vote for old '{}' committee member".format(self.echo_acc0, old_member_id))

            lcc.set_step("Waiting for maintenance and release of two blocks")
            self.wait_for_next_maintenance(self.__database_api_identifier, print_log=True)
            self.utils.set_timeout_until_num_blocks_released(self, self.__database_api_identifier, wait_block_count=2,
                                                             print_log=False)

            lcc.set_step("Get updated active committee members ids, ethereum addresses and store")
            active_committee_members_ids = updated_active_committee_members_ids
            updated_active_committee_members = self.get_active_committee_members()
            updated_active_committee_members_ids = updated_active_committee_members["ids"]

            lcc.set_step("Check that old committee member added. Store old and new committee members ids")
            require_that("'updated list of active committee members'", updated_active_committee_members_ids,
                         not_equal_to(active_committee_members_ids))
            old_member_id = set(active_committee_members_ids).difference(
                set(updated_active_committee_members_ids)).pop()
            new_member_id = set(updated_active_committee_members_ids).difference(
                set(active_committee_members_ids)).pop()
            require_that("'new committee member'", new_member_id, equal_to(old_committee_member_account_id))
            lcc.log_info(
                "Old committee member id: '{}', new committee member id: '{}'".format(old_member_id, new_member_id))

            lcc.set_step("Check that new committee member became not active committee member, old - active")
            old_member_address = self.get_active_committee_members_eth_addresses(old_member_id, print_log=False)
            new_member_address = self.get_active_committee_members_eth_addresses(new_member_id, print_log=False)
            lcc.log_info("'{}' old committee member address: '{}', '{}' new committee member address: '{}'"
                         "".format(old_member_id, old_member_address, new_member_id, new_member_address))

            new_committee_member_status = self.eth_trx.get_status_of_committee_member(self, self.web3,
                                                                                      new_member_address)
            check_that("'status of new committee member '{}''".format(new_member_address),
                       new_committee_member_status, is_true())

            old_committee_member_status = self.eth_trx.get_status_of_committee_member(self, self.web3,
                                                                                      old_member_address)
            check_that("'status of old committee member '{}''".format(old_member_address),
                       old_committee_member_status, is_false())
        else:
            lcc.log_warning(
                "Tests did not run in the local network. Scenario 'change_active_committee_member' was skipped.")
