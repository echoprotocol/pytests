# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc

from common.base_test import BaseTest

from project import NATHAN_PK

SUITE = {
    "description": "Testing distribution of reward for block with fallbacks"
}


@lcc.prop("main", "type")
@lcc.tags("reward_for_block_with_fallback")
# todo: back this tag @lcc.tags("scenarios")
@lcc.suite("Check scenario 'Reward for block with fallbacks'")
class RewardForBlockWithFallbacks(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.accounts = ["1.2.6", "1.2.7", "1.2.8", "1.2.11", "1.2.12"]

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("The scenario describes the mechanism of distribution of reward for block with fallbacks")
    def reward_for_block_with_fallbacks(self):
        total_verifiers_balance, reward, total_verifiers_reward, delegate_reward, account_reward = 0, 0, 0, 0, 0
        verifiers_balances, rewards = [], []
        verifiers_rewards, producer_rewards = {}, {}
        verifier, producer = False, False

        lcc.set_step("Get accounts 'delegate_share'")
        response_id = self.send_request(self.get_request("get_accounts", [self.accounts]),
                                        self.__database_api_identifier, debug_mode=True)
        delegate_share = self.get_response(response_id, log_response=True)

        lcc.set_step("Get accounts balances")
        self.utils.set_timeout_until_num_blocks_released(self, self.__database_api_identifier)
        for account in self.accounts:
            response_id = self.send_request(self.get_request("get_account_balances", [account, [self.echo_asset]]),
                                            self.__database_api_identifier, debug_mode=True)
            balance_before_call = self.get_response(response_id, log_response=True)

        lcc.set_step("Transfer from nathan to 1.2.6 account")
        operation = self.echo_ops.get_transfer_operation(echo=self.echo, from_account_id="1.2.12",
                                                         to_account_id="1.2.6", amount=10,
                                                         amount_asset_id="1.3.0", signer=NATHAN_PK)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=True)
        block_number = broadcast_result["block_num"]

        lcc.set_step("Get block with operation")
        response_id = self.send_request(self.get_request("get_block", [block_number]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id, log_response=True)["result"]

        lcc.set_step("Get next block after block with operation")
        next_block_num = block_number + 1
        self.utils.set_timeout_until_num_blocks_released(self, self.__database_api_identifier)
        response_id = self.send_request(self.get_request("get_block", [next_block_num]),
                                        self.__database_api_identifier)
        prev_signatures = self.get_response(response_id, log_response=True)

        lcc.set_step("Get accounts balances")
        for account in self.accounts:
            response_id = self.send_request(self.get_request("get_account_balances", [account, [self.echo_asset]]),
                                            self.__database_api_identifier, debug_mode=True)
            balance_before_call = self.get_response(response_id, log_response=True)

