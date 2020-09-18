# -*- coding: utf-8 -*-
import time

from common.base_test import BaseTest
from project import INIT0_PK, INIT1_PK, INIT2_PK, INIT3_PK, INIT4_PK

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, not_equal_to

SUITE = {
    "description": "Operation 'committee_member_deactivate'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "committee_member_operations", "committee_member_deactivate")
@lcc.suite("Check work of operation 'committee_member_deactivate'", rank=1)
class CommitteeMemberDeactivate(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.init0 = None
        self.init1 = None
        self.init2 = None
        self.init3 = None
        self.init4 = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_ethereum()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.committee_members_info = self.get_active_committee_members_info(self.__database_api_identifier)
        self.init0 = self.committee_members_info[0]["account_id"]
        self.init1 = self.committee_members_info[1]["account_id"]
        self.init2 = self.committee_members_info[2]["account_id"]
        self.init3 = self.committee_members_info[3]["account_id"]
        self.init4 = self.committee_members_info[4]["account_id"]
        lcc.log_info(
            "Echo  initial accounts: {}, {}, {}, {}, {}".format(
                self.init0, self.init1, self.init2, self.init3, self.init4
            )
        )

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    # todo: Bug ECHO-2400
    @lcc.disabled()
    @lcc.test("Simple work of operation 'committee_member_deactivate'")
    @lcc.depends_on("Operations.CommitteeMember.CommitteeMemberActivate.CommitteeMemberActivate.method_main_check")
    def method_main_check(self):
        operation = self.echo_ops.get_committee_member_deactivate_operation(
            echo=self.echo,
            committee_member_account=self.init0,
            committee_to_deactivate=self.committee_members_info[-1]["committee_id"],
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
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=operation)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception("Operation 'proposal_created' failed while broadcast")
        proposal_id = broadcast_result["trx"]["operation_results"][0][1]
        lcc.set_step("Make voting of deactivating new account")
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

        lcc.set_step(
            "Waiting for maintenance and release of two blocks and check that new committee member were deactivated"
        )
        self.produce_block(self.__database_api_identifier)
        time.sleep(15)
        self.produce_block(self.__database_api_identifier)
        check_that(
            "acitve committee member",
            self.committee_members_info[-1]["account_id"],
            not_equal_to(self.get_active_committee_members_info(self.__database_api_identifier)[-1]["account_id"]),
            quiet=True
        )
