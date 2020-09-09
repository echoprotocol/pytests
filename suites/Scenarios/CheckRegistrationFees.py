# -*- coding: utf-8 -*-

from common.base_test import BaseTest
from fixtures.base_fixtures import get_random_valid_account_name

import lemoncheesecake.api as lcc

SUITE = {
    "description": "Checks fee changes after registration of several accounts"
}


@lcc.prop("main", "type")
@lcc.tags("scenarios", "check_registration_fees")
@lcc.suite("Check scenario 'check_registration_fees'", rank=1)
class CheckRegistrationFees(BaseTest):

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
            "API identifiers are: database='{}', registration='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier
            )
        )
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo accounts are: #1='{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("The scenario checks fee changes after registration of several accounts")
    def method_main_check(self):
        account_name = get_random_valid_account_name()
        public_key = self.generate_keys()
        steps = 10
        operation = self.echo_ops.get_account_create_operation(
            self.echo, account_name, public_key[1], public_key[1], registrar=self.echo_acc0, signer=self.echo_acc0
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        previous_fee = collected_operation[0][1]['fee']["amount"]
        for i in range(steps):
            account_name = get_random_valid_account_name()
            public_key = self.generate_keys()

            lcc.set_step("Perform account creation operation")
            operation = self.echo_ops.get_account_create_operation(
                self.echo, account_name, public_key[1], public_key[1], registrar=self.echo_acc0, signer=self.echo_acc0
            )
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            current_fee = collected_operation[0][1]['fee']["amount"]
            self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
            if previous_fee != current_fee:
                lcc.log_error("Test failed, fee for account create operation increased")
            previous_fee = current_fee
        lcc.log_info("Registarated {} accounts, fee collected per registration: {}".format(steps, current_fee))
        lcc.log_info("Test passed!")
