# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Operation 'create DID'"
}


@lcc.prop("main", "type")
@lcc.tags("operations", "did_operations", "did_create")
@lcc.suite("Check work of method 'DID create'", rank=1)
class DIDCreate(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None

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
        lcc.log_info("Echo account is {}".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'DID create'")
    def method_main_check(self, get_random_btc_public_key):
        public_key = "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"

        lcc.set_step("Perform DID create operation")
        transfer_operation = self.echo_ops.did_create_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                essence=self.echo_acc0,
                                                                public_keys=public_key)
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=True)
        lcc.log_info("'DID create' operation broadcasted successfully")





