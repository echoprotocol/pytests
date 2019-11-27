# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc

from common.base_test import BaseTest
from datetime import datetime, timedelta

from project import INIT0_PK, INIT1_PK, INIT2_PK, INIT3_PK, INIT4_PK

SUITE = {
    "description": "Operation 'committee_member_deactivate'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("operations", "committee_member_operations", "committee_member_deactivate")
@lcc.suite("Check work of operation 'committee_member_deactivate'", rank=1)
class CommitteeMemberDeactivate(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def get_active_committee_members_ids_and_account_ids(self):
        response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
        active_committee_members = self.get_response(response_id)["result"][
            "active_committee_members"]
        committee_members_ids = [[], []]
        for member in active_committee_members:
            committee_members_ids[0].append(member[0])
            committee_members_ids[1].append(member[1])
        return committee_members_ids

    def get_expiration_time(self, seconds):
        pattern = "%Y-%m-%dT%H:%M:%S"
        now = self.get_datetime(global_datetime=True)
        expiration = datetime.strptime(now, pattern) + timedelta(seconds=seconds)
        return expiration.strftime(pattern)

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_ethereum()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'committee_member_deactivate'")
    @lcc.depends_on("Operations.CommitteeMember.CommitteeMemberActivate.CommitteeMemberActivate.method_main_check")
    def committee_member_deactivate_operation(self):
        lcc.set_step("Get active committee members ids, ethereum addresses and store")
        active_committe_member_ids = self.get_active_committee_members_ids_and_account_ids()
        committee_members_ids, committee_members_account_ids = active_committe_member_ids[0], active_committe_member_ids[1]
        new_member_id = committee_members_ids.pop()
        committee_members_account_ids.pop()
        fee_paying_account = committee_members_account_ids[0]

        operation = self.echo_ops.get_committee_member_deactivate_operation(
            echo=self.echo,
            committee_member_account=fee_paying_account,
            committee_to_deactivate=new_member_id,
            signer=INIT0_PK)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        lcc.log_info("Collected successfully")
        lcc.set_step("Make proposal of deactivating new account")
        operation = self.echo_ops.get_proposal_create_operation(
            echo=self.echo,
            fee_paying_account=fee_paying_account,
            proposed_ops=collected_operation,
            expiration_time=self.get_expiration_time(15),
            review_period_seconds=10,
            signer=INIT0_PK
        )
        lcc.log_info("{}".format(operation))
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=operation)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception("Operation 'proposal_created' failed while broadcast")
        proposal_id = broadcast_result["trx"]["operation_results"][0][1]
        lcc.set_step("Make voting of deactivating new account")
        operation = self.echo_ops.get_proposal_update_operation(
            echo=self.echo,
            fee_paying_account=fee_paying_account,
            proposal=proposal_id,
            active_approvals_to_add=committee_members_account_ids,
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

        lcc.set_step("Waiting for maintenance and release of two blocks and check that new committee member were deactivated")
        self.produce_block(self.__database_api_identifier)
        import time
        time.sleep(15)
        self.produce_block(self.__database_api_identifier)

        current_active_committe_members = self.get_active_committee_members_ids_and_account_ids()
        if new_member_id not in current_active_committe_members:
            lcc.log_info("new acitve committee member were deactivated")
        else:
            lcc.log_error("new acitve committee member has not been deactivated")
