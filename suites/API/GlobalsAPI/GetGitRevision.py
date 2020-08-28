# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, is_none, is_not_none, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_git_revision'"
}


@lcc.prop("main", "type")
@lcc.tags("methods", "global_api", "get_git_revision")
@lcc.suite("Check work of method 'get_git_revision_'", rank=1)
class GeGitRevision(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__did_api_identifier = None
        self.echo_acc0 = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'get_git_revision'")
    def method_main_check(self):
        lcc.set_step("Call method 'get_git_revision'")
        response_id = self.send_request(self.get_request("get_git_revision", []),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        require_that('result', result["ECHO_GIT_REVISION_SHA"], equal_to("63bf1ff6bec5198d17b604ad13a09f9506cd5713"))
        require_that('result', result["ECHO_GIT_REVISION_UNIX_TIMESTAMP"], equal_to("4 days ago"))
        require_that('result', result["ECHO_GIT_REVISION_DESCRIPTION"], equal_to("0.21-rc.2"))
