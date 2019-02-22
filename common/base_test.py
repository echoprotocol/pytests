# -*- coding: utf-8 -*-
import codecs
import json
import os

from websocket import create_connection

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_

from common.receiver import Receiver
from common.validation import Validator

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "..//resources")
ECHO_DEV = json.load(open(os.path.join(RESOURCES_DIR, "urls.json")))["BASE_URL"]
METHOD = json.load(open(os.path.join(RESOURCES_DIR, "echo_methods.json")))
EXPECTED = json.load(open(os.path.join(RESOURCES_DIR, "expected_data.json")))


class BaseTest(object):

    def __init__(self):
        super().__init__()
        self.__ws = create_connection(ECHO_DEV)
        self.__id = 0
        self.receiver = Receiver(self.__ws)
        self.validator = Validator()

    @staticmethod
    def get_byte_code(var):
        return json.load(open(os.path.join(RESOURCES_DIR, "echo_contracts.json")))[var]

    @staticmethod
    def get_file_attachment_path(file_name):
        return os.path.join(RESOURCES_DIR, file_name)

    def add_file_to_report(self, kind, filename, file_description, data=None):
        try:
            if kind == "file" and data is None:
                lcc.set_step("Attachment file")
                lcc.save_attachment_file(self.get_file_attachment_path(filename), file_description)
            elif kind == "image" and data is None:
                lcc.set_step("Image attachment")
                lcc.save_image_file(self.get_file_attachment_path(filename), file_description)
            elif kind == "file" and data is not None:
                lcc.set_step("Attachment file content")
                lcc.save_attachment_content(data, filename, file_description)
            elif kind == "image" and data is not None:
                lcc.set_step("Image attachment content")
                lcc.save_image_content(data, filename, file_description)
        except FileNotFoundError:
            lcc.log_error("File or image does not exist!")

    @staticmethod
    def prepare_attach_to_report(kind, filename, file_description, data):
        try:
            if kind == "file":
                lcc.set_step("Prepare attachment file")
                with lcc.prepare_attachment(filename, file_description) \
                        as file:
                    with open(file, "w") as fh:
                        fh.write(data)
            elif kind == "image":
                lcc.set_step("Prepare image attachment")
                with lcc.prepare_image_attachment(filename, file_description) \
                        as file:
                    with open(file, "w") as fh:
                        fh.write(data)
        except FileNotFoundError:
            lcc.log_error("File or image does not exist!")

    @staticmethod
    def get_request(method_name, params=None):
        # Params must be list
        request = [1, method_name]
        if params is None:
            request.extend([METHOD[method_name]])
            return request
        request.extend([params])
        return request

    @staticmethod
    def get_expected(variable_name):
        # Return data from json file
        return EXPECTED[variable_name]

    @staticmethod
    def get_template():
        # Return call method format
        return {"id": 0, "method": "call", "params": []}

    def __call_method(self, method, api_identifier=None):
        # Returns the api method call
        self.__id += 1
        call_template = self.get_template()
        try:
            if api_identifier is None:
                call_template["id"] = self.__id
                call_template["params"] = method
                return call_template
            call_template["id"] = self.__id
            call_template["params"].append(api_identifier)
            for i in range(1, len(method)):
                call_template["params"].append(method[i])
            return call_template
        except KeyError:
            lcc.log_error("That key does not exist!")
        except IndexError:
            lcc.log_error("This index does not exist!")

    def send_request(self, request, api_identifier=None, debug_mode=False):
        # Send request to server
        if api_identifier is None:
            method = self.__call_method(request)
            self.__ws.send(json.dumps(method))
            if debug_mode:
                lcc.log_debug("Send: {}".format(method))
            return method.get("id")
        method = self.__call_method(request, api_identifier)
        self.__ws.send(json.dumps(method))
        if debug_mode:
            lcc.log_debug("Send: {}".format(method))
        return method.get("id")

    def get_response(self, id_response, is_positive=True, debug_mode=False):
        # Receive answer from server
        try:
            if debug_mode:
                lcc.log_debug("Parameters: positive={}, ".format(is_positive))
                response = json.loads(self.__ws.recv())
                lcc.log_debug("Received:\n{}".format(json.dumps(response, indent=4)))
            return self.receiver.get_response(id_response, is_positive)
        except KeyError:
            lcc.log_error("That key does not exist!")
        except IndexError:
            lcc.log_error("This index does not exist!")

    def get_notice(self, id_response, object_id=None, log_block_id=True, debug_mode=False):
        # Receive notice from server
        try:
            if debug_mode:
                lcc.log_debug("Parameters: object_id={}, log_block_id={}".format(object_id, log_block_id))
                response = json.loads(self.__ws.recv())
                lcc.log_debug("Received:\n{}".format(json.dumps(response, indent=4)))
            return self.receiver.get_notice(id_response, object_id, log_block_id)
        except KeyError:
            lcc.log_error("That key does not exist!")
        except IndexError:
            lcc.log_error("This index does not exist!")

    def get_trx_completed_response(self, id_response):
        # Receive answer from server that transaction completed
        response = self.get_response(id_response)
        check_that(
            "transaction completed",
            response.get("result")[1].get("exec_res").get("excepted"),
            is_("None")
        )
        return response

    def get_identifier(self, api, debug_mode=False):
        # Initialise identifier for api
        call_template = self.get_template()
        call_template["params"] = [1, api, []]
        self.__ws.send(json.dumps(call_template))
        response = json.loads(self.__ws.recv())
        api_identifier = response["result"]
        if debug_mode:
            lcc.log_debug("Api identifier is '{}'".format(api_identifier))
        return api_identifier

    def get_contract_result(self, response, debug_mode=False):
        contract_performance_result = str((response.get("operation_results"))[0][-1])
        if debug_mode:
            lcc.log_debug("Contract performance result is {}".format(contract_performance_result))
        if self.validator.is_contract_result_id(contract_performance_result):
            return contract_performance_result
        return lcc.log_error("Wrong format of contract result, got {}".format(contract_performance_result))

    def get_contract_id(self, response, debug_mode=False):
        contract_identifier_hex = response["result"][1].get("exec_res").get("new_address")
        contract_id = "1.16.{}".format(int(str(contract_identifier_hex)[2:], 16))
        if debug_mode:
            lcc.log_debug("Contract identifier is {}".format(contract_id))
        if self.validator.is_contract_id(contract_id):
            return contract_id
        return lcc.log_error("Wrong format of contract id, got {}".format(contract_id))

    @staticmethod
    def get_contract_output(response, in_hex=False):
        if in_hex:
            contract_output = str(response["result"][1].get("exec_res").get("output"))
            return contract_output
        contract_output = str(
            codecs.decode(str(response["result"][1].get("exec_res").get("output")), "hex").decode('utf-8'))
        return contract_output.replace("\u0000", "").replace("\u000e", "")

    @staticmethod
    def _login_status(response):
        # Check authorization status
        try:
            if not response["result"]:
                lcc.log_error("Login failed!")
            lcc.log_info("Login successful")
        except KeyError:
            lcc.log_error("This key does not exist!")

    def __login_echo(self):
        # Login to Echo
        lcc.set_step("Login to Echo")
        response_id = self.send_request(self.get_request("login"))
        response = self.get_response(response_id)
        self._login_status(response)

    def setup_suite(self):
        # Check status of connection
        lcc.set_step("Open connection")
        if self.__ws is None:
            lcc.log_error("Connection not established")
        lcc.log_url(ECHO_DEV)
        lcc.log_info("Connection successfully created")
        self.__login_echo()

    def teardown_suite(self):
        # Close connection to WebSocket
        lcc.set_step("Close connection")
        connection = self.__ws.close()
        if connection is not None:
            lcc.log_error("Connection not closed")
        lcc.log_info("Connection closed")
