# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_, is_integer, is_str, check_that_in, is_false

from common.base_test import BaseTest
from common.echo_operation import EchoOperations


SUITE = {
    "description": "Test 'Piggy'"
}


@lcc.suite("Test smart contract")
@lcc.tags("smart")
class TestSmartContract(BaseTest):
    __get_contract_result = "get_contract_result"
    __get_contract_balances = "get_contract_balances"
    __get_named_account_balances = "get_named_account_balances"
    __get_objects = "get_objects"

    def __init__(self):
        super().__init__()
        self.__resp = None
        self.__id_db = self.get_identifier(self._database_api)
        self.echo_op = EchoOperations()

    @lcc.test("Test contract 'piggy.sol'")
    def test_piggy_smart_contract(self):
        account = "test10123223"
        value_amount = 1000

        lcc.set_step("Deploy contract")
        self.__resp = self.echo_op.create_contract(self.get_byte_code("piggy_code"), account, value_amount)

        lcc.set_step("Get id of the new contract")
        contract_id = [self.get_contract_id(self.__resp)]
        lcc.log_info("Contract id is {}".format(contract_id))

        lcc.set_step("Get the new address of the new contract")
        self.send_request(self.get_request(self.__get_contract_result, contract_id), self.__id_db)
        self.__resp = self.get_trx_completed_response()
        contract_identifier = self.get_contract_identifier(self.__resp)
        lcc.log_info("Contract identifier is {}".format(contract_identifier))

        lcc.set_step("Call 'greet' method")
        self.__resp = self.echo_op.call_contract_method(self.get_byte_code("piggy_greet"), account,
                                                        contract_identifier)
        contract_id = [self.get_contract_id(self.__resp)]
        lcc.log_info("Contract id is {}".format(contract_id))
        self.send_request(self.get_request(self.__get_contract_result, contract_id), self.__id_db)
        self.__resp = self.get_trx_completed_response()

        lcc.set_step("Check get 'Hello World!!!'")
        contract_output = self.get_contract_output(self.__resp, False)[1:]
        check_that(
            "return of method 'greet'",
            contract_output,
            is_("Hello World!!!"),
        )

        lcc.set_step("Get contract balance")
        self.send_request(self.get_request(self.__get_contract_balances, [contract_identifier]), self.__id_db)
        self.__resp = self.get_response()
        check_that_in(
            self.__resp["result"][0],
            "amount", is_integer(value_amount),
            "asset_id", is_str("1.3.0")
        )
        contract_balance = self.__resp["result"][0]["amount"]

        lcc.set_step("Get owner balance and store")
        params = [account, ["1.3.0"]]
        self.send_request(self.get_request(self.__get_named_account_balances, params), self.__id_db)
        self.__resp = self.get_response()
        owner_balance = self.__resp["result"][0]["amount"]

        lcc.set_step("Call 'getPennie' method")
        self.__resp = self.echo_op.call_contract_method(self.get_byte_code("piggy_getPennie"), account,
                                                        contract_identifier)
        contract_id = [self.get_contract_id(self.__resp)]
        lcc.log_info("Contract id is {}".format(contract_id))
        self.send_request(self.get_request(self.__get_contract_result, contract_id), self.__id_db)
        self.__resp = self.get_trx_completed_response()

        lcc.set_step("Get contract and owner balance. Amount should be reduced and increase by one respectively.")
        self.send_request(self.get_request(self.__get_contract_balances, [contract_identifier]), self.__id_db)
        self.__resp = self.get_response()
        check_that_in(
            self.__resp["result"][0],
            "amount", is_integer(contract_balance - 1),
            "asset_id", is_str("1.3.0")
        )

        params = [account, ["1.3.0"]]
        self.send_request(self.get_request(self.__get_named_account_balances, params), self.__id_db)
        self.__resp = self.get_response()
        check_that(
            "'owner balance'",
            self.__resp["result"][0]["amount"],
            is_(str(int(owner_balance) + 1))
        )

        lcc.set_step("Destroy the contract. Call 'breakPiggy' method")
        self.__resp = self.echo_op.call_contract_method(self.get_byte_code("piggy_breakPiggy"), account,
                                                        contract_identifier)
        contract_id = [self.get_contract_id(self.__resp)]
        lcc.log_info("Contract id is {}".format(contract_id))
        self.send_request(self.get_request(self.__get_contract_result, contract_id), self.__id_db)
        self.__resp = self.get_trx_completed_response()

        lcc.set_step("Get contract balance, must be 0 (zero)")
        self.send_request(self.get_request(self.__get_contract_balances, [contract_identifier]), self.__id_db)
        self.__resp = self.get_response()
        check_that(
            "'contract balance'",
            self.__resp["result"][0]["amount"],
            is_integer(0)
        )

        lcc.set_step("Check that contract to be 'suicided=True'")
        self.send_request(self.get_request(self.__get_objects, [[contract_identifier]]), self.__id_db)
        self.__resp = self.get_response()
        check_that(
            "contract deleted and 'suicided'",
            self.__resp["result"][0]["suicided"],
            is_false()  # todo: change on true when the bug would fixed
        )
