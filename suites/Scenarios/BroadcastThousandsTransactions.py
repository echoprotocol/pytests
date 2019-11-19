# -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, greater_than_or_equal_to, is_true

from common.base_test import BaseTest

SUITE = {
    "description": "Scenario 'Collect and broadcast more than two thousand contract operations in the Echo'"
}


@lcc.tags("TASK ECHOT-280")
@lcc.disabled()
@lcc.prop("main", "type")
@lcc.tags("scenarios", "broadcast_thousands_transactions")
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
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc1 = self.get_account_id(self.accounts[1], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("The scenario describes creating many calling contract operations in chain")
    def create_many_calling_contract_operations(self):
        number_of_transactions = self.get_random_limit_integer(2000, 3000)
        operations = []
        all_transactions, trx_operations = [], []

        lcc.set_step("Create and collect {} operations".format(number_of_transactions))
        for amount_value in range(number_of_transactions):
            transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                      from_account_id=self.echo_acc0,
                                                                      to_account_id=self.echo_acc1,
                                                                      amount=amount_value + 1)
            operations.append(transfer_operation)
        start_broadcast_block = self.get_head_block_num()

        lcc.set_step("Broadcast transactions")
        for transaction_num in range(number_of_transactions):
            collected_operation = self.collect_operations(
                operations[transaction_num],
                self.__database_api_identifier
            )
            self.echo_ops.broadcast(
                echo=self.echo,
                list_operations=collected_operation,
                broadcast_with_callback=True,
                log_broadcast=False
            )
        end_broadcast_block = self.get_head_block_num()

        print("1")
        while True:
            if start_broadcast_block <= self.get_head_block_num():
                if len(self.get_block(start_broadcast_block)["transactions"]):
                    break
                start_broadcast_block += 1
        print("2")
        while True:
            if end_broadcast_block <= self.get_head_block_num():
                if not len(self.get_block(end_broadcast_block)["transactions"]):
                    break
                end_broadcast_block += 1
        print("3")
        for block_num in range(start_broadcast_block, end_broadcast_block):
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
