# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc

from common.base_test import BaseTest
from datetime import datetime, timedelta

SUITE = {
    "description": "Operation 'committee_member_deactivate'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("operations", "committee_member_operations", "committee_member_deactivate")
@lcc.suite("Check work of method 'committee_member_deactivate'", rank=1)
class CommitteeMemberActivate(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def get_active_committee_members_ids(self):
        response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
        active_committee_members = self.get_response(response_id)["result"][
            "active_committee_members"]
        return [member[0] for member in active_committee_members]

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
        active_committe_members = self.get_active_committee_members_ids()
        new_member_id = active_committe_members[-1]
        operation = self.echo_ops.get_committee_member_deactivate_operation(
            echo=self.echo,
            committee_member_account=new_member_id,
            committee_to_deactivate=new_member_id,
            signer="5J6azg8iUcQEbxEaLAFrJbcdBjgKqewLF81A63NE4T2aeHCsKiE")
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        lcc.log_info("Collected successfully")
        lcc.set_step("Make proposal of deactivating new account")
        operation = self.echo_ops.get_proposal_create_operation(
            echo=self.echo,
            fee_paying_account="1.2.6",
            proposed_ops=[{"op": collected_operation[0]}],
            expiration_time=self.get_expiration_time(15),
            review_period_seconds=10,
            signer="5J6azg8iUcQEbxEaLAFrJbcdBjgKqewLF81A63NE4T2aeHCsKiE"
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier, proposal=True)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        proposal_id = broadcast_result["trx"]["operation_results"][0][1]
        lcc.set_step("Make voting of deactivating new account")
        operation = self.echo_ops.get_proposal_update_operation(
            echo=self.echo,
            fee_paying_account="1.2.6",
            proposal=proposal_id,
            active_approvals_to_add=["1.2.7", "1.2.8", "1.2.9", "1.2.10", "1.2.11"],
            active_approvals_to_remove=[],
            owner_approvals_to_remove=[],
            key_approvals_to_add=[],
            key_approvals_to_remove=[],
            signer=["5J6azg8iUcQEbxEaLAFrJbcdBjgKqewLF81A63NE4T2aeHCsKiE",
                    "5KaTLGtpGyCbod6hM2A9RETYcNn8CMR7e7LRKLi6DPDvnF1qxEm",
                    "5KJe2KY1yVnnBwXDtTDGfmnRGdUdR4HpLTUqpsG39h6VexYQwWH",
                    "5K3FJdakQUJvLon2dBxLNUwcHJbZxW6XBvc1AJKDCiGHPyXZadz",
                    "5JMgujU9Zmz85buhkPQyEMXLvK7FZ6giSLjRT25uf1tpV6uPULS",
                    "5JFDAh3DqESZEifvvB1dGgLu4Ar9WXMgx2YSwdBngR3mY9H2YGw"]
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("All committee member has voted")

        lcc.set_step("Waiting for maintenance and release of two blocks and check that new committee member were deactivated")
        import time
        time.sleep(25)

        current_active_committe_members = self.get_active_committee_members_ids()
        if new_member_id not in current_active_committe_members:
            lcc.log_info("new acitve committee member were deactivated")
        else:
            lcc.log_error("new acitve committee member has not been deactivated")
