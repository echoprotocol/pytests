# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.receiver import Receiver

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_integer, is_none

SUITE = {
    "description": "Echorand Api"
}


@lcc.prop("main", "type")
@lcc.tags("api", "echorand_api")
@lcc.suite("Echorand API")
class EchorandApi(object):

    @lcc.tags("connection_to_echorand_api", "connection_to_apis")
    @lcc.test("Check connection to EchorandApi")
    def connection_to_history_api(self, get_random_integer):
        base = BaseTest()
        base.ws = base.create_connection_to_echo()
        base.receiver = Receiver(web_socket=base.ws)
        lcc.set_step("Requesting Access to a History API")
        api_identifier = base.get_identifier("echorand")
        check_that("'echorand api identifier'", api_identifier, is_integer())

        lcc.set_step("Check Echorand api identifier. Call echorand api method 'set_echorand_message_callback'")
        callback_id = get_random_integer
        response_id = base.send_request(
            base.get_request("set_echorand_message_callback", [callback_id]), api_identifier
        )
        response = base.get_response(response_id)

        check_that("'call method 'set_echorand_message_callback''", response["result"], is_none(), quiet=True)
