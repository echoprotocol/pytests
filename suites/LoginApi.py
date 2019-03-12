# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_bool, is_true

from common.base_test import BaseTest

SUITE = {
    "description": "Login Api"
}


@lcc.prop("testing", "main")
@lcc.tags("login_api")
@lcc.suite("LoginApi API", rank=0)
class LoginApi(object):

    @lcc.prop("type", "method")
    @lcc.test("Login with empty credential")
    def login_with_empty_credential(self):
        base = BaseTest()
        lcc.set_step("Login to the Full Node with empty credential")
        response_id = base.send_request(base.get_request("login"))
        response = base.get_response(response_id)

        lcc.set_step("Check that login successful")
        check_that("'login status'", response["result"], is_bool(is_true()))


@lcc.prop("testing", "positive")
@lcc.tags("login_api")
@lcc.suite("Positive testing of method 'login'", rank=1)
class PositiveTesting(object):

    @lcc.prop("type", "method")
    @lcc.test("Login with credential")
    # @lcc.depends_on("LoginApi.login_with_empty_credential")  # todo: add with new release lcc
    def login_with_credential(self):
        lcc.set_step("Login to the Full Node with credential")
        base = BaseTest()
        credential = ["test", "TEST123"]
        response_id = base.send_request(base.get_request("login", credential))
        response = base.get_response(response_id)

        lcc.set_step("Check that login successful")
        check_that("'login status'", response["result"], is_bool(is_true()))

# todo: add when will be validation on login
# @lcc.prop("testing", "negative")
# @lcc.tags("login_api")
# @lcc.suite("Negative testing of method 'login'")
# class NegativeTesting(object):
#
    # @lcc.prop("type", "method")
    # @lcc.test("Login with wrong credential")
    # @lcc.depends_on("LoginApi.login_with_empty_credential")  # todo: add with new release lcc
    # def login_with_wrong_credential(self):
    #     base = BaseTest()
    #     lcc.set_step("Login to the Full Node with wrong credential")
    #     credential = [0, 0]
    #     response_id = base.send_request(base.get_request("login", credential))
    #     response = base.get_response(response_id, negative=True)
    #
    #     lcc.set_step("Check that login not successful")
    #     check_that("'login status'", response["result"], is_bool(is_false()))
