# -*- coding: utf-8 -*-

from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, equal_to

SUITE = {
    "description": "Operation 'account_create'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "asset_transfer_operations", "account_create")
@lcc.suite("Check work of method 'account_create'", rank=1)
class AccountCreate(BaseTest):

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

    @lcc.test("Simple work of method 'account_create'")
    def method_main_check(self, get_random_valid_account_name):
        account_name = get_random_valid_account_name
        public_key = self.generate_keys()

        lcc.set_step("Perform account creation operation")
        operation = self.echo_ops.get_account_create_operation(
            self.echo, account_name, public_key[1], public_key[1], registrar=self.echo_acc0, signer=self.echo_acc0
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(
            echo=self.echo, list_operations=collected_operation, log_broadcast=False
        )
        operation_result = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("Account is created, id='{}'".format(operation_result))

        lcc.set_step("Get account by name")
        response_id = self.send_request(
            self.get_request("get_account_by_name", [account_name]), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_account_by_name' with param: {}".format(account_name))

        lcc.set_step("Checking created account")
        performed_operations = collected_operation[0][1]
        account_info = response["result"]
        check_that_in(
            account_info, "registrar", equal_to(performed_operations["registrar"]), "name",
            equal_to(performed_operations["name"]), "active", equal_to(performed_operations["active"]), "echorand_key",
            equal_to(performed_operations["echorand_key"]), "options", equal_to(performed_operations["options"])
        )
