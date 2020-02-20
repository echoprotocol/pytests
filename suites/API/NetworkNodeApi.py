# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_integer, require_that, \
    check_that_in, equal_to, is_true, has_length, is_none, is_list

from common.base_test import BaseTest
from common.receiver import Receiver

SUITE = {
    "description": "Network Node Api "
}


@lcc.prop("main", "type")
@lcc.tags("api", "network_node_api")
@lcc.suite("Network Node API")
class NetworkNodeApi(BaseTest):

    @lcc.tags("connection_to_network_node_api", "connection_to_apis")
    @lcc.test("Check connection to NetworkNodeApi")
    def connection_to_network_node_api(self):
        self.endpoint = "0.0.0.0:6310"
        self.ws = self.create_connection_to_echo()
        self.receiver = Receiver(web_socket=self.ws)
        lcc.set_step("Requesting Access to a History API")
        self.api_identifier = self.get_identifier("network_node")
        check_that("'network node api identifier'", self.api_identifier, is_integer())

        lcc.set_step("Check network node api identifier. Call network node api method 'get_info'")
        response_id = self.send_request(self.get_request("get_info", []), self.api_identifier)
        response = self.get_response(response_id)

        if require_that("'call method 'get_info''", response["result"], has_length(6), quiet=True):
            check_that_in(
                response["result"],
                "listening_on", equal_to(self.endpoint),
                "accept_incoming_connections", is_true(),
                "node_public_key", equal_to("02226199775521ceba2d7ad6719ac1d06179ee2e795e4cf747d717c60e83244cd2"),
                "node_id", equal_to("aec011d480e9cee3b69346a40039f4040d938336d909d94c28a27700af2513a703"),
                "firewalled", equal_to("unknown"),
                "connection_count", equal_to(0),
                quiet=True
            )

    @lcc.test("Check method 'add_node'")
    @lcc.depends_on("API.NetworkNodeApi.NetworkNodeApi.connection_to_network_node_api")
    def add_node(self):
        response_id = self.send_request(self.get_request("add_node", ["0.0.0.0:6310"]), self.api_identifier)
        response = self.get_response(response_id)
        check_that(
            "'call method 'add_node''",
            response["result"], is_none(), quiet=True
        )

    @lcc.test("Check method 'get_connected_peers'")
    @lcc.depends_on("API.NetworkNodeApi.NetworkNodeApi.connection_to_network_node_api")
    def get_connected_peers(self):
        response_id = self.send_request(self.get_request("get_connected_peers", []), self.api_identifier)
        response = self.get_response(response_id)
        check_that(
            "'call method 'add_node''",
            response["result"], is_list(), quiet=True
        )

    @lcc.test("Check method 'get_potential_peers'")
    @lcc.depends_on("API.NetworkNodeApi.NetworkNodeApi.connection_to_network_node_api")
    def get_potential_peers(self):
        response_id = self.send_request(self.get_request("get_potential_peers", []), self.api_identifier)
        result = self.get_response(response_id)["result"][0]
        if require_that("'call method 'get_potential_peers''", result, has_length(6), quiet=True):
            check_that_in(
                result,
                "endpoint", equal_to(self.endpoint),
                "last_connection_disposition", equal_to("last_connection_handshaking_failed"),
                "number_of_successful_connection_attempts", is_integer(),
                "number_of_failed_connection_attempts", is_integer(),
                quiet=True
            )
            if not self.type_validator.is_iso8601(result["last_seen_time"]):
                lcc.log_error(
                    "Wrong format of 'last_seen_time', got: {}".format(result["last_seen_time"]))
            else:
                lcc.log_info("'last_seen_time' has correct format: iso8601")
            if not self.type_validator.is_iso8601(result["last_connection_attempt_time"]):
                lcc.log_error(
                    "Wrong format of 'last_connection_attempt_time', got: {}".format(
                        result["last_connection_attempt_time"]))
            else:
                lcc.log_info("'last_connection_attempt_time' has correct format: iso8601")

    @lcc.test("Check method 'get_advanced_node_parameters'")
    @lcc.depends_on("API.NetworkNodeApi.NetworkNodeApi.connection_to_network_node_api")
    def get_advanced_node_parameters(self):
        response_id = self.send_request(self.get_request("get_advanced_node_parameters", []), self.api_identifier)
        result = self.get_response(response_id)["result"]
        if require_that("'call method 'get_advanced_node_parameters''", result, has_length(6), quiet=True):
            check_that_in(
                result,
                "peer_connection_retry_timeout", is_integer(),
                "desired_number_of_connections", is_integer(),
                "maximum_number_of_connections", is_integer(),
                "maximum_number_of_blocks_to_handle_at_one_time", is_integer(),
                "maximum_number_of_sync_blocks_to_prefetch", is_integer(),
                "maximum_blocks_per_peer_during_syncing", is_integer(),
                quiet=True
            )

    @lcc.test("Check method 'set_advanced_node_parameters'")
    @lcc.depends_on("API.NetworkNodeApi.NetworkNodeApi.connection_to_network_node_api")
    def set_advanced_node_parameters(self):
        params = {"maximum_number_of_connections": 50}
        response_id = self.send_request(self.get_request("set_advanced_node_parameters", [params]), self.api_identifier)
        result = self.get_response(response_id)["result"]
        check_that(
            "'call method 'add_node''",
            result, is_none(), quiet=True
        )





