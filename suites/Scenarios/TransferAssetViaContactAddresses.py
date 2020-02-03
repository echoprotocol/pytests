# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that_in, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Transfer assets using account addresses"
}


@lcc.prop("main", "type")
@lcc.tags("scenarios", "transfer_asset_via_account_address")
@lcc.suite("Check scenario 'Transfer assets via account address'")
class TransferAssetViaContactAddresses(BaseTest):

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
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("The scenario describes the ability to transfer assets via account address recipient")
    def transfer_asset_via_account_address(self, get_random_valid_account_name, get_random_string, get_random_integer,
                                           get_random_integer_up_to_fifty):
        new_account = get_random_valid_account_name
        label = get_random_string
        addresses_count = 2
        account_addresses = []
        transfer_amount = get_random_integer
        withdraw_amount = get_random_integer_up_to_fifty
        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get account balance and store")
        balance_before_transfer = self.utils.get_account_balances(self, new_account, self.__database_api_identifier)
        lcc.log_info("Account '{}' balance in '{}' asset: '{}'".format(new_account, self.echo_asset,
                                                                       balance_before_transfer["amount"]))

        lcc.set_step("Create multiple account address for new account")
        for i in range(addresses_count):
            self.utils.perform_account_address_create_operation(self, new_account, label + str(i),
                                                                self.__database_api_identifier
                                                                )

        lcc.set_step("Get addresses of created account in the network and store addresses")
        _from, limit = 0, 100
        params = [new_account, _from, limit]
        response_id = self.send_request(self.get_request("get_account_addresses", params),
                                        self.__database_api_identifier)
        results = self.get_response(response_id)["result"]
        for result in results:
            account_addresses.append(result["address"])
        lcc.log_info("Call method 'get_account_addresses' of new account")

        lcc.set_step("Transfer assets via first account_address")
        self.utils.perform_transfer_to_address_operations(self, self.echo_acc0, account_addresses[0],
                                                          self.__database_api_identifier,
                                                          transfer_amount=transfer_amount,
                                                          fee_asset_id=self.echo_asset
                                                          )

        lcc.set_step("Get account balance after transfer and store")
        balance_after_transfer = self.utils.get_account_balances(self, new_account, self.__database_api_identifier)
        lcc.log_info("Account '{}' balance in '{}' asset: '{}'".format(new_account, self.echo_asset,
                                                                       balance_after_transfer["amount"]))

        lcc.set_step("Check that transfer assets completed successfully")
        check_that_in(
            balance_after_transfer,
            "amount", equal_to(balance_before_transfer["amount"] + transfer_amount),
            "asset_id", equal_to(balance_before_transfer["asset_id"])
        )

        lcc.set_step("Transfer assets via second account_address")
        amount = transfer_amount + transfer_amount
        self.utils.perform_transfer_to_address_operations(self, self.echo_acc0, account_addresses[1],
                                                          self.__database_api_identifier, transfer_amount=amount,
                                                          fee_asset_id=self.echo_asset
                                                          )

        lcc.set_step("Get account balance after second transfer and store")
        balance_after_second_transfer = self.utils.get_account_balances(self, new_account,
                                                                        self.__database_api_identifier)
        lcc.log_info("Account '{}' balance in '{}' asset: '{}'".format(new_account, self.echo_asset,
                                                                       balance_after_second_transfer["amount"]))

        lcc.set_step("Check that second transfer assets completed successfully")
        check_that_in(
            balance_after_second_transfer,
            "amount", equal_to(balance_after_transfer["amount"] + amount),
            "asset_id", equal_to(balance_after_transfer["asset_id"])
        )

        lcc.set_step("Transfer assets received to account address")
        self.utils.perform_transfer_operations(self, new_account, self.echo_acc0, self.__database_api_identifier,
                                               transfer_amount=withdraw_amount, get_only_fee=True)
        lcc.log_info("From the account of the recipient transferred assets to the account sender")

        lcc.set_step("Get account balance after return to sender")
        balance = self.utils.get_account_balances(self, new_account, self.__database_api_identifier)
        check_that_in(
            balance,
            "amount", equal_to(balance_after_second_transfer["amount"] - withdraw_amount),
            "asset_id", equal_to(balance_before_transfer["asset_id"])
        )

        lcc.set_step("Again transfer assets via first account_address")
        amount = transfer_amount + withdraw_amount
        self.utils.perform_transfer_to_address_operations(self, self.echo_acc0, account_addresses[0],
                                                          self.__database_api_identifier, transfer_amount=amount,
                                                          fee_asset_id=self.echo_asset
                                                          )

        lcc.set_step("Get account balance after transfer and store")
        balance_after_transfer = self.utils.get_account_balances(self, new_account, self.__database_api_identifier)
        lcc.log_info("Account '{}' balance in '{}' asset: '{}'".format(new_account, self.echo_asset,
                                                                       balance_after_transfer["amount"]))

        lcc.set_step("Check that transfer assets completed successfully")
        check_that_in(
            balance_after_transfer,
            "amount", equal_to(balance["amount"] + amount),
            "asset_id", equal_to(balance_before_transfer["asset_id"])
        )
