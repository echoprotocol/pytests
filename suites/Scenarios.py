# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc


@lcc.prop("testing", "main")
@lcc.tags("scenarios")
@lcc.suite("LoginApi API", rank=1)
class Scenarios:

    @lcc.test("Check that work database_api")
    # @lcc.depends_on("DatabaseApi.connection_to_database_api")  # todo: add with new release lcc
    def database_api(self):
        pass

    @lcc.test("Check that work registration api")
    # @lcc.depends_on("RegistrationApi.connection_to_registration_api")  # todo: add with new release lcc
    def registration_api(self):
        pass
