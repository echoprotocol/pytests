# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.receiver import Receiver

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, has_entry, is_integer, is_not_none

SUITE = {
    "description": "Database Api"
}


@lcc.prop("main", "type")
@lcc.tags("api", "database_api")
@lcc.suite("Database API")
class DatabaseApi(object):

    @lcc.tags("connection_to_database_api", "connection_to_apis")
    @lcc.test("Check connection to DatabaseApi")
    def connection_to_database_api(self):
        base = BaseTest()
        base.ws = base.create_connection_to_echo()
        base.receiver = Receiver(web_socket=base.ws)
        lcc.set_step("Requesting Access to a Database API")
        api_identifier = base.get_identifier("database")
        check_that("'database api identifier'", api_identifier, is_integer())

        lcc.set_step("Check Database api identifier. Call database api method 'get_objects'")
        response_id = base.send_request(base.get_request("get_objects", [["1.2.0", "1.3.0"]]), api_identifier)
        response = base.get_response(response_id)

        check_that("'call method 'get_objects''", response["result"], is_not_none(), quiet=True)

        lcc.set_step("Check that Database api identifier is unique")
        response_id = base.send_request(base.get_request("get_objects", [["1.2.0", "1.3.0"]]), api_identifier + 1)
        response = base.get_response(response_id, negative=True)

        check_that("'using another identifier gives an error'", response, has_entry("error"), quiet=True)

        base.ws.close()
