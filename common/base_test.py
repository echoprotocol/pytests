# -*- coding: utf-8 -*-
import json
import os

from websocket import create_connection

import lemoncheesecake.api as lcc

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "..//resources")
ECHO_DEV = json.load(open(os.path.join(RESOURCES_DIR, "urls.json")))["BASE_URL"]
METHOD = json.load(open(os.path.join(RESOURCES_DIR, "echo_methods.json")))
EXPECTED = json.load(open(os.path.join(RESOURCES_DIR, "expected_data.json")))


class BaseTest(object):
    _login_api = "login"
    _database_api = "database"
    _asset_api = "asset"
    _history_api = "history"
    _network_broadcast_api = "network_broadcast"
    _crypto_api = "crypto"
    _registration_api = "registration"

    def __init__(self):
        self.__ws = create_connection(ECHO_DEV)
        self.__resp = None
        self.__request = None
        self.__api_id = 0

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

    def get_request(self, method_name, params=None):
        # Params must be list
        self.__request = [1, method_name]
        if params is None:
            self.__request.extend([METHOD[method_name]])
            return self.__request
        else:
            self.__request.extend([params])
            return self.__request

    @staticmethod
    def get_expected(variable_name):
        # Return data from json file
        return EXPECTED[variable_name]

    @staticmethod
    def get_template():
        # Return call method format
        return {"id": 0, "method": "call", "params": []}

    def __call_method(self, method, call_back=None):
        # Returns the api method call
        self.__api_id += 1
        call_template = self.get_template()
        try:
            if call_back is None:
                call_template["id"] = self.__api_id
                call_template["params"] = method
                return call_template
            else:
                call_template["id"] = self.__api_id
                call_template["params"].append(call_back)
                for i in range(1, len(method)):
                    try:
                        call_template["params"].append(method[i])
                    except IndexError:
                        lcc.log_error("This index does not exist!")
                return call_template
        except KeyError:
            lcc.log_error("That key does not exist!")

    def send_request(self, request, call_back=None):
        # Send request to server
        if call_back is None:
            self.__ws.send(json.dumps(self.__call_method(request)))
            return self.__ws
        else:
            self.__ws.send(json.dumps(self.__call_method(request, call_back)))
            return self.__ws

    def get_response(self):
        # Receive answer from server
        self.__resp = json.loads(self.__ws.recv())
        lcc.log_info("Received: \n{}".format(json.dumps(self.__resp, indent=4)))
        return self.__resp

    def get_identifier(self, api):
        # Initialise identifier for api
        call_template = self.get_template()
        call_template["params"] = [1, api, []]
        self.__ws.send(json.dumps(call_template))
        self.__resp = json.loads(self.__ws.recv())
        identifier = self.__resp["result"]
        return identifier

    @staticmethod
    def _login_status(response):
        # Check authorization status
        try:
            if response["result"]:
                lcc.log_info("Login successful")
            else:
                lcc.log_info("Login failed")
        except KeyError:
            lcc.log_error("Login failed")

    def __login_echo(self):
        # Login to Echo
        lcc.set_step("Login to Echo")
        self.send_request(self.get_request(self._login_api))
        self.__resp = self.get_response()
        self._login_status(self.__resp)

    def setup_suite(self):
        # Check status of connection
        lcc.set_step("Open connection")
        if self.__ws is not None:
            lcc.log_url(ECHO_DEV)
            lcc.log_info("Connection successfully created")
            self.__login_echo()
        else:
            lcc.log_error("Connection not established")

    def teardown_suite(self):
        # Close connection to WebSocket
        lcc.set_step("Close connection")
        self.__ws.close()
        lcc.log_info("Connection closed")
