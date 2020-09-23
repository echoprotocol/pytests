# -*- coding: utf-8 -*-
import time

from common.base_test import BaseTest
from project import INIT0_PK, INIT1_PK, INIT2_PK, INIT3_PK, INIT4_PK, REQUIRED_DEPOSIT_AMOUNT, ROPSTEN

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, is_false, is_true, not_equal_to, require_that

SUITE = {
    "description": "Check for updating the list of active committee members"
}


@lcc.prop("main", "type")
@lcc.tags("scenarios", "sidechain", "sidechain_ethereum", "change_active_committee_member")
@lcc.suite("Check scenario 'Change active committee members'")
class ChangeActiveCommitteeMember(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.init0 = None
        self.init1 = None
        self.init2 = None
        self.init3 = None
        self.init4 = None

    def get_active_committee_members_eth_addresses(self, active_committee_members_ids=None, print_log=True):
        if active_committee_members_ids is not None:
            active_committee_members_ids = [active_committee_members_ids]
        else:
            active_committee_members_ids = [
                ids["committee_id"] for ids in self.get_active_committee_members_info(self.__database_api_identifier)
            ]
        eth_addresses = []
        response_id = self.send_request(
            self.get_request("get_committee_members", [active_committee_members_ids]), self.__database_api_identifier
        )
        committee_members_objs = self.get_response(response_id)["result"]
        for i, committee_member_obj in enumerate(committee_members_objs):
            if committee_member_obj["id"] == active_committee_members_ids[i]:
                eth_addresses.append(committee_member_obj["eth_address"])
                if print_log:
                    lcc.log_info(
                        "'{}' active committee members has '{}' eth_address".format(
                            active_committee_members_ids[i], eth_addresses[i]
                        )
                    )
        if len(eth_addresses) == 1:
            return eth_addresses[0]
        return eth_addresses

    def get_active_committee_members(self):
        return {
            "ids": [
                ids["committee_id"] for ids in self.get_active_committee_members_info(self.__database_api_identifier)
            ],
            "eth_addresses": self.get_active_committee_members_eth_addresses()
        }

    def setup_suite(self):
        if not ROPSTEN:
            super().setup_suite()
            self._connect_to_ethereum()
            self._connect_to_echopy_lib()
            lcc.set_step("Setup for {}".format(self.__class__.__name__))
            self.__database_api_identifier = self.get_identifier("database")
            self.__registration_api_identifier = self.get_identifier("registration")
            lcc.log_info(
                "API identifiers are: database='{}', registration='{}'".format(
                    self.__database_api_identifier, self.__registration_api_identifier
                )
            )
            self.echo_acc0 = self.get_account_id(
                self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
            )
            lcc.log_info("Echo account is '{}'".format(self.echo_acc0))
            committee_members_info = self.get_active_committee_members_info(self.__database_api_identifier)
            self.init0 = committee_members_info[0]["account_id"]
            self.init1 = committee_members_info[1]["account_id"]
            self.init2 = committee_members_info[2]["account_id"]
            self.init3 = committee_members_info[3]["account_id"]
            self.init4 = committee_members_info[4]["account_id"]
            lcc.log_info(
                "Echo  initial accounts: {}, {}, {}, {}, {}".format(
                    self.init0, self.init1, self.init2, self.init3, self.init4
                )
            )
        else:
            lcc.log_warning(
                "Tests did not run in the local network. Scenario 'change_active_committee_member' was skipped."
            )

    def teardown_suite(self):
        if not ROPSTEN:
            self._disconnect_to_echopy_lib()
            super().teardown_suite()

    @lcc.test("The scenario describes the mechanism of updating the list of active committee members")
    def change_active_committee_member(
        self, get_random_valid_account_name, get_random_eth_address, get_random_btc_public_key
    ):
        new_account = get_random_valid_account_name
        eth_account_address = get_random_eth_address
        btc_public_key = get_random_btc_public_key

        if not ROPSTEN:
            lcc.set_step("Get active committee members ids, ethereum addresses and store")
            active_committee_members = self.get_active_committee_members()
            active_committee_members_ids = active_committee_members["ids"]

            lcc.set_step("Get all committee members statuses. Store active committee members")
            for eth_address in active_committee_members["eth_addresses"][:-1]:
                committee_member_status = self.eth_trx.get_status_of_committee_member(self, self.web3, eth_address)
                if not committee_member_status:
                    raise Exception(
                        "Active committee member with '{}' eth_address in the ECHO network "
                        "do not compare with members in the Ethereum network".format(eth_address)
                    )
                lcc.log_info("Address '{}' is active: '{}'".format(eth_address, committee_member_status))

            lcc.set_step("Register new account in the ECHO network")
            new_account_id = self.get_account_id(
                new_account, self.__database_api_identifier, self.__registration_api_identifier
            )
            lcc.log_info("New Echo account created, account_id='{}'".format(new_account_id))

            lcc.set_step("Create created account as new committee member in the ECHO network")
            broadcast_result = self.utils.perform_committee_member_create_operation(
                self,
                new_account_id,
                eth_account_address,
                btc_public_key,
                self.__database_api_identifier,
                deposit_amount=REQUIRED_DEPOSIT_AMOUNT
            )
            committee_member_id = broadcast_result["trx"]["operation_results"][0][1]
            lcc.log_info("New committee member id: {}".format(committee_member_id))

            lcc.set_step("Collect 'committee_member_activate_operation'")
            operation = \
                self.echo_ops.get_committee_member_activate_operation(echo=self.echo,
                                                                      committee_to_activate=committee_member_id,
                                                                      committee_member_activate=new_account_id)
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            lcc.log_info("Collected successfully")

            lcc.set_step("Make proposal operation of new active committee member")
            operation = self.echo_ops.get_proposal_create_operation(
                echo=self.echo,
                fee_paying_account=self.init0,
                proposed_ops=collected_operation,
                expiration_time=self.get_expiration_time(15),
                review_period_seconds=10,
                signer=INIT0_PK
            )
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
            if not self.is_operation_completed(broadcast_result, expected_static_variant=1):
                raise Exception("Operation 'proposal_created' failed while broadcast")
            proposal_id = broadcast_result["trx"]["operation_results"][0][1]
            lcc.log_info("Proposal id {}".format(proposal_id))

            lcc.set_step("Make voting for new active committee member")
            operation = self.echo_ops.get_proposal_update_operation(
                echo=self.echo,
                fee_paying_account=self.init0,
                proposal=proposal_id,
                active_approvals_to_add=[self.init0, self.init1, self.init2, self.init3, self.init4],
                active_approvals_to_remove=[],
                key_approvals_to_add=[],
                key_approvals_to_remove=[],
                signer=[INIT0_PK, INIT1_PK, INIT2_PK, INIT3_PK, INIT4_PK]
            )
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
            if not self.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Operation 'proposal_update' failed while broadcast")
            lcc.log_info("All committee member has voted")

            lcc.set_step("Set timer for proposal expiration")
            time.sleep(15)
            self.produce_block(self.__database_api_identifier)
            lcc.log_info("Voting finished.")

            lcc.set_step("Set timer for sidechain")
            time.sleep(5)
            self.produce_block(self.__database_api_identifier)
            lcc.log_info("Timer expired")

            lcc.set_step("Get updated active committee members ids, ethereum addresses and store")
            updated_active_committee_members = self.get_active_committee_members()
            updated_active_committee_members_ids = updated_active_committee_members["ids"]

            lcc.set_step("Check that new committee member added.")
            require_that(
                "'updated list of active committee members'",
                updated_active_committee_members_ids,
                not_equal_to(active_committee_members_ids),
                quiet=True
            )
            updated_active_committee_members_ids_set = set(updated_active_committee_members_ids)
            active_committee_members_ids_set = set(active_committee_members_ids)
            new_member_id = updated_active_committee_members_ids_set.difference(active_committee_members_ids_set)
            new_member_id = new_member_id.pop()
            require_that("'new committee member'", new_member_id, equal_to(committee_member_id), quiet=True)

            lcc.set_step("Check that new committee member became active committee member.")
            new_member_address = self.get_active_committee_members_eth_addresses(new_member_id, print_log=False)
            lcc.log_info("'{}' new committee member address: '{}'".format(new_member_id, new_member_address))
            new_committee_member_status = self.eth_trx.get_status_of_committee_member(
                self, self.web3, new_member_address
            )
            check_that(
                "'status of new committee member '{}''".format(new_member_address),
                new_committee_member_status,
                is_true(),
                quiet=True
            )

            lcc.set_step("Collect 'committee_member_deactivate_operation'")
            operation = \
                self.echo_ops.get_committee_member_deactivate_operation(
                    echo=self.echo,
                    committee_member_account=new_member_id,
                    committee_to_deactivate=committee_member_id,
                    signer=INIT0_PK
                )
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            lcc.log_info("Collected successfully")

            lcc.set_step("Make proposal of deactivating new account")
            operation = self.echo_ops.get_proposal_create_operation(
                echo=self.echo,
                fee_paying_account=self.init0,
                proposed_ops=collected_operation,
                expiration_time=self.get_expiration_time(15),
                review_period_seconds=10,
                signer=INIT0_PK
            )
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
            proposal_id = broadcast_result["trx"]["operation_results"][0][1]
            lcc.log_info("Proposal id {}".format(proposal_id))

            lcc.set_step("Make voting for new active committee member")
            operation = self.echo_ops.get_proposal_update_operation(
                echo=self.echo,
                fee_paying_account=self.init0,
                proposal=proposal_id,
                active_approvals_to_add=[self.init0, self.init1, self.init2, self.init3, self.init4],
                active_approvals_to_remove=[],
                key_approvals_to_add=[],
                key_approvals_to_remove=[],
                signer=[INIT0_PK, INIT1_PK, INIT2_PK, INIT3_PK, INIT4_PK]
            )
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

            lcc.set_step("Set timer for proposal expiration")
            time.sleep(15)
            self.produce_block(self.__database_api_identifier)
            lcc.log_info("Voting finished.")

            lcc.set_step("Set timer for sidechain")
            time.sleep(30)
            self.produce_block(self.__database_api_identifier)
            lcc.log_info("Timer expired")

            lcc.set_step("Get updated active committee members ids, ethereum addresses and store")
            active_committee_members_ids = updated_active_committee_members_ids
            updated_active_committee_members = self.get_active_committee_members()
            updated_active_committee_members_ids = updated_active_committee_members["ids"]

            lcc.set_step("Check that new committee member deleted.")
            require_that(
                "'updated list of active committee members'",
                active_committee_members_ids,
                not_equal_to(updated_active_committee_members_ids),
                quiet=True
            )
            active_committee_members_ids_set = set(active_committee_members_ids)
            updated_active_committee_members_ids_set = set(updated_active_committee_members_ids)
            deleted_member_id = active_committee_members_ids_set.difference(updated_active_committee_members_ids_set)
            deleted_member_id = deleted_member_id.pop()
            require_that("'deleted committee member'", new_member_id, equal_to(deleted_member_id))

            new_committee_member_status = self.eth_trx.get_status_of_committee_member(
                self, self.web3, new_member_address
            )
            check_that(
                "'status of new committee member '{}''".format(new_member_address),
                new_committee_member_status,
                is_false(),
                quiet=True
            )
        else:
            lcc.log_warning(
                "Tests did not run in the local network. Scenario 'change_active_committee_member' was skipped."
            )
