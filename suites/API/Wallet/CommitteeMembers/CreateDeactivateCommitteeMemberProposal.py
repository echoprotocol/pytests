# -*- coding: utf-8 -*-
import time

from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import INIT0_PK, INIT1_PK, INIT2_PK, INIT3_PK, INIT4_PK, INIT5_PK

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, not_equal_to

SUITE = {
    "description": "Method 'create_deactivate_committee_member_proposal'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_committee_member", "wallet_create_deactivate_committee_member_proposal")
@lcc.suite("Check work of method 'create_deactivate_committee_member_proposal'", rank=1)
class CreateDeactivateCommitteeMemberProposal(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier
            )
        )

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    def get_active_committee_members(self):
        return {
            "ids": [
                ids["committee_id"] for ids in self.get_active_committee_members_info(self.__database_api_identifier)
            ]
        }

    @lcc.depends_on(
        "API.Wallet.CommitteeMembers.CreateActivateCommitteeMemberProposal.CreateActivateCommitteeMemberProposal.method_main_check"
    )
    @lcc.test("Simple work of method 'wallet_create_deactivate_committee_member_proposal'")
    def method_main_check(self, get_random_eth_address, get_random_btc_public_key):
        self.unlock_wallet()

        lcc.set_step("Import key")
        self.send_wallet_request("import_key", ['init4', INIT4_PK], log_response=False)
        self.send_wallet_request("import_key", ['init5', INIT5_PK], log_response=False)
        lcc.log_info("Key imported")

        lcc.set_step("Get initial account ids")
        self.init0 = self.get_account_id('init0', self.__database_api_identifier, self.__registration_api_identifier)
        self.init1 = self.get_account_id('init1', self.__database_api_identifier, self.__registration_api_identifier)
        self.init2 = self.get_account_id('init2', self.__database_api_identifier, self.__registration_api_identifier)
        self.init3 = self.get_account_id('init3', self.__database_api_identifier, self.__registration_api_identifier)
        self.init4 = self.get_account_id('init4', self.__database_api_identifier, self.__registration_api_identifier)
        self.init5 = self.get_account_id('init5', self.__database_api_identifier, self.__registration_api_identifier)
        lcc.log_info(
            "Initial account ids: '{}', '{}', '{}', '{}', '{}', '{}'".format(
                self.init0, self.init1, self.init2, self.init3, self.init4, self.init5
            )
        )
        lcc.set_step("Get active committee members list")
        active_committee_members = self.get_active_committee_members()
        active_committee_members_ids = active_committee_members["ids"]
        lcc.log_info("Active committee members are {}".format(active_committee_members_ids))

        lcc.set_step("Get '{}' committee id".format(self.init5))
        response_id = self.send_request(
            self.get_request("get_committee_member_by_account", [self.init5]), self.__database_api_identifier
        )
        init5_committee_member_id = self.get_response(response_id)["result"]['id']
        lcc.log_info("Account committee id: {}".format(init5_committee_member_id))

        lcc.set_step("Create deactivate committee member proposal")
        expiration_time = self.get_expiration_time(seconds=15)
        proposal = self.send_wallet_request(
            "create_deactivate_committee_member_proposal", [self.init4, init5_committee_member_id, expiration_time],
            log_response=False
        )
        self.produce_block(self.__database_api_identifier)

        lcc.log_info("Search for a block with deactivate committee member proposal")
        block = int(proposal['result']['ref_block_num'])
        proposal_id = self.get_proposal_id_from_next_blocks(block)
        lcc.log_info("Block found, proposal id in block: '{}'".format(proposal_id))

        lcc.set_step("Update proposal with committee deactivate")
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
        check_that(
            'active committee members list', active_committee_members_ids,
            not_equal_to(updated_active_committee_members_ids)
        )
