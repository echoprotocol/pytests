# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, not_equal_to
from common.base_test import BaseTest
from datetime import datetime, timedelta
from project import INIT0_PK, INIT1_PK, INIT2_PK, INIT3_PK, INIT4_PK
SUITE = {
    "description": "Operation 'committee_member_update_global_parameters'"
}
@lcc.prop("main", "type")
@lcc.prop("positive", "type")
@lcc.tags("operations", "committee_member_operations", "committee_member_update_global_parameters")
@lcc.suite("Check work of method 'committee_member_update_global_parameters'", rank=1)
class CommitteeMemberUpdateGlobalParameters(BaseTest):
    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.init0 = None
        self.init1 = None
        self.init2 = None
        self.init3 = None
        self.init4 = None

    def get_expiration_time(self, seconds):
        pattern = "%Y-%m-%dT%H:%M:%S"
        now = self.get_datetime(global_datetime=True)
        expiration = datetime.strptime(now, pattern) + timedelta(seconds=seconds)
        return expiration.strftime(pattern)

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))
        self.init0 = self.get_initial_account_id(0, self.__database_api_identifier)
        self.init1 = self.get_initial_account_id(1, self.__database_api_identifier)
        self.init2 = self.get_initial_account_id(2, self.__database_api_identifier)
        self.init3 = self.get_initial_account_id(3, self.__database_api_identifier)
        self.init4 = self.get_initial_account_id(4, self.__database_api_identifier)

    def dynamic(self):
        response_id = self.send_request(self.get_request("get_dynamic_global_properties"), self.__database_api_identifier)
        dyn = self.get_response(response_id, log_response=False)["result"]
        lcc.log_info("{}, {}, {}".format(dyn["head_block_number"], dyn["time"], dyn["next_maintenance_time"]))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("Simple work of method 'committee_member_update_global_parameters'")
    def method_main_check(self):
        response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
        global_properties1 = self.get_response(response_id)["result"]
        lcc.set_step("Perform 'committee_member_update_global_parameters' operation")
        operation = self.echo_ops.get_committee_member_update_global_parameters_operation(
            echo=self.echo, _time_net_1mb=102,
            signer=INIT0_PK, debug_mode=True)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        lcc.set_step("Make proposal of `committee_member_update_global_parameters`")
        expiration_time = self.get_expiration_time(30)
        lcc.log_info("{}".format(expiration_time))
        operation = self.echo_ops.get_proposal_create_operation(
            echo=self.echo,
            fee_paying_account=self.init0,
            proposed_ops=collected_operation,
            expiration_time=expiration_time,
            review_period_seconds=10,
            signer=INIT0_PK
        )
        import time
        # collected_operation = self.collect_operations(operation, self.__database_api_identifier, proposal=True)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=operation, log_broadcast=True)
        self.dynamic()
        proposal_id = broadcast_result["trx"]["operation_results"][0][1]
        lcc.set_step("Make voting for new global parameters")
        operation = self.echo_ops.get_proposal_update_operation(
            echo=self.echo,
            fee_paying_account=self.init1,
            proposal=proposal_id,
            active_approvals_to_add=[self.init0, self.init1, self.init2, self.init3, self.init4],
            active_approvals_to_remove=[],
            key_approvals_to_add=[],
            key_approvals_to_remove=[],
            signer=[INIT0_PK, INIT1_PK, INIT2_PK, INIT3_PK, INIT4_PK]
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=True)
        self.dynamic()
        lcc.log_info("All committee member has voted")
        lcc.set_step("Waiting for maintenance and release of two blocks and check that parameters have been updated")
        self.produce_block(self.__database_api_identifier)
        self.dynamic()
        self.produce_block(self.__database_api_identifier)
        self.dynamic()
        time.sleep(60)
        self.produce_block(self.__database_api_identifier)
        self.dynamic()
        self.produce_block(self.__database_api_identifier)
        self.dynamic()
        response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
        global_properties = self.get_response(response_id)["result"]
        check_that("global", global_properties1, not_equal_to(global_properties), quiet=True)
