# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_, is_list

from common.base_test import BaseTest

SUITE = {
    "description": "Check all the methods belonging to the history_api"
}


@lcc.suite("Testing 'History API' methods call")
class HistoryApi(BaseTest):

    def __init__(self):
        super().__init__()
        self.__api_identifier = self.get_identifier("history")

    @lcc.test("Get account history")
    def test_get_account_history(self):
        lcc.set_step("Get account history")
        response_id = self.send_request(self.get_request("get_account_history"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get account history")
        check_that(
            "'account history'",
            response["result"],
            is_list(self.get_expected("get_account_history")),
        )

    @lcc.test("Get relative account history")
    def test_get_relative_account_history(self):
        lcc.set_step("Get relative account history")
        response_id = self.send_request(self.get_request("get_relative_account_history"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get relative account history")
        check_that(
            "'relative account history'",
            response["result"],
            is_list(self.get_expected("get_relative_account_history")),
        )

    @lcc.test("Get account history operations")
    def test_get_account_history_operations(self):
        lcc.set_step("Get account history operations")
        response_id = self.send_request(self.get_request("get_account_history_operations"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get account history operations")
        check_that(
            "'account history operations'",
            response["result"],
            is_(self.get_expected("get_account_history_operations")),
        )

    @lcc.test("Get contract history")
    def test_get_contract_history(self):
        lcc.set_step("Get contract history")
        response_id = self.send_request(self.get_request("get_contract_history"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get contract history")
        check_that(
            "'contract history'",
            response["result"],
            is_(self.get_expected("get_contract_history")),
        )
