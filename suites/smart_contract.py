# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_, is_integer, is_str, check_that_in, is_true, is_list, has_entry, \
    is_none

from common.base_test import BaseTest
from common.echo_operation import EchoOperations

SUITE = {
    "description": "Testing contract creation and calling its methods"
}


@lcc.suite("Creation 'piggy' smart contract and calling its methods")
@lcc.tags("smart")
class PiggySmartContract(BaseTest):

    def __init__(self):
        super().__init__()
        self.__api_identifier = self.get_identifier("database")
        self.echo_op = EchoOperations()

    @lcc.test("Test contract 'piggy.sol'")
    def test_piggy_smart_contract(self, get_random_number):
        account = "test-kazak-1"
        value_amount = 1000
        subscription_callback_id = get_random_number

        lcc.set_step("Deploy contract")
        operation_response = self.echo_op.create_contract(self.get_byte_code("piggy_code"), account, value_amount)

        lcc.set_step("Get performance result of the new contract")
        contract_result = [self.get_contract_result(operation_response)]

        lcc.set_step("Get id of the new contract")
        response_id = self.send_request(self.get_request("get_contract_result", contract_result),
                                        self.__api_identifier)
        contract_id_16 = self.get_trx_completed_response(response_id)
        contract_id = self.get_contract_id(contract_id_16)

        lcc.set_step("Call 'greet' method")
        operation_response = self.echo_op.call_contract_method(self.get_byte_code("piggy_greet"), account,
                                                               contract_id)
        contract_result = [self.get_contract_result(operation_response)]
        response_id = self.send_request(self.get_request("get_contract_result", contract_result),
                                        self.__api_identifier)
        response = self.get_trx_completed_response(response_id)

        lcc.set_step("Check get 'Hello World!!!'")
        contract_output = self.get_contract_output(response, in_hex=False)[1:]
        check_that(
            "return of method 'greet'",
            contract_output,
            is_("Hello World!!!"),
        )

        lcc.set_step("Get contract balance")
        response_id = self.send_request(self.get_request("get_contract_balances", [contract_id]),
                                        self.__api_identifier)
        response = self.get_response(response_id)
        check_that_in(
            response["result"][0],
            "amount", is_integer(value_amount),
            "asset_id", is_str("1.3.0")
        )
        contract_balance = response["result"][0]["amount"]

        lcc.set_step("Get owner balance and store")
        params = [account, ["1.3.0"]]
        response_id = self.send_request(self.get_request("get_named_account_balances", params),
                                        self.__api_identifier)
        response = self.get_response(response_id)
        owner_balance = response["result"][0]["amount"]

        lcc.set_step("Subscribe contract logs")
        params_for_subscribe = [subscription_callback_id, contract_id, 0, 9999]
        response_id = self.send_request(self.get_request("subscribe_contract_logs", params_for_subscribe),
                                        self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check subscribe contract logs")
        check_that(
            "'subscribe contract logs'",
            response["result"],
            is_list([]),
        )

        lcc.set_step("Call 'getPennie' method")
        operation_response = self.echo_op.call_contract_method(self.get_byte_code("piggy_getPennie"), account,
                                                               contract_id)
        contract_result = [self.get_contract_result(operation_response)]

        lcc.set_step("Check contract logs")
        response = self.get_notice(subscription_callback_id)

        object_keys = ["address", "log", "data"]
        for i in range(len(object_keys)):
            check_that(
                "'contract logs'",
                response,
                has_entry(
                    object_keys[i],
                ),
            )
        contract_identifier_16 = contract_id_16["result"][1].get("exec_res").get("new_address")
        check_that_in(
            response,
            "address", is_(contract_identifier_16),
        )

        response_id = self.send_request(self.get_request("get_contract_result", contract_result),
                                        self.__api_identifier)
        self.get_trx_completed_response(response_id)

        lcc.set_step("Get contract and owner balance. Amount should be reduced and increase by one respectively.")
        response_id = self.send_request(self.get_request("get_contract_balances", [contract_id]),
                                        self.__api_identifier)
        response = self.get_response(response_id)
        check_that_in(
            response.get("result")[0],
            "amount", is_integer(contract_balance - 1),
            "asset_id", is_str("1.3.0")
        )

        params = [account, ["1.3.0"]]
        response_id = self.send_request(self.get_request("get_named_account_balances", params),
                                        self.__api_identifier)
        response = self.get_response(response_id)
        check_that(
            "'owner balance'",
            response.get("result")[0].get("amount"),
            is_integer(owner_balance + 1)
        )

        lcc.set_step("Destroy the contract. Call 'breakPiggy' method")
        response = self.echo_op.call_contract_method(self.get_byte_code("piggy_breakPiggy"), account, contract_id)
        contract_result = [self.get_contract_result(response)]
        response_id = self.send_request(self.get_request("get_contract_result", contract_result),
                                        self.__api_identifier)
        self.get_trx_completed_response(response_id)

        lcc.set_step("Get contract balance, must be 0 (zero)")
        response_id = self.send_request(self.get_request("get_contract_balances", [contract_id]),
                                        self.__api_identifier)
        response = self.get_response(response_id)
        check_that(
            "'contract balance'",
            response["result"][0]["amount"],
            is_integer(0)
        )

        lcc.set_step("Check that contract to be 'suicided=True'")
        response_id = self.send_request(self.get_request("get_objects", [[contract_id]]), self.__api_identifier)
        response = self.get_response(response_id)
        check_that(
            "contract deleted and 'destroyed'",
            response["result"][0]["destroyed"],
            is_true()
        )

        lcc.set_step("Cancel all subscriptions")
        response_id = self.send_request(self.get_request("cancel_all_subscriptions"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check that canceled all subscriptions")
        check_that(
            "'subscribe result'",
            response["result"],
            is_none(),
        )
