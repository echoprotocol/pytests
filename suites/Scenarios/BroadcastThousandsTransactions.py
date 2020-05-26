# -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, greater_than_or_equal_to, is_true

from common.base_test import BaseTest

SUITE = {
    "description": "Scenario 'Collect and broadcast more than two thousand contract operations in the Echo'"
}


@lcc.disabled()
@lcc.prop("main", "type")
@lcc.tags("broadcast_thousands_transactions")
@lcc.suite("Check scenario 'broadcast_thousands_transactions'", rank=1)
class BroadcastThousandsTransactions(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None
        self.contract = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet()")

    def get_random_limit_integer(self, start, limit):
        random_int = random.randrange(start, limit)
        lcc.log_info("Generated random integer: {}".format(random_int))
        return random_int

    def get_head_block_num(self):
        return self.echo.api.database.get_dynamic_global_properties()["head_block_number"]

    def get_block(self, num):
        return self.echo.api.database.get_block(num)

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
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("The scenario describes creating many calling contract operations in chain")
    def create_many_calling_contract_operations(self, get_random_integer):
        subscription_callback_id = get_random_integer
        number_of_transactions = self.get_random_limit_integer(10000, 11000)
        all_transactions, trx_operations, signed_trx, operations = [], [], [], []

        lcc.set_step("Create and collect {} operations".format(number_of_transactions))
        self.produce_block(self.__database_api_identifier)
        start_broadcast_block = self.get_head_block_num()
        lcc.log_info("Broadcasting start block number {}".format(start_broadcast_block + 1))
        for i in range(number_of_transactions):
            transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                      from_account_id=self.echo_acc0,
                                                                      to_account_id=self.echo_acc1, amount=i + 1)
            collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
            signed_trx.append(self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                      no_broadcast=True))
            operations.append(transfer_operation)
        lcc.log_info("{} transactions prepared".format(number_of_transactions))

        lcc.set_step("Broadcast transactions")
        while True:
            for signed_tx in signed_trx:
                params = [subscription_callback_id, signed_tx]
                response_id = self.send_request(self.get_request("broadcast_transaction_with_callback", params),
                                                self.__network_broadcast_identifier)
                self.get_response(response_id)
            break

        self.produce_block(self.__database_api_identifier)
        end_broadcast_block = self.get_head_block_num()
        lcc.log_info("Brodcasting finish block number {}".format(end_broadcast_block))

        for block_num in range(start_broadcast_block + 1, end_broadcast_block + 1):
            transactions = self.get_block(block_num)["transactions"]
            all_transactions.extend(transactions)
            for trx in all_transactions:
                trx_operations.extend(trx["operations"])
        require_that("broadcasted transactions length", len(all_transactions),
                     greater_than_or_equal_to(number_of_transactions),
                     quiet=False)

        lcc.set_step("Check broadcasted transactions in blocks.")
        operation_count = 0
        for i, operation in enumerate(operations):
            if operation[:2] in trx_operations:
                operation_count += 1
        require_that(
            "'all operations in blocks transactions'",
            operation_count == number_of_transactions, is_true(),
            quiet=False
        )
