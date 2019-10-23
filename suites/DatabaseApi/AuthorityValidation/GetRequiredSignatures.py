# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, has_item, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_required_signatures'"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("Bug ECHO-1029, ECHO-1031")
@lcc.tags("api", "database_api", "database_api_authority_validation", "get_required_signatures")
@lcc.suite("Check work of method 'get_required_signatures'", rank=1)
class GetRequiredSignatures(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None

    def get_account_info(self, account_id):
        response_id = self.send_request(self.get_request("get_accounts", [[account_id]]),
                                        self.__database_api_identifier)
        return self.get_response(response_id)["result"][0]

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
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'get_required_signatures'")
    def method_main_check(self):
        lcc.set_step("Get account active keys")
        account_info = self.get_account_info(self.echo_acc0)
        lcc.log_info("Active keys of account {} were taken".format(self.echo_acc0))

        lcc.set_step("Build transfer transaction")
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=self.echo_acc0,
                                                                  to_account_id=self.echo_acc1)
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        signed_tx = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                            no_broadcast=True)

        del signed_tx["signatures"]
        lcc.log_info("Transaction was built")

        expected_keys = [account_info['active']["key_auths"][0][0]]

        lcc.set_step("Get potential signatures for built transaction")
        response_id = self.send_request(self.get_request("get_potential_signatures", [signed_tx]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call 'get_potential_signatures' method for built transaction")

        lcc.set_step("Check 'get_potential_signatures' method result")
        require_that(
            "potential keys",
            response["result"], equal_to(expected_keys), quiet=True
        )

        lcc.set_step("Get required signatures for bulded transaction")
        response_id = self.send_request(
            self.get_request(
                "get_required_signatures",
                [signed_tx, expected_keys]
            ),
            self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info(
            "Call 'get_required_signatures' method for built transaction and "
            "keys from 'get_potential_signatures' method"
        )

        lcc.set_step("Check 'get_required_signatures' method result")
        require_that(
            "required keys",
            response["result"], equal_to(expected_keys), quiet=True
        )


@lcc.prop("positive", "type")
@lcc.tags("api", "database_api", "database_api_authority_validation", "get_required_signatures")
@lcc.suite("Positive testing of method 'get_required_signatures'", rank=2)
class PositiveTesting(BaseTest):
    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc5 = None
        self.echo_acc6 = None
        self.reserved_public_key = None

    def get_account_info(self, account_id):
        response_id = self.send_request(self.get_request("get_accounts", [[account_id]]),
                                        self.__database_api_identifier)
        return self.get_response(response_id)["result"][0]

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
        self.echo_acc5 = self.get_account_id(self.accounts[5], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc6 = self.get_account_id(self.accounts[6], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc7 = self.get_account_id(self.accounts[7], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info(
            "Echo accounts are: #1='{}', #2='{}', #3='{}', #4='{}'".format(
                self.echo_acc0,
                self.echo_acc5,
                self.echo_acc6,
                self.echo_acc7
            )
        )
        self.reserved_public_key = self.get_reserved_public_key()
        lcc.log_info("Reserved public key: {}".format(self.reserved_public_key))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Add additional account_auths and change weight_threshold to account and get required signatures for it")
    @lcc.depends_on("DatabaseApi.AuthorityValidation.GetRequiredSignatures.GetRequiredSignatures.method_main_check")
    def get_potential_signatures_of_accounts_with_additional_account_auths(self):
        lcc.set_step("Get account active keys")
        account_info_1 = self.get_account_info(self.echo_acc5)
        account_active_keys_1 = account_info_1["active"]
        lcc.log_info("Active keys of account {} were taken".format(self.echo_acc5))

        lcc.set_step("Get account active keys")
        account_info_2 = self.get_account_info(self.echo_acc6)
        account_active_keys_2 = account_info_2["active"]
        lcc.log_info("Active keys of account {} were taken".format(self.echo_acc6))

        lcc.set_step("Update info of '{}' account (add account_auths)".format(self.echo_acc6))
        account_auths = [account_auth[0] for account_auth in account_active_keys_2["account_auths"]]
        account_auths_new_item = [self.echo_acc5, 2]
        if self.echo_acc5 not in account_auths:
            new_active_keys = account_active_keys_2.copy()
            new_active_keys["account_auths"].extend([account_auths_new_item])
            new_active_keys["weight_threshold"] = 2
            account_info_2["active"] = new_active_keys
            self.utils.perform_account_update_operation(self, self.echo_acc6, account_info_2,
                                                        self.__database_api_identifier)
        lcc.log_info("'account_auths' of '{}' account was updated".format(self.echo_acc6))

        lcc.set_step("Get active keys info about account")
        actual_account_info_2 = self.get_account_info(self.echo_acc6)
        actual_account_active_keys_2 = actual_account_info_2["active"]
        require_that(
            "new keys",
            actual_account_active_keys_2["account_auths"], has_item(account_auths_new_item),
            quiet=True
        )

        lcc.set_step("Build transfer transaction")
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=self.echo_acc6,
                                                                  to_account_id=self.echo_acc5)
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        signed_tx = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                            no_broadcast=True)
        del signed_tx["signatures"]
        lcc.log_info("Transaction was built")

        expected_keys = [
            account_active_keys_1["key_auths"][0][0]
        ]

        lcc.set_step("Get potential signatures for builded transaction")
        response_id = self.send_request(self.get_request("get_potential_signatures", [signed_tx]),
                                        self.__database_api_identifier)
        potential_keys = self.get_response(response_id)["result"]
        lcc.log_info("Call 'get_potential_signatures' method for builded transaction")

        lcc.set_step("Get required signatures for builded transaction with pontential keys")
        response_id = self.send_request(
            self.get_request(
                "get_required_signatures",
                [signed_tx, potential_keys]
            ),
            self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info("Call 'get_required_signatures' method for builded transaction with potential keys")

        lcc.set_step("Check 'get_required_signatures' method result")
        require_that(
            "required keys",
            response["result"], equal_to(expected_keys), quiet=True
        )

    @lcc.test("Add additional key_auths and change weight_threshold to account and get required signatures for it")
    @lcc.depends_on("DatabaseApi.AuthorityValidation.GetRequiredSignatures.GetRequiredSignatures.method_main_check")
    def get_potential_signatures_of_accounts_with_additional_key_auths(self):
        lcc.set_step("Get account active keys")
        account_info = self.get_account_info(self.echo_acc7)
        account_active_keys = account_info["active"]
        lcc.log_info("Active keys of account {} were taken".format(self.echo_acc7))

        lcc.set_step("Update info of '{}' account (add key_auths)".format(self.echo_acc7))
        key_auths = [key_auth[0] for key_auth in account_active_keys["key_auths"]]
        key_auths_new_item = [self.reserved_public_key, 2]
        if self.reserved_public_key not in key_auths:
            new_active_keys = account_active_keys.copy()
            new_active_keys["key_auths"].extend([key_auths_new_item])
            new_active_keys["weight_threshold"] = 2
            account_info["active"] = new_active_keys
            self.utils.perform_account_update_operation(self, self.echo_acc7, account_info,
                                                        self.__database_api_identifier)
        lcc.log_info("'key_auths' of '{}' account was updated".format(self.echo_acc7))

        lcc.set_step("Get active keys info about account")
        actual_account_info = self.get_account_info(self.echo_acc7)
        actual_account_active_keys = actual_account_info["active"]
        require_that(
            "new keys",
            actual_account_active_keys["key_auths"], has_item(key_auths_new_item),
            quiet=True
        )

        lcc.set_step("Build transfer transaction")
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=self.echo_acc7,
                                                                  to_account_id=self.echo_acc0)
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        signed_tx = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                            no_broadcast=True)
        del signed_tx["signatures"]
        lcc.log_info("Transaction was built")

        expected_keys = [
            self.reserved_public_key
        ]

        lcc.set_step("Get potential signatures for builded transaction")
        response_id = self.send_request(self.get_request("get_potential_signatures", [signed_tx]),
                                        self.__database_api_identifier)
        potential_keys = self.get_response(response_id)["result"]
        lcc.log_info("Call 'get_potential_signatures' method for builded transaction")

        lcc.set_step("Get required signatures for builded transaction with pontential keys")
        response_id = self.send_request(
            self.get_request(
                "get_required_signatures",
                [signed_tx, potential_keys]
            ),
            self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info("Call 'get_required_signatures' method for builded transaction with potential keys")

        lcc.set_step("Check 'get_required_signatures' method result")
        require_that(
            "required keys",
            response["result"], equal_to(expected_keys), quiet=True
        )
