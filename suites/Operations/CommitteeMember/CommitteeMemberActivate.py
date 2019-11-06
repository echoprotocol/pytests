# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest
from datetime import datetime, timedelta

SUITE = {
    "description": "Operation 'committee_member_activate'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("operations", "committee_member_operations", "committee_member_activate")
@lcc.suite("Check work of method 'committee_member_activate'", rank=1)
class CommitteeMemberActivate(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

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
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def get_expiration_time(self, seconds):
        pattern = "%Y-%m-%dT%H:%M:%S"
        now = self.get_datetime(global_datetime=True)
        expiration = datetime.strptime(now, pattern) + timedelta(seconds=seconds)
        return expiration.strftime(pattern)

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'committee_member_activate'")
    def method_main_check(self, get_random_valid_account_name, get_random_eth_address, get_random_btc_public_key):
        new_account = get_random_valid_account_name
        eth_account_address = get_random_eth_address
        btc_public_key = get_random_btc_public_key
        required_deposit = 100000000000

        lcc.set_step("Register new account in the ECHO network")
        new_account_id = self.get_account_id(new_account, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account_id))

        lcc.set_step("Create created account as new committee member in the ECHO network")
        broadcast_result = self.utils.perform_committee_member_create_operation(self, new_account_id,
                                                                                eth_account_address,
                                                                                btc_public_key,
                                                                                self.__database_api_identifier,
                                                                                deposit_amount=required_deposit)
        committee_member_id = broadcast_result["trx"]["operation_results"][0][1]
        lcc.log_info("New committee member id: {}".format(committee_member_id))

        lcc.set_step("Collect 'committee_member_activate_operation'")
        operation = \
            self.echo_ops.get_committee_member_activate_operation(echo=self.echo,
                                                                  committee_to_activate=committee_member_id,
                                                                  committee_member_activate=new_account_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        lcc.log_info("Collected successfully")

        lcc.set_step("Make proposal of new active committee member")
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

        lcc.set_step("Make voting for new active committee member")
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

        response_id = self.send_request(self.get_request("get_global_properties"),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        last_active_committee_member = response["result"]["active_committee_members"][-1][-1]
        check_that("new account in committee member", new_account_id, equal_to(last_active_committee_member))
