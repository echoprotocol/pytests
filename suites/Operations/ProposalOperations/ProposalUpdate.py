# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from project import INIT0_PK, INIT1_PK

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, is_true, require_that

SUITE = {
    "description": "Operation 'proposal_update'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "proposal_operations", "proposal_update")
@lcc.suite("Check work of operation 'proposal_update'", rank=1)
class ProposalUpdate(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.init0 = None
        self.init1 = None

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

        self.committee_members_info = self.get_active_committee_members_info(self.__database_api_identifier)
        self.init0 = self.committee_members_info[0]["account_id"]
        self.init1 = self.committee_members_info[1]["account_id"]
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.init0, self.init1))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of operation 'proposal_update'")
    def method_main_check(self, get_random_integer_up_to_ten):
        transfer_amount = get_random_integer_up_to_ten

        lcc.set_step("Collect transfer operation")
        transfer_operation = self.echo_ops.get_transfer_operation(
            echo=self.echo, from_account_id=self.init1, amount=transfer_amount, to_account_id=self.init0
        )
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        lcc.log_info("Transfer operation collected")

        lcc.set_step("Make proposal of transfer operation")
        operation = self.echo_ops.get_proposal_create_operation(
            echo=self.echo,
            fee_paying_account=self.init0,
            proposed_ops=collected_operation,
            expiration_time=self.get_expiration_time(60),
            review_period_seconds=10,
            signer=INIT0_PK
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        require_that(
            "broadcast transaction complete successfully",
            self.is_operation_completed(broadcast_result, 1),
            is_true(),
            quiet=True
        )
        proposal_id = broadcast_result["trx"]["operation_results"][0][1]
        lcc.log_info("Propsal created, proposal id: '{}'".format(proposal_id))

        lcc.set_step("Make voting for transfer operation")
        operation = self.echo_ops.get_proposal_update_operation(
            echo=self.echo,
            fee_paying_account=self.init1,
            proposal=proposal_id,
            active_approvals_to_add=[self.init1],
            active_approvals_to_remove=[],
            key_approvals_to_add=[],
            key_approvals_to_remove=[],
            signer=[INIT1_PK]
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        require_that(
            "broadcast transaction complete successfully",
            self.is_operation_completed(broadcast_result, 0),
            is_true(),
            quiet=True
        )
        lcc.log_info("All committee member has voted")

        lcc.set_step("Check that all required committee member has voted")
        response_id = self.send_request(
            self.get_request("get_proposed_transactions", [self.init1]), self.__database_api_identifier
        )
        result = self.get_response(response_id)["result"][0]
        check_that(
            "available_active_approvals", result["available_active_approvals"], equal_to([self.init1]), quiet=True
        )
