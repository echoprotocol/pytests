# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest
from project import INIT0_PK
import time
SUITE = {
    "description": "Operation 'withdraw_committee_member_balance'"
}


@lcc.prop("main", "type")
@lcc.tags("scenarios", "withdraw_committee_member_balance")
@lcc.suite("Check work of scenario 'withdraw_committee_member_balance'", rank=1)
class WithdrawCommitteeMemberBalance(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}'".format(self.__database_api_identifier))

        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("The scenario describes withdraw balance after ")
    def method_main_check(self, get_random_integer):
        minimal_frozen_balance = 100000000001
        amount_to_freeze = 100000000100

        lcc.set_step("Get first active committee member id and account id")
        response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
        active_committee_members = self.get_response(response_id)["result"]["active_committee_members"][0]
        committee_member_id = active_committee_members[0]
        committee_member_account_id = active_committee_members[1]
        lcc.log_info("Committee member id: '{}' and account id: '{}'".format(committee_member_id,
                                                                             committee_member_account_id))
        lcc.set_step("Check active committee member frozen balance")
        response_id = self.send_request(self.get_request("get_committee_frozen_balance", [committee_member_id]),
                                        self.__database_api_identifier)
        current_frozen_balance = self.get_response(response_id)["result"]["amount"]
        lcc.log_info("{} account, has frozen balance amount: {}".format(committee_member_account_id, current_frozen_balance))

        if int(current_frozen_balance) <= minimal_frozen_balance:
            lcc.log_info("Not enought asset to withdraw frozen balance")
            lcc.set_step("Add deposit to committee member: '{}' account". format(committee_member_account_id))
            if int(current_frozen_balance) >= 100000000000:
                amount_to_freeze = 100
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
            amount=int(current_frozen_balance) - minimal_frozen_balance, asset_id=self.echo_asset, signer=INIT0_PK)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.produce_block(self.__database_api_identifier)
        try:
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        except Exception as e:
            # todo: change error message check after changing the error message
            lcc.log_info("{}".format(e))
        time.sleep(50)
        try:
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        except Exception as e:
            lcc.log_info("{}".format(e))
        if not self.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception("Balance is not withdrawn")
        lcc.log_info("Committee member balance have been withdrawn")

        lcc.set_step("Check that frozen balance have been withdrawn")
        response_id = self.send_request(self.get_request("get_committee_frozen_balance", [committee_member_id]),
                                        self.__database_api_identifier)
        frozen_balance_after_withdraw = self.get_response(response_id)["result"]["amount"]
        check_that("frozen balance", int(frozen_balance_after_withdraw), equal_to(minimal_frozen_balance))
