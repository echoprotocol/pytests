# -*- coding: utf-8 -*-
import time

from common.base_test import BaseTest
from common.wallet_base_test import WalletBaseTest
from project import INIT0_PK, INIT1_PK, INIT2_PK, INIT3_PK, INIT4_PK, WALLET_PASSWORD

import lemoncheesecake.api as lcc

SUITE = {
    "description": "Method 'propose_fee_change'"
}


@lcc.prop("main", "type")
@lcc.tags("api", "wallet_api", "wallet_accounts", "wallet_propose_fee_change")
@lcc.suite("Check work of method 'propose_fee_change'", rank=1)
class ProposeFeeChange(WalletBaseTest, BaseTest):

    def __init__(self):
        WalletBaseTest.__init__(self)
        BaseTest.__init__(self)
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    # @lcc.disabled()
    @lcc.test("Simple work of method 'wallet_propose_fee_change'")
    def method_main_check(self):
        lcc.set_step("Unlock wallet")
        response = self.send_wallet_request("is_new", [], log_response=False)
        if response['result']:
            self.send_wallet_request("set_password", [WALLET_PASSWORD], log_response=False)
        response = self.send_wallet_request("is_locked", [], log_response=False)
        if response['result']:
            self.send_wallet_request("unlock", [WALLET_PASSWORD], log_response=False)
        lcc.log_info("Wallet unlocked")
        lcc.set_step("Import key")
        self.send_wallet_request("import_key", ['init4', INIT4_PK], log_response=False)
        self.send_wallet_request("import_key", ['init0', INIT0_PK], log_response=False)
        lcc.log_info("Key imported")

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

        params_to_update = {
            "scale": 1000
        }

        lcc.set_step('Check propose_fee_change method')
        expiration_time = self.get_expiration_time(seconds=30)
        proposal = self.send_wallet_request(
            "propose_fee_change", [self.init4, expiration_time, params_to_update], log_response=False
        )
        lcc.log_info("{}".format(proposal))
        lcc.log_info("Search for a block with fee change proposal")
        block = int(proposal['result']['ref_block_num'])
        proposal_id = self.get_proposal_id_from_next_blocks(block)
        lcc.log_info("Block found, proposal id in block: '{}'".format(proposal_id))

        lcc.set_step("Update proposal with committee deactivate")
        operation = self.echo_ops.get_proposal_update_operation(
            echo=self.echo,
            fee_paying_account=self.init0,
            proposal=proposal_id,
            active_approvals_to_add=[self.init0, self.init1, self.init2, self.init3, self.init4],
            active_approvals_to_remove=[],
            key_approvals_to_add=[],
            key_approvals_to_remove=[],
            signer=[INIT0_PK, INIT1_PK, INIT2_PK, INIT3_PK, INIT4_PK]
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception("Operation 'proposal_update' failed while broadcast")
        lcc.log_info("All committee member has voted")

        lcc.set_step("Set timer for proposal expiration")
        time.sleep(15)
        self.produce_block(self.__database_api_identifier)
        lcc.log_info("Voting finished.")

        lcc.set_step("Set timer for sidechain")
        time.sleep(5)
        self.produce_block(self.__database_api_identifier)
        lcc.log_info("Timer expired")

        get_global_properties_result = self.send_wallet_request(
            "get_global_properties", [], log_response=False
        )['result']
        lcc.log_info("{}".format(get_global_properties_result))
