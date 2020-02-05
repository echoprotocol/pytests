# -*- coding: utf-8 -*-


import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_integer, has_entry, is_not_none

from common.base_test import BaseTest
from common.receiver import Receiver

SUITE = {
    "description": "Registration Api"
}


@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.prop("negative", "type")
@lcc.tags("api", "notice", "registration_api")
@lcc.suite("Registration API", rank=1)
class RegistrationApi(object):

    @lcc.tags("connection_to_registration_api", "connection_to_apis")
    @lcc.test("Check connection to RegistrationApi")
    def connection_to_registration_api(self):
        base = BaseTest()
        base.ws = base.create_connection_to_echo()
        base.receiver = Receiver(web_socket=base.ws)
        lcc.set_step("Requesting Access to a Registration API")
        api_identifier = base.get_identifier("registration")
        check_that("'registration api identifier'", api_identifier, is_integer())

        lcc.set_step("Check Registration api identifier. Call registration api method 'register_account'")

        response_id = base.send_request(base.get_request("request_registration_task"), api_identifier)
        response = base.get_response(response_id)
        check_that(
            "'call method 'request_registration_task''",
            response["result"], is_not_none(), quiet=True
        )

        lcc.set_step("Check that History api identifier is unique")
        response_id = base.send_request(base.get_request("request_registration_task"), api_identifier + 1)
        response = base.get_response(response_id, negative=True, log_response=True)
        check_that(
            "'using another identifier gives an error'",
            response, has_entry("error"), quiet=True
        )

        base.ws.close()
