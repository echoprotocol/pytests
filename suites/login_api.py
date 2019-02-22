# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import is_bool, check_that, is_not_none, is_integer, is_true
from common.base_test import BaseTest


@lcc.test("Login with empty credential")
def test_login_with_empty_credential():
    base = BaseTest()
    lcc.set_step("Login to the Full Node with empty credential")
    response_id = base.send_request(base.get_request("login"))
    response = base.get_response(response_id)

    lcc.set_step("Check that login successful")
    check_that("'login status'", response["result"], is_bool(is_true()))


@lcc.test("Login with credential")
def test_login_with_credential():
    base = BaseTest()
    lcc.set_step("Login to the Full Node with credential")
    credential = ["test", "TEST123"]
    response_id = base.send_request(base.get_request("login", credential))
    response = base.get_response(response_id)

    lcc.set_step("Check that login successful")
    check_that("'login status'", response["result"], is_bool(is_true()))


SUITE = {
    "description": "Check all the methods belonging to the login_api"
}


@lcc.suite("Testing 'Login API' methods call")
class LoginApi(BaseTest):

    def __init__(self):
        super().__init__()

    @lcc.test("Connection to database api")
    def test_connection_to_db_api(self):
        lcc.set_step("Requesting Access to a Database API")
        api_identifier = self.get_identifier("database")
        check_that("'database api identifier'", api_identifier, is_integer())

        lcc.set_step("Check Database api identifier. Call database api method 'get_objects'")
        response_id = self.send_request(self.get_request("get_objects"), api_identifier)
        response = self.get_response(response_id)

        check_that(
            "'call method 'get_objects''",
            response["result"],
            is_not_none(),
        )

        lcc.set_step("Check that Database api identifier is unique")
        response_id = self.send_request(self.get_request("get_objects"), api_identifier + 1)
        response = self.get_response(response_id)

        check_that(
            "'using another identifier gives an error'",
            response["error"],
            is_not_none(),
        )

    @lcc.test("Connection to asset api")
    def test_connection_to_asset_api(self):
        lcc.set_step("Requesting Access to an Asset API")
        api_identifier = self.get_identifier("asset")
        check_that("'asset api identifier'", api_identifier, is_integer())

        lcc.set_step("Check Asset api identifier. Call asset api method 'get_all_asset_holders'")
        response_id = self.send_request(self.get_request("get_all_asset_holders"), api_identifier)
        response = self.get_response(response_id)

        check_that(
            "'call method 'get_all_asset_holders''",
            response["result"],
            is_not_none(),
        )

        lcc.set_step("Check that Asset api identifier is unique")
        response_id = self.send_request(self.get_request("get_objects"), api_identifier + 1)
        response = self.get_response(response_id)

        check_that(
            "'using another identifier gives an error'",
            response["error"],
            is_not_none(),
        )

    @lcc.test("Connection to history api")
    def test_connection_to_history_api(self):
        lcc.set_step("Requesting Access to a History API")
        api_identifier = self.get_identifier("history")
        check_that("'history api identifier'", api_identifier, is_integer())

        lcc.set_step("Check History api identifier. Call asset api method 'get_account_history'")
        response_id = self.send_request(self.get_request("get_account_history"), api_identifier)
        response = self.get_response(response_id)

        check_that(
            "'call method 'get_account_history''",
            response["result"],
            is_not_none(),
        )

        lcc.set_step("Check that Asset api identifier is unique")
        response_id = self.send_request(self.get_request("get_account_history"), api_identifier + 1)
        response = self.get_response(response_id)

        check_that(
            "'using another identifier gives an error'",
            response["error"],
            is_not_none(),
        )
