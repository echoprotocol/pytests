# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest
from fixtures.base_fixtures import get_random_valid_account_name

SUITE = {
    "description": "Comparison of objects balance accounts when transfer in subscription"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("balance_obj_in_subscription")
@lcc.suite("Check scenario 'Balance objects in subscription'")
class BalanceObjectsInSubscribe(BaseTest):

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

    def teardown_suite(self):

        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "scenario")
    @lcc.test("The scenario comparing objects balance accounts when transfer assets")
    def compare_balance_objects_when_transfer(self, get_random_integer):
        subscription_callback_id, transfer_amount = get_random_integer, get_random_integer
        tracked_accounts, accounts_balance_after_transfer = [], []
        balance_object_count, got_account_balance_notices = 0, 0
        notices = {}
        tracked_accounts_names = [get_random_valid_account_name(), get_random_valid_account_name()]

        lcc.set_step("Create and get two new accounts")
        for tracked_account_name in tracked_accounts_names:
            new_account = self.get_account_id(tracked_account_name, self.__database_api_identifier,
                                              self.__registration_api_identifier)
            lcc.log_info("New Echo account created, account_id='{}'".format(new_account))
            tracked_accounts.append(new_account)

        lcc.set_step("Get transfer operation fee")
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=tracked_accounts[0],
                                                                  to_account_id=tracked_accounts[1],
                                                                  amount=transfer_amount)
        fee = self.get_required_fee(transfer_operation, self.__database_api_identifier)[0]["amount"]
        lcc.log_info("Required fee for transfer transaction: '{}'".format(fee))

        lcc.set_step("Set subscribe callback")
        params = [subscription_callback_id, False]
        response_id = self.send_request(self.get_request("set_subscribe_callback", params),
                                        self.__database_api_identifier)
        if self.get_response(response_id)["result"] is not None:
            raise Exception("Subscription failed")
        lcc.log_info("Global subscription turned on")

        lcc.set_step("Get accounts to subscribe to them")
        params = [[tracked_accounts[0], tracked_accounts[1]], True]
        response_id = self.send_request(self.get_request("get_full_accounts", params),
                                        self.__database_api_identifier)
        if not self.get_response(response_id)["result"]:
            raise Exception("Subscription failed")
        lcc.log_info("Accounts info received. Subscription completed")

        lcc.set_step("Transfer assets from account to account")
        self.utils.perform_transfer_operations(self, tracked_accounts[0], tracked_accounts[1],
                                               self.__database_api_identifier,
                                               transfer_amount=transfer_amount)
        lcc.log_info(
            "Transfer '{}' assets from '{}' to '{}'. Fee for operation: '{}'".format((transfer_amount - fee),
                                                                                     tracked_accounts[0],
                                                                                     tracked_accounts[1], fee))

        lcc.set_step("Get notice about accounts updates")
        while len(tracked_accounts) > got_account_balance_notices:
            current_notices = self.get_notice(subscription_callback_id, notices_list=True)
            for notice in current_notices:
                if "id" in notice and self.validator.is_account_balance_id(notice["id"]):
                    notices.update({notice["id"]: notice})
                    got_account_balance_notices += 1

        notices_list = [notices[key] for key in notices]
        for tracked_account in tracked_accounts:
            for notice in notices_list:
                if self.validator.is_account_balance_id(notice["id"]):
                    if notice["owner"] == tracked_account:
                        accounts_balance_after_transfer.append(notice["balance"])
                        balance_object_count += 1
        if balance_object_count != len(tracked_accounts):
            raise Exception("Wrong notice received")
        lcc.log_info("Get notice with '{}' balance_objects owned by tracked accounts".format(balance_object_count))

        lcc.set_step("Check that the notice came the updated accounts balances")
        accounts_balance_before_transfer = [transfer_amount + fee, 0]
        for i, tracked_account in enumerate(tracked_accounts):
            if i != 0:
                fee = 0
                transfer_amount = - transfer_amount
            check_that(
                "balance of account '{}'".format(tracked_accounts[i]),
                int(accounts_balance_after_transfer[i]),
                equal_to(int(accounts_balance_before_transfer[i]) - transfer_amount - fee)
            )
