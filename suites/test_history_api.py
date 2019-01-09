# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_

from common.base_test import BaseTest

SUITE = {
    "description": "Test 'History API'"
}


@lcc.suite("Test asset methods")
class TestAssetMethod(BaseTest):
    __get_account_history = "get_account_history"
    __get_relative_account_history = "get_relative_account_history"
    __get_account_history_operations = "get_account_history_operations"
    __get_contract_history = "get_contract_history"

    def __init__(self):
        super().__init__()
        self.__resp = None
        self.__identifier = self.get_identifier(self._history_api)

    @lcc.test("Get account history")
    def test_get_account_history(self):
        lcc.set_step("Get account history")
        self.send_request(self.get_request(self.__get_account_history), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get account history")
        check_that(
            "'account history'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_account_history)),
        )

    @lcc.test("Get relative account history")
    def test_get_relative_account_history(self):
        lcc.set_step("Get relative account history")
        self.send_request(self.get_request(self.__get_relative_account_history), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get relative account history")
        check_that(
            "'relative account history'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_relative_account_history)),
        )

    @lcc.test("Get account history operations")
    @lcc.tags("empty data receive")
    def test_get_account_history_operations(self):
        lcc.set_step("Get account history operations")
        self.send_request(self.get_request(self.__get_account_history_operations), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get account history operations")
        check_that(
            "'account history operations'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_account_history_operations)),
        )

    @lcc.test("Get contract history")
    @lcc.tags("no contract")
    @lcc.disabled()
    def test_get_contract_history(self):
        lcc.set_step("Get contract history")
        self.send_request(self.get_request(self.__get_contract_history), self.__identifier)
        self.__resp = self.get_response()

        lcc.set_step("Check get contract history")
        check_that(
            "'contract history'",
            self.__resp["result"],
            is_(self.get_expected(self.__get_contract_history)),
        )
