# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import has_item, is_true, require_that

SUITE = {
    "description": "Operation 'proposal_create'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "proposal_operations", "proposal_create")
@lcc.suite("Check work of method 'proposal_create'", rank=1)
class ProposalCreate(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None

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
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        self.echo_acc1 = self.get_account_id(
            self.accounts[1], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'proposal_create'")
    def method_main_check(self):
        transfer_operation = self.echo_ops.get_transfer_operation(
            echo=self.echo, from_account_id=self.echo_acc1, to_account_id=self.echo_acc0
        )
        lcc.set_step("Collect transfer operation")
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)

        lcc.set_step("Make proposal of transfer operation")
        operation = self.echo_ops.get_proposal_create_operation(
            echo=self.echo,
            fee_paying_account=self.echo_acc0,
            proposed_ops=collected_operation,
            expiration_time=self.get_expiration_time(15),
            review_period_seconds=10
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

        lcc.set_step("Get proposed transactions for '{}' account".format(self.echo_acc1))
        response_id = self.send_request(
            self.get_request("get_proposed_transactions", [self.echo_acc1]), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info("Call 'get_proposed_transactions' with id='{}' parameter".format(self.echo_acc1))

        proposed_transactions_ids = [propose_transaction["id"] for propose_transaction in response["result"]]
        lcc.set_step("Check 'get_proposed_transactions' method result")
        require_that("proposed transactions ids", proposed_transactions_ids, has_item(proposal_id), quiet=True)
