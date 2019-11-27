# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest
from project import INIT0_PK

SUITE = {
    "description": "Operation 'committee_frozen_balance_withdraw'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "committee_member_operations", "committee_frozen_balance_withdraw")
@lcc.suite("Check work of operation 'committee_frozen_balance_withdraw'", rank=1)
class CommitteeFrozenBalanceWithdraw(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info(
            "API identifiers are: database='{}'".format(self.__database_api_identifier))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'committee_frozen_balance_withdraw'")
    def method_main_check(self, get_random_integer):
        residual_frozen_balance = 10
        amount_to_freeze = get_random_integer + 10

        lcc.set_step("Get first active committee member id and account id")
        response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
        active_committee_members = self.get_response(response_id)["result"]["active_committee_members"]
        committee_member_id = active_committee_members[0][0]
        committee_member_account_id = active_committee_members[0][1]
        lcc.log_info("Committee member id: '{}' and account id: '{}'".format(committee_member_id,
                                                                             committee_member_account_id))
        lcc.set_step("Check active committee member frozen balance")
        response_id = self.send_request(self.get_request("get_committee_frozen_balance", [committee_member_id]),
                                        self.__database_api_identifier)
        current_frozen_balance = self.get_response(response_id)["result"]["amount"]
        lcc.log_info("{} account, has frozen balance amount: {}".format(committee_member_account_id, current_frozen_balance))

        if current_frozen_balance <= residual_frozen_balance:
            lcc.log_info("Not enought asset to withdraw frozen balance")
            lcc.set_step("Freeze asset of committee_member: '{}' account". format(committee_member_account_id))
            operation = self.echo_ops.get_committee_frozen_balance_deposit_operation(
                echo=self.echo, committee_member=committee_member_id, committee_member_account=committee_member_account_id,
                amount=amount_to_freeze, asset_id=self.echo_asset, signer=INIT0_PK)
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
            if not self.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Balance is not freezed")
            response_id = self.send_request(self.get_request("get_committee_frozen_balance", [committee_member_id]),
                                            self.__database_api_identifier)
            current_frozen_balance = self.get_response(response_id)["result"]["amount"]
            lcc.log_info("Account {} frozen balance updated, frozen balance amount: {}".format(
                         committee_member_account_id, current_frozen_balance))

        lcc.set_step("Withdraw balance of active committee member")
        operation = self.echo_ops.get_committee_frozen_balance_withdraw_operation(
            echo=self.echo, committee_member_account=committee_member_account_id,
            amount=current_frozen_balance - residual_frozen_balance, asset_id=self.echo_asset, signer=INIT0_PK)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception("Balance is not withdrawn")
        lcc.log_info("Committee member balance have been withdrawn")

        lcc.set_step("Check that frozen balance have been withdrawn")
        response_id = self.send_request(self.get_request("get_committee_frozen_balance", [committee_member_id]),
                                        self.__database_api_identifier)
        frozen_balance_after_withdraw = self.get_response(response_id)["result"]["amount"]
        check_that("frozen balance", frozen_balance_after_withdraw, equal_to(residual_frozen_balance))
