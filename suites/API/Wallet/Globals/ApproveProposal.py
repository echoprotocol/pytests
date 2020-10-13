# -*- coding: utf-8 -*-
import time

from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import INIT0_PK, INIT1_PK, INIT2_PK, INIT3_PK, INIT4_PK, INIT5_PK, REQUIRED_DEPOSIT_AMOUNT

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, not_equal_to, require_that

SUITE = {
    "description": "Method 'approve_proposal'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_globals", "wallet_approve_proposal")
@lcc.suite("Check work of method 'approve_proposal'", rank=1)
class ApproveProposal(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.init0 = None
        self.init1 = None
        self.init2 = None
        self.init3 = None
        self.init4 = None

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
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))
        lcc.set_step("Get initial account ids")
        self.init0 = self.get_account_id('init0', self.__database_api_identifier, self.__registration_api_identifier)
        self.init1 = self.get_account_id('init1', self.__database_api_identifier, self.__registration_api_identifier)
        self.init2 = self.get_account_id('init2', self.__database_api_identifier, self.__registration_api_identifier)
        self.init3 = self.get_account_id('init3', self.__database_api_identifier, self.__registration_api_identifier)
        self.init4 = self.get_account_id('init4', self.__database_api_identifier, self.__registration_api_identifier)
        self.init5 = self.get_account_id('init5', self.__database_api_identifier, self.__registration_api_identifier)
        lcc.log_info(
            "Initial account ids: '{}', '{}', '{}', '{}', '{}', '{}'".format(
                self.init0, self.init1, self.init2, self.init3, self.init4, self.init5
            )
        )

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    # @lcc.disabled()
    @lcc.test("Simple work of method 'wallet_approve_proposal'")
    def method_main_check(self, get_random_valid_account_name, get_random_eth_address, get_random_btc_public_key):
        self.unlock_wallet()
        lcc.set_step("Import key")
        self.send_wallet_request("import_key", ['init0', INIT0_PK], log_response=False)
        self.send_wallet_request("import_key", ['init1', INIT1_PK], log_response=False)
        self.send_wallet_request("import_key", ['init2', INIT2_PK], log_response=False)
        self.send_wallet_request("import_key", ['init3', INIT3_PK], log_response=False)
        self.send_wallet_request("import_key", ['init4', INIT4_PK], log_response=False)
        self.send_wallet_request("import_key", ['init5', INIT5_PK], log_response=False)
        lcc.log_info("Key imported")

        new_account = get_random_valid_account_name
        eth_account_address = get_random_eth_address
        btc_public_key = get_random_btc_public_key

        lcc.set_step("Register new account in the ECHO network")
        new_account_id = self.get_account_id(
            new_account, self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account_id))

        lcc.set_step("Create created account as new committee member in the ECHO network")
        broadcast_result = self.utils.perform_committee_member_create_operation(
            self,
            new_account_id,
            eth_account_address,
            btc_public_key,
            self.__database_api_identifier,
            deposit_amount=REQUIRED_DEPOSIT_AMOUNT
        )
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
            fee_paying_account=self.init0,
            proposed_ops=collected_operation,
            expiration_time=self.get_expiration_time(15),
            review_period_seconds=10,
            signer=INIT0_PK
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception("Operation 'proposal_created' failed while broadcast")
        proposal_id = broadcast_result["trx"]["operation_results"][0][1]

        proposal_params = {
            "active_approvals_to_add": [],
            "active_approvals_to_remove": [],
            "key_approvals_to_add": [],
            "key_approvals_to_remove": []
        }
        proposal_params['active_approvals_to_add'].extend([self.init0, self.init1, self.init2, self.init3, self.init4])
        self.send_wallet_request(
            "approve_proposal", [self.init0, proposal_id, proposal_params, True], log_response=False
        )

        lcc.set_step(
            "Waiting for maintenance and release of two blocks and check that new committee member were activated"
        )
        time.sleep(15)
        self.produce_block(self.__database_api_identifier)
        response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
        last_active_committee_member = self.get_response(response_id)["result"]["active_committee_members"][-1][1]
        check_that(
            "new account in committee member", new_account_id, equal_to(last_active_committee_member), quiet=False
        )

        lcc.set_step("Deactivate created account")
        self.committee_members_info = self.get_active_committee_members_info(self.__database_api_identifier)

        operation = self.echo_ops.get_committee_member_deactivate_operation(
            echo=self.echo,
            committee_member_account=self.init0,
            committee_to_deactivate=self.committee_members_info[-1]["committee_id"],
            signer=INIT0_PK
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        lcc.log_info("Deactivate operation collected successfully")
        lcc.set_step("Make proposal of deactivating new account")
        operation = self.echo_ops.get_proposal_create_operation(
            echo=self.echo,
            fee_paying_account=self.init0,
            proposed_ops=collected_operation,
            expiration_time=self.get_expiration_time(30),
            review_period_seconds=10,
            signer=INIT0_PK
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=operation)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception("Operation 'proposal_created' failed while broadcast")
        proposal_id = broadcast_result["trx"]["operation_results"][0][1]
        self
        lcc.set_step("Make voting of deactivating new account")
        proposal_params = {
            "active_approvals_to_add": [],
            "active_approvals_to_remove": [],
            "key_approvals_to_add": [],
            "key_approvals_to_remove": []
        }
        proposal_params['active_approvals_to_add'].extend([self.init0, self.init1, self.init2, self.init3, self.init4])
        self.send_wallet_request(
            "approve_proposal", [self.init0, proposal_id, proposal_params, True], log_response=False
        )

        lcc.set_step(
            "Waiting for maintenance and release of two blocks and check that new committee member were deactivated"
        )
        self.produce_block(self.__database_api_identifier)
        time.sleep(30)
        self.produce_block(self.__database_api_identifier)
        response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
        last_active_committee_member = self.get_response(response_id)["result"]["active_committee_members"][-1][1]
        require_that(
            "acitve committee member", new_account_id, not_equal_to(last_active_committee_member), quiet=False
        )
