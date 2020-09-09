# -*- coding: utf-8 -*-
from common.base_test import BaseTest

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import has_item, is_true, require_that

SUITE = {
    "description": "Method 'verify_account_authority'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_authority_validation", "verify_account_authority")
@lcc.suite("Check work of method 'verify_account_authority'", rank=1)
class VerifyAccountAuthority(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc0_name = None

    def get_account_info(self, account_id):
        response_id = self.send_request(
            self.get_request("get_accounts", [[account_id]]), self.__database_api_identifier
        )
        return self.get_response(response_id)["result"][0]

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
        self.echo_acc0_name = self.accounts[0]
        self.echo_acc0 = self.get_account_id(
            self.echo_acc0_name, self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'verify_account_authority'")
    def method_main_check(self):
        lcc.set_step("Get account active keys")
        account_info = self.get_account_info(self.echo_acc0)
        account_public_key = account_info["active"]["key_auths"][0][0]
        lcc.log_info("Active keys of account {} were taken".format(self.echo_acc0))

        lcc.set_step("Verify authority of '{}' account".format(self.echo_acc0))
        params = [self.echo_acc0_name, [account_public_key]]
        response_id = self.send_request(
            self.get_request("verify_account_authority", params), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info("Call 'verify_account_authority' with '{}' parameters".format(params))

        require_that("account authority verify status", response["result"], is_true())


@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_authority_validation", "verify_account_authority")
@lcc.suite("Positive testing of method 'verify_account_authority'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc3 = None
        self.echo_acc4 = None
        self.echo_acc4_name = None
        self.reserved_public_key = None

    def get_account_info(self, account_id):
        response_id = self.send_request(
            self.get_request("get_accounts", [[account_id]]), self.__database_api_identifier
        )
        return self.get_response(response_id)["result"][0]

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
        self.echo_acc3 = self.get_account_id(
            self.accounts[3], self.__database_api_identifier, self.__registration_api_identifier
        )
        self.echo_acc4_name = self.accounts[4]
        self.echo_acc4 = self.get_account_id(
            self.echo_acc4_name, self.__database_api_identifier, self.__registration_api_identifier
        )
        lcc.log_info(
            "Echo accounts are: #1='{}', #2='{}', #3='{}'".format(self.echo_acc0, self.echo_acc3, self.echo_acc4)
        )
        self.reserved_public_key = self.get_reserved_public_key()
        lcc.log_info("Reserved public key: {}".format(self.reserved_public_key))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Add additional account_auths to account and verify account authority for it")
    @lcc.depends_on(
        "API.DatabaseApi.AuthorityValidation.VerifyAccountAuthority.VerifyAccountAuthority.method_main_check"
    )
    def get_potential_signatures_of_accounts_with_additional_account_auths(self):
        lcc.set_step("Get account active keys")
        account_info_1 = self.get_account_info(self.echo_acc3)
        account_active_keys_1 = account_info_1["active"]
        lcc.log_info("Active keys of account {} were taken".format(self.echo_acc3))

        lcc.set_step("Get account active keys")
        account_info_2 = self.get_account_info(self.echo_acc4)
        account_active_keys_2 = account_info_2["active"]
        lcc.log_info("Active keys of account {} were taken".format(self.echo_acc4))

        lcc.set_step("Update info of '{}' account (add account_auths)".format(self.echo_acc4))
        account_auths = [account_auth[0] for account_auth in account_active_keys_2["account_auths"]]
        account_auths_new_item = [self.echo_acc3, 1]
        if self.echo_acc3 not in account_auths:
            new_active_keys = account_active_keys_2.copy()
            new_active_keys["account_auths"].extend([account_auths_new_item])
            account_info_2["active"] = new_active_keys
            self.utils.perform_account_update_operation(
                self, self.echo_acc4, account_info_2, self.__database_api_identifier
            )
        lcc.log_info("'account_auths' of '{}' account was updated".format(self.echo_acc4))

        lcc.set_step("Get active keys info about account")
        actual_account_info_2 = self.get_account_info(self.echo_acc4)
        actual_account_active_keys_2 = actual_account_info_2["active"]
        require_that(
            "new keys", actual_account_active_keys_2["account_auths"], has_item(account_auths_new_item), quiet=True
        )

        account_public_key_1 = account_active_keys_1["key_auths"][0][0]

        lcc.set_step("Verify authority of '{}' account".format(self.echo_acc4))
        params = [self.echo_acc4_name, [account_public_key_1]]
        response_id = self.send_request(
            self.get_request("verify_account_authority", params), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info("Call 'verify_account_authority' with '{}' parameters".format(params))

        require_that("account authority verify status", response["result"], is_true())

    @lcc.test("Add additional key_auths to account and verify account authority for it")
    @lcc.depends_on(
        "API.DatabaseApi.AuthorityValidation.VerifyAccountAuthority.VerifyAccountAuthority.method_main_check"
    )
    def get_potential_signatures_of_accounts_with_additional_key_auths(self):
        lcc.set_step("Get account active keys")
        account_info_2 = self.get_account_info(self.echo_acc4)
        account_active_keys_2 = account_info_2["active"]
        lcc.log_info("Active keys of account {} were taken".format(self.echo_acc4))

        lcc.set_step("Update info of '{}' account (add key_auths)".format(self.echo_acc4))
        key_auths = [key_auth[0] for key_auth in account_active_keys_2["key_auths"]]
        key_auths_new_item = [self.reserved_public_key, 1]
        if self.reserved_public_key not in key_auths:
            new_active_keys = account_active_keys_2.copy()
            new_active_keys["key_auths"].extend([key_auths_new_item])
            account_info_2["active"] = new_active_keys
            self.utils.perform_account_update_operation(
                self, self.echo_acc4, account_info_2, self.__database_api_identifier
            )
        lcc.log_info("'key_auths' of '{}' account was updated".format(self.echo_acc4))

        lcc.set_step("Get active keys info about account")
        actual_account_info_2 = self.get_account_info(self.echo_acc4)
        actual_account_active_keys_2 = actual_account_info_2["active"]
        require_that("new keys", actual_account_active_keys_2["key_auths"], has_item(key_auths_new_item), quiet=True)

        lcc.set_step("Verify authority of '{}' account".format(self.echo_acc4))
        params = [self.echo_acc4_name, [self.reserved_public_key]]
        response_id = self.send_request(
            self.get_request("verify_account_authority", params), self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info("Call 'verify_account_authority' with '{}' parameters".format(params))

        require_that("account authority verify status", response["result"], is_true())
