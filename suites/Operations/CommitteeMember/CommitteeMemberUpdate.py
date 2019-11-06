# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, not_equal_to

from fixtures.base_fixtures import get_random_eth_address, get_random_btc_public_key, get_random_url
from common.base_test import BaseTest

SUITE = {
    "description": "Operation 'committee_member_update'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("operations", "vesting_balances_operations", "committee_member_update")
@lcc.suite("Check work of method 'committee_member_update'", rank=1)
class CommitteeMemberUpdate(BaseTest):

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
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'committee_member_update'")
    def method_main_check(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name
        eth_account_address = get_random_eth_address()
        btc_public_key = get_random_btc_public_key()
        new_eth_account_address = get_random_eth_address()
        new_btc_public_key = get_random_btc_public_key()
        new_url = get_random_url()

        lcc.set_step("Register new account in the network")
        new_account_id = self.get_account_id(new_account, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account_id))

        response_id = self.send_request(self.get_request("get_committee_member_by_account", [new_account_id]),
                                        self.__database_api_identifier)
        committee_member = self.get_response(response_id)["result"]
        check_that("'get_committee_member_by_account' method result", committee_member, equal_to(None))

        lcc.set_step("Perform 'committee_member_create' operation")
        operation = self.echo_ops.get_committee_member_create_operation(echo=self.echo,
                                                                        committee_member_account=new_account_id,
                                                                        eth_address=eth_account_address,
                                                                        btc_public_key=btc_public_key,
                                                                        url="",
                                                                        deposit_amount=0)
        self.utils.add_balance_for_operations(self, new_account_id, operation, self.__database_api_identifier)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("'committee_member_create' operation broadcastes successfully")

        lcc.set_step("Perform 'committee_member_update' operation")
        response_id = self.send_request(self.get_request("get_committee_member_by_account", [new_account_id]),
                                        self.__database_api_identifier)
        committee_member = self.get_response(response_id)["result"]
        committee_member_id = committee_member["id"]
        committee_member_account = committee_member["committee_member_account"]
        old_url = committee_member["url"]
        old_eth_address = committee_member["eth_address"]
        old_btc_public_key = committee_member["btc_public_key"]

        lcc.set_step("Perform 'committee_member_update' operation")
        operation = self.echo_ops.get_committee_member_update_operation(echo=self.echo,
                                                                        committee_member=committee_member_id,
                                                                        committee_member_account=committee_member_account,
                                                                        new_eth_address=new_eth_account_address,
                                                                        new_btc_public_key=new_btc_public_key,
                                                                        new_url=new_url)
        self.utils.add_balance_for_operations(self, new_account_id, operation, self.__database_api_identifier)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("'committee_member_update' operation broadcasted successfully")

        lcc.set_step("Check that committee member fields have been updated")
        response_id = self.send_request(self.get_request("get_committee_member_by_account", [new_account_id]),
                                        self.__database_api_identifier)
        committee_member = self.get_response(response_id)["result"]
        check_that("id", committee_member["id"], equal_to(committee_member_id))
        check_that("committee_member_account", committee_member["committee_member_account"],
                   equal_to(committee_member_account))
        check_that("url", committee_member["url"], not_equal_to(old_url))
        check_that("eth_address", committee_member["eth_address"], not_equal_to(old_eth_address))
        check_that("btc_public_key", committee_member["btc_public_key"], not_equal_to(old_btc_public_key))
