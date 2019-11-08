# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, has_item

from common.base_test import BaseTest

SUITE = {
    "description": "Operation 'proposal_update'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "asset_transfer_operations", "proposal_update")
@lcc.suite("Check work of method 'proposal_update'", rank=1)
class ProposalUpdate(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None

    def get_expiration_time(self, seconds):
        pattern = "%Y-%m-%dT%H:%M:%S"
        now = self.get_datetime(global_datetime=True)
        expiration = datetime.strptime(now, pattern) + timedelta(seconds=seconds)
        return expiration.strftime(pattern)

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc1 = self.get_account_id(self.accounts[1], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'proposal_update'")
    def method_main_check(self, get_random_integer_up_to_ten):
        transfer_amount = get_random_integer_up_to_ten

        response_id = self.send_request(self.get_request("get_account_balances", ["1.2.6", [self.echo_asset]]),
                                        self.__database_api_identifier)
        account_balance = self.get_response(response_id)["result"][0]["amount"]
        lcc.log_info("{}".format(account_balance))
        lcc.set_step("Collect transfer operation")
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo, from_account_id="1.2.6",
                                                                  amount=transfer_amount, to_account_id="1.2.7")
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        lcc.log_info("Transfer operation collected")

        lcc.set_step("Make proposal of transfer operation")
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
        lcc.log_info("Propsal created, proposal id: '{}'".format(proposal_id))
        lcc.set_step("Make voting for transfer operation")
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

        lcc.set_step("Waiting for maintenance and release of two blocks and check that new committee member were activated")
        import time
        time.sleep(25)
        response_id = self.send_request(self.get_request("get_account_balances", ["1.2.6", [self.echo_asset]]),
                                        self.__database_api_identifier)
        current_account_balance = self.get_response(response_id)["result"][0]["amount"]
        lcc.log_info("Account: {}, have balance: {}".format("1.2.7", current_account_balance))
        check_that("transferred amount", int(current_account_balance) - int(account_balance), equal_to(transfer_amount))
