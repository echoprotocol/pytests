# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, check_that_in, is_list, is_integer, check_that, \
    equal_to, has_length

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_block_rewards'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_blocks_transactions", "get_block_rewards")
@lcc.suite("Check work of method 'get_block_rewards'", rank=1)
class GetBlockRewards(BaseTest):
    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'get_block_rewards'")
    def method_main_check(self):
        lcc.set_step("Get the full first block in the chain")
        block_num = 1
        response_id = self.send_request(self.get_request("get_block_rewards", [block_num]), self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_block_rewards' with block_num='{}' parameter".format(block_num))

        lcc.set_step("Check simple work of method 'get_block_rewards'")
        result = response["result"]
        require_that(
            "'the first full block'",
            result, has_length(3)
        )
        check_that_in(
            result,
            "emission", is_integer(),
            "fees", is_integer(),
            "rewards", is_list()
        )


@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_blocks_transactions", "get_block_rewards")
@lcc.suite("Positive testing of method 'get_block_rewards'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.echo_acc0 = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__network_broadcast_identifier = self.get_identifier("network_broadcast")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', network_broadcast='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier,
                self.__network_broadcast_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc1 = self.get_account_id(self.accounts[1], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Check info about several blocks")
    @lcc.depends_on("DatabaseApi.BlocksTransactions.GetBlockRewards.GetBlockRewards.method_main_check")
    def work_of_method_with_several_blocks(self, get_random_integer):
        subscription_callback_id = get_random_integer
        lcc.set_step("Sign transfer operation")
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=self.echo_acc0,
                                                                  to_account_id=self.echo_acc1, amount=1)
        params = [[transfer_operation], "1.3.0"]
        response_id = self.send_request(self.get_request("get_required_fees", params), self.__database_api_identifier)
        fee = self.get_response(response_id)["result"][0]["amount"]
        lcc.log_info("Required fee for transfer operation: {}".format(fee))
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        signed_trx = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                             no_broadcast=True)
        lcc.log_info("Transfer operation signed")

        lcc.set_step("Broadcast transfer operation with callback")
        params = [subscription_callback_id, signed_trx]
        response_id = self.send_request(self.get_request("broadcast_transaction_with_callback", params),
                                        self.__network_broadcast_identifier)
        self.get_response(response_id)
        notice = self.get_notice(subscription_callback_id, log_response=False)
        block_num = notice["block_num"]
        lcc.log_info("Get {} block with transfer operation from returned notice".format(block_num))
        self.produce_block(self.__database_api_identifier)
        lcc.set_step("Get rewards from block with transfer operation")
        response_id = self.send_request(self.get_request("get_block_rewards", [block_num]),
                                        self.__database_api_identifier)
        rewards = self.get_response(response_id)["result"]["rewards"]
        lcc.log_info("Rewards from block taken successfully")
        lcc.set_step("Get block producers")
        response_id = self.send_request(self.get_request("get_block", [block_num]),
                                        self.__database_api_identifier)
        cert = self.get_response(response_id)["result"]["cert"]
        lcc.log_info("Block producers taken successfully")
        beneficiarys = [beneficiary[0] for beneficiary in rewards]
        lcc.set_step("Check that all block producers get rewards, and fee collected correctly")
        for producers in cert:
            if "1.2." + str(producers["_producer"]) not in beneficiarys:
                lcc.log_error(
                    "{} not in accounts that get rewards for broadcasted operation".format(producers["_producer"]))
        lcc.log_info("All accounts get rewards for block producing")
        rewards_amount = 0
        for i in rewards:
            rewards_amount += i[1]
        check_that("collected rewards amount", fee, equal_to(rewards_amount), quiet=True)
