# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

SUITE = {
    "description": "Method 'get_btc_stake_address'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags(
    "api", "database_api", "sidechain", "sidechain_bitcoin", "database_api_sidechain_bitcoin", "get_btc_stake_address"
)
@lcc.suite("Check work of method 'get_btc_stake_address'", rank=1)
class GetBtcStakeAddress(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_ethereum()
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

    @lcc.test("Simple work of method 'get_btc_stake_address'")
    def method_main_check(self, get_random_btc_public_key, get_random_valid_account_name):
        new_account_name = get_random_valid_account_name
        btc_public_key = get_random_btc_public_key
        pubkey_hash = self.utils.get_public_hash(btc_public_key)
        lcc.set_step("Create and get new account")
        new_account_id = self.get_account_id(
            new_account_name, self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account_id))

        lcc.set_step("Perform sidechain_stake_btc_create_script")
        operation = self.echo_ops.get_sidechain_stake_btc_create_script_operation(
            echo=self.echo, account=new_account_id, pubkey_hash=pubkey_hash
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=1):
            lcc.log_error("'sidechain_stake_btc_create_script' fallen while broadcast")
        else:
            lcc.log_info("'sidechain_stake_btc_create_script' broadcasted successfully.")
        lcc.set_step("Call 'get_btc_stake_address' method and check its result")
        response_id = self.send_request(
            self.get_request("get_btc_stake_address", [new_account_id]), self.__database_api_identifier
        )
        result = self.get_response(response_id)["result"]
        if self.type_validator.is_btc_stake_address_id(result['id']):
            lcc.log_info("Correct format of `btc_stake_address_id`, got: {}".format(result['id']))
        else:
            lcc.log_info("Wrong format of `btc_stake_address_id`, got: {}".format(result['id']))
        check_that("account", result['account'], equal_to(new_account_id))
        if self.type_validator.is_btc_address(result['address']):
            lcc.log_info("New btc_address created!")
        else:
            lcc.log_info("Wrong btc_address format")
        if self.type_validator.is_hex(result['stake_script']):
            lcc.log_info("correct format of stake script, got: {}".format(result['stake_script']))
        else:
            lcc.log_info("Wrong format of stake script, got: {}".format(result['stake_script']))
