# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, require_that, is_true
from project import INIT0_PK, INIT1_PK

from common.base_test import BaseTest

SUITE = {
    "description": "Operation 'proposal_update'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "proposal_operations", "proposal_update")
@lcc.suite("Check work of method 'proposal_update'", rank=1)
class ProposalUpdate(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'proposal_update'")
    def method_main_check(self, get_random_integer_up_to_ten):
        transfer_amount = get_random_integer_up_to_ten

        response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
        active_committee_members = self.get_response(response_id)["result"]["active_committee_members"]
        proposal_creator_id = active_committee_members[0][1]
        proposal_approval_account_id = active_committee_members[1][1]

        lcc.set_step("Collect transfer operation")
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo, from_account_id=proposal_approval_account_id,
                                                                  amount=transfer_amount, to_account_id=proposal_creator_id)
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        lcc.log_info("Transfer operation collected")

        lcc.set_step("Make proposal of transfer operation")
        operation = self.echo_ops.get_proposal_create_operation(
            echo=self.echo,
            fee_paying_account=proposal_creator_id,
            proposed_ops=collected_operation,
            expiration_time=self.get_expiration_time(60),
            review_period_seconds=10,
            signer=INIT0_PK
        )
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=operation)
        require_that(
            "broadcast transaction complete successfully",
            self.is_operation_completed(broadcast_result, 1), is_true(),
            quiet=True
        )
        proposal_id = broadcast_result["trx"]["operation_results"][0][1]
        lcc.log_info("Propsal created, proposal id: '{}'".format(proposal_id))

        lcc.set_step("Make voting for transfer operation")
        operation = self.echo_ops.get_proposal_update_operation(
            echo=self.echo,
            fee_paying_account=proposal_approval_account_id,
            proposal=proposal_id,
            active_approvals_to_add=[proposal_approval_account_id],
            active_approvals_to_remove=[],
            key_approvals_to_add=[],
            key_approvals_to_remove=[],
            signer=[INIT1_PK]
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        require_that(
            "broadcast transaction complete successfully",
            self.is_operation_completed(broadcast_result, 0), is_true(),
            quiet=True
        )
        lcc.log_info("All committee member has voted")

        lcc.set_step("Check that all required committee member has voted")
        response_id = self.send_request(self.get_request("get_proposed_transactions", [proposal_approval_account_id]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][0]
        check_that("available_active_approvals", result["available_active_approvals"],
                   equal_to([proposal_approval_account_id]), quiet=True)
