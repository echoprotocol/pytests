# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, is_none

from common.base_test import BaseTest

SUITE = {
    "description": "Operation 'DID delete'"
}


@lcc.disabled()
@lcc.prop("main", "type")
@lcc.tags("operations", "did_operations", "did_delete")
@lcc.suite("Check work of method 'DID delete'", rank=1)
class DIDDelete(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__did_api_identifier = None
        self.echo_acc0 = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__did_api_identifier = self.get_identifier("did")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is {}".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'DID delete'")
    def method_main_check(self):
        public_key = self.generate_keys()[1][4:]

        lcc.set_step("Perform DID create operation")
        transfer_operation = self.echo_ops.did_create_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                essence=self.echo_acc0,
                                                                public_keys=public_key)
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        lcc.log_info("'DID create' operation broadcasted successfully")

        lcc.set_step("Perform DID delete operation")
        did_id = broadcast_result["trx"]["operation_results"][0][1]
        transfer_operation = self.echo_ops.did_delete_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                did_identifier="255."+did_id)
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        lcc.log_info("'DID delete' operation broadcasted successfully")

        lcc.set_step("Check DID object {} was deleted".format(did_id))
        did_id = broadcast_result["trx"]["operation_results"][0][1]
        response_id = self.send_request(self.get_request("get_objects", [[did_id]]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][0]
        require_that('result', result, is_none())

        #todo: added check by get_did_object
        # lcc.set_step("Call method 'get_did_object'")
        # did_id = broadcast_result["trx"]["operation_results"][0][1]
        # response_id = self.send_request(self.get_request("get_did_object", ["255." + did_id]),
        #                                 self.__did_api_identifier)
        # result = self.get_response(response_id)["result"]
        # require_that('result', result, is_none())
