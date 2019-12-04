# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest
from project import INIT0_PK

SUITE = {
    "description": "Operation 'committee_frozen_balance_deposit'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "committee_member_operations", "committee_frozen_balance_deposit")
@lcc.suite("Check work of operation 'committee_frozen_balance_deposit'", rank=1)
class CommitteeFrozenBalanceDeposit(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.init0 = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info(
            "API identifiers are: database='{}'".format(self.__database_api_identifier))
        self.committee_members_info = self.get_active_committee_members_info(self.__database_api_identifier)
        self.init0 = self.committee_members_info[0]["account_id"]
        lcc.log_info("Echo  initial accounts: {}".format(
                     self.init0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of operation 'committee_frozen_balance_deposit'")
    def method_main_check(self, get_random_integer):
        amount_to_freeze = get_random_integer + 10

        lcc.set_step("Get first active committee member id and account id")
        committee_member_id = self.committee_members_info[0]["committee_id"]
        lcc.log_info("Committee member id: '{}' and account id: '{}'".format(committee_member_id,
                                                                             self.init0))
        lcc.set_step("Get active committee member balance")
        params = [self.init0, [self.echo_asset]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        current_balance = self.get_response(response_id)["result"][0]["amount"]
        lcc.log_info("{} account id balance: {}".format(self.init0, current_balance))

        lcc.set_step("Check active committee member frozen balance")
        response_id = self.send_request(self.get_request("get_committee_frozen_balance", [committee_member_id]),
                                        self.__database_api_identifier)
        current_frozen_balance = self.get_response(response_id)["result"]["amount"]
        lcc.log_info("{} account id frozen balance: {}".format(self.init0, current_frozen_balance))

        lcc.set_step("Freeze part of active committee member balance")
        operation = self.echo_ops.get_committee_frozen_balance_deposit_operation(
            echo=self.echo, committee_member=committee_member_id, committee_member_account=self.init0,
            amount=amount_to_freeze, asset_id=self.echo_asset, signer=INIT0_PK)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception("Balance is not freezed")
        lcc.log_info("Freeze {} assets".format(amount_to_freeze))

        lcc.set_step("Get required fee for 'committee_frozen_balance_deposit' operation")
        response_id = self.send_request(self.get_request("get_required_fees", [[operation[:-1]], self.echo_asset]),
                                        self.__database_api_identifier)
        fee_amount = self.get_response(response_id)["result"][0]["amount"]
        lcc.log_info("Required fee: '{}'".format(fee_amount))

        lcc.set_step("Check active committee member balance after performing operation")
        params = [self.init0, [self.echo_asset]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        balance_after_freeze = self.get_response(response_id)["result"][0]["amount"]
        check_that(
            "balance reduced",
            int(current_balance) - int(balance_after_freeze), equal_to(amount_to_freeze + fee_amount),
            quiet=True
        )

        lcc.set_step("Check active committee member frozen balance")
        response_id = self.send_request(self.get_request("get_committee_frozen_balance", [committee_member_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        frozen_balance = response["result"]["amount"]
        check_that(
            "frozen balance",
            frozen_balance, equal_to(current_frozen_balance + amount_to_freeze),
            quiet=True
        )
