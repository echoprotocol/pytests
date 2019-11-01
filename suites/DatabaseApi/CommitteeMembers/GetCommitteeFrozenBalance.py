# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, greater_than

from common.base_test import BaseTest
from fixtures.base_fixtures import get_random_integer
from project import INIT0_PK

SUITE = {
    "description": "Method 'get_committee_frozen_balance'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.prop("negative", "type")
@lcc.tags("api", "database_api", "database_api_committee_members", "get_committee_frozen_balance")
@lcc.suite("Check work of method 'get_committee_frozen_balance'", rank=1)
class GetCommitteeFrozenBalance(BaseTest):

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

    @lcc.test("Simple work of method 'get_committee_frozen_balance'")
    def method_main_check(self):
        amount_to_freeze = get_random_integer()

        lcc.set_step("Get first active committee member id and account id")
        response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
        active_committee_members = self.get_response(response_id)["result"]["active_committee_members"]
        committee_member_id = active_committee_members[0][0]
        committee_member_account_id = active_committee_members[0][1]
        lcc.log_info("Committee member id: '{}' and account id: '{}'".format(committee_member_id,
                                                                             committee_member_account_id))

        lcc.set_step("Get first active committee member balance")
        params = [committee_member_account_id, [self.echo_asset]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        current_balance = self.get_response(response_id)["result"][0]["amount"]
        lcc.log_info("{} account id balance: {}".format(committee_member_account_id, current_balance))

        lcc.set_step("Check first active committee member frozen balance")
        response_id = self.send_request(self.get_request("get_committee_frozen_balance", [committee_member_id]),
                                        self.__database_api_identifier)
        current_frozen_balance = self.get_response(response_id)["result"]["amount"]
        lcc.log_info("{} account id frozen balance: {}".format(committee_member_account_id, current_frozen_balance))

        lcc.set_step("Freeze part of first active committee member balance")
        operation = self.echo_ops.get_committee_frozen_balance_deposit_operation(
            echo=self.echo, committee_member=committee_member_id, committee_member_account=committee_member_account_id,
            amount=amount_to_freeze, asset_id="1.3.0", signer=INIT0_PK)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("Freeze {} assets".format(amount_to_freeze))

        lcc.set_step("Get required fee for 'committee_frozen_balance_deposit' operation")
        response_id = self.send_request(self.get_request("get_required_fees", [[operation[:-1]], self.echo_asset]),
                                        self.__database_api_identifier)
        fee_amount = self.get_response(response_id)["result"][0]["amount"]
        lcc.log_info("Required fee: '{}'".format(fee_amount))

        lcc.set_step("Check first active committee member balance after performing operation")
        params = [committee_member_account_id, [self.echo_asset]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        balance_after_freeze = self.get_response(response_id)["result"][0]["amount"]
        check_that("balance reduced ", int(current_balance) - int(balance_after_freeze),
                   equal_to(amount_to_freeze + fee_amount))

        lcc.set_step("Check first active committee member frozen balance")
        response_id = self.send_request(self.get_request("get_committee_frozen_balance", [committee_member_id]),
                                        self.__database_api_identifier)
        frozen_balance = self.get_response(response_id)["result"]["amount"]
        check_that("frozen balance", frozen_balance, equal_to(current_frozen_balance + amount_to_freeze))


@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_committee_members", "get_committee_frozen_balance")
@lcc.suite("Positive testing of method 'get_committee_frozen_balance'", rank=2)
class PositiveTesting(BaseTest):

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

    @lcc.test("Get committee frozen balance after several freeze")
    @lcc.depends_on(
        "DatabaseApi.CommitteeMembers.GetCommitteeFrozenBalance.GetCommitteeFrozenBalance.method_main_check")
    def perform_next_frozen_committee_frozen_balance_deposit_operation(self):
        amount_to_freeze = get_random_integer()

        lcc.set_step("Get first active committee members id and account id")
        response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
        active_committee_members = self.get_response(response_id)["result"]["active_committee_members"]
        committee_member_id = active_committee_members[0][0]
        committee_member_account_id = active_committee_members[0][1]
        lcc.log_info("Committee member id: '{}' and account id: '{}'".format(committee_member_id,
                                                                             committee_member_account_id))

        lcc.set_step("Get first active committee member frozen balance")
        response_id = self.send_request(self.get_request("get_committee_frozen_balance", [committee_member_id]),
                                        self.__database_api_identifier)
        frozen_balance = self.get_response(response_id)["result"]["amount"]
        lcc.log_info("{} account id frozen balance: {}".format(committee_member_account_id, frozen_balance))

        lcc.set_step("Freeze part of committee member balance")
        operation = self.echo_ops.get_committee_frozen_balance_deposit_operation(
            echo=self.echo, committee_member=committee_member_id, committee_member_account=committee_member_account_id,
            amount=amount_to_freeze, asset_id="1.3.0", signer=INIT0_PK)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("Freeze {} assets".format(amount_to_freeze))

        lcc.set_step("Check first active committee member frozen balance")
        response_id = self.send_request(self.get_request("get_committee_frozen_balance", [committee_member_id]),
                                        self.__database_api_identifier)
        current_frozen_balance = self.get_response(response_id)["result"]["amount"]
        check_that("frozen balance", frozen_balance + amount_to_freeze, equal_to(current_frozen_balance))


@lcc.prop("negative", "type")
@lcc.tags("api", "database_api", "database_api_committee_members", "get_committee_frozen_balance")
@lcc.suite("Negative testing of method 'get_committee_frozen_balance'", rank=3)
class NegativeTesting(BaseTest):

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

    @lcc.test("Freeze more than is available on the account")
    @lcc.depends_on(
        "DatabaseApi.CommitteeMembers.GetCommitteeFrozenBalance.GetCommitteeFrozenBalance.method_main_check")
    def check_freezing_amount_more_than_is_available_in_account_balance(self):
        error_message = "Assert Exception: d.get_balance(op.committee_member_account, op.amount.asset_id) >= " \
                        "op.amount: Not enough balance"

        lcc.set_step("Get committee members id and account_id")
        response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
        active_committee_members = self.get_response(response_id)["result"]["active_committee_members"]
        committee_member_id = active_committee_members[0][0]
        committee_member_account_id = active_committee_members[0][1]
        lcc.log_info("Committee member id: '{}' and account id: '{}'".format(committee_member_id,
                                                                             committee_member_account_id))

        lcc.set_step("Get first active committee member frozen balance")
        response_id = self.send_request(self.get_request("get_committee_frozen_balance", [committee_member_id]),
                                        self.__database_api_identifier)
        current_balance = self.get_response(response_id)["result"]["amount"]
        lcc.log_info("{} account id frozen balance: {}".format(committee_member_account_id, current_balance))

        lcc.set_step("Freeze more than is available")
        operation = self.echo_ops.get_committee_frozen_balance_deposit_operation(
            echo=self.echo, committee_member=committee_member_id, committee_member_account=committee_member_account_id,
            amount=int(current_balance) + 1, asset_id="1.3.0", signer=INIT0_PK)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        try:
            self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=True)
        except Exception as e:
            check_that("error message", e.__str__(), equal_to(error_message))
