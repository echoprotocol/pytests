# -*- coding: utf-8 -*-

from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, is_list

SUITE = {
    "description": "Operation 'DID update'"
}


@lcc.disabled()
@lcc.prop("main", "type")
@lcc.tags("operations", "did_operations", "did_update")
@lcc.suite("Check work of method 'DID create'", rank=1)
class DIDUpdate(BaseTest):

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
            "API identifiers are: database='{}', registration='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier
            )
        )
        self.echo_acc0 = self.get_account_id(
            self.accounts[0], self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo account is {}".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'DID update'")
    def method_main_check(self):
        public_key = self.generate_keys()[1][4:]
        update_public_key = self.generate_keys()[1][4:]

        lcc.set_step("Perform DID create operation")
        transfer_operation = self.echo_ops.did_create_operation(
            echo=self.echo, registrar=self.echo_acc0, essence=self.echo_acc0, public_keys=public_key
        )
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        lcc.log_info("'DID create' operation broadcasted successfully")

        lcc.set_step("Perform DID update operation")
        did_id = broadcast_result["trx"]["operation_results"][0][1]
        transfer_operation = self.echo_ops.did_update_operation(
            echo=self.echo,
            registrar=self.echo_acc0,
            did_identifier="255." + did_id,
            pub_keys_to_delete=[public_key],
            pub_keys_to_add=[update_public_key]
        )
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("'DID update' operation broadcasted successfully")

        lcc.set_step("Check DID object after operation 'DID_update'")
        did_id = broadcast_result["trx"]["operation_results"][0][1]
        response_id = self.send_request(self.get_request("get_objects", [[did_id]]), self.__database_api_identifier)
        result = self.get_response(response_id)["result"][0]
        if not self.type_validator.is_did_object_id(result["id"]):
            lcc.log_error("Wrong format of 'id', got: {}".format(result["id"]))
        else:
            lcc.log_info("'id' has correct format: did_object_did")
        check_that('public key', result["public_keys"], equal_to([update_public_key]))
        check_that('essence', result["essence"], equal_to(self.echo_acc0))
        check_that('extensions', result["extensions"], is_list())
