# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc

from common.base_test import BaseTest

SUITE = {
    "description": "Test 'Piggy'"
}


@lcc.suite("Test smart contract")
# @lcc.disabled()
class TestSmartContract(BaseTest):
    __get_account_history = "get_account_history"
    __get_contract_result = "get_contract_result"
    __get_contract_balances = "get_contract_balances"
    __get_objects = "get_objects"
    __get_full_accounts = "get_full_accounts"

    def __init__(self):
        super().__init__()
        self.__resp = None
        self.__id_db = self.get_identifier(self._database_api)
        self.__id_history = self.get_identifier(self._history_api)

    # todo: need paste the code here after the library would be created
    # Deploy contract "node deploy.js"

    @lcc.test("Get the address of the new contract")
    @lcc.tags("deploy")
    def test_piggy_smart_contract_step1(self):
        lcc.set_step("Get the address of the new contract")
        params = ["1.17.190"]
        self.send_request(self.get_request(self.__get_contract_result, params), self.__id_db)
        self.__resp = self.get_response()

    # todo: need paste the code here after the library would be created
    # Call the greet method to transfer money to a contract and output 'Hello World !!!' - "node greet.js"

    @lcc.test("Get 'Hello world'")
    @lcc.tags("greet")
    def test_piggy_smart_contract_step2(self):
        lcc.set_step("Get 'Hello world'")
        params = ["1.17.191"]
        self.send_request(self.get_request(self.__get_contract_result, params), self.__id_db)
        self.__resp = self.get_response()

    @lcc.test("Get contract balance")
    @lcc.tags("greet")
    def test_piggy_smart_contract_step3(self):
        lcc.set_step("Получить баланс контракта")
        params = ["1.16.80"]
        self.send_request(self.get_request(self.__get_contract_balances, params), self.__id_db)
        self.__resp = self.get_response()

    @lcc.test("Get owner balance and store")
    def test_piggy_smart_contract_step4(self):
        lcc.set_step("Get owner balance and store")
        params = [["1.2.16"], False]
        self.send_request(self.get_request(self.__get_full_accounts, params), self.__id_db)
        self.__resp = self.get_response()

    # todo: need paste the code here after the library would be created
    # Call the getPennie method to transfer 1 asset to owner - "node getPennie.js"

    @lcc.test("Send one Asset to owner")
    @lcc.tags("getPennie")
    def test_piggy_smart_contract_step5(self):
        lcc.set_step("Send one Asset to owner")
        params = ["1.17.198"]
        self.send_request(self.get_request(self.__get_contract_result, params), self.__id_db)
        self.__resp = self.get_response()

    @lcc.test("Get contract balance. Amount should be reduced by one.")
    @lcc.tags("getPennie")
    def test_piggy_smart_contract_step6(self):
        lcc.set_step("Get contract balance. Amount should be reduced by one.")
        params = ["1.16.80"]
        self.send_request(self.get_request(self.__get_contract_balances, params), self.__id_db)
        self.__resp = self.get_response()

        lcc.set_step("Get owner balance. Amount should be increase by one")
        params = [["1.2.16"], False]
        self.send_request(self.get_request(self.__get_full_accounts, params), self.__id_db)
        self.__resp = self.get_response()

    # todo: need paste the code here after the library would be created
    # Destroy the contract and check balance and status of it - "node breakPiggy.js"

    @lcc.test("Destroy the contract")
    @lcc.tags("breakPiggy")
    def test_piggy_smart_contract_step7(self):
        lcc.set_step("Destroy the contract")
        params = ["1.17.196"]
        self.send_request(self.get_request(self.__get_contract_result, params), self.__id_db)
        self.__resp = self.get_response()

    @lcc.test("Receive confirmation that the contract has been destroyed.")
    @lcc.tags("breakPiggy")
    def test_piggy_smart_contract_step8(self):
        lcc.set_step("Get contract balance, must be 0 (zero)")
        params = ["1.16.80"]
        self.send_request(self.get_request(self.__get_contract_balances, params), self.__id_db)
        self.__resp = self.get_response()

        lcc.set_step("Get that contract to be 'suicided=True'")
        params = [["1.16.80"]]
        self.send_request(self.get_request(self.__get_objects, params), self.__id_db)
        self.__resp = self.get_response()
