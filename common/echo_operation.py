import json
import os

import lemoncheesecake.api as lcc

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "..//resources")
OPERATIONS = json.load(open(os.path.join(RESOURCES_DIR, "echo_operations.json")))
PRIVATE_KEY = json.load(open(os.path.join(RESOURCES_DIR, "wallet.json")))["PRIVATE_KEY"]


class EchoOperations(object):

    def __init__(self):
        super().__init__()
        self.list_operations = []

    @staticmethod
    def get_operation_json(variable_name, example=False):
        # Return needed operation template from json file
        if example:
            return OPERATIONS[variable_name]
        return OPERATIONS[variable_name][1]

    def get_transfer_operation(self, echo, from_account_id, to_account_id, amount=1, fee_amount=0, fee_asset_id="1.3.0",
                               amount_asset_id="1.3.0", with_memo=False, from_memo="", to_memo="", nonce_memo="",
                               message="", debug_mode=False):
        operation_id = echo.config.operation_ids.TRANSFER
        if with_memo:
            transfer_props = self.get_operation_json("transfer_operation_with_memo").copy()
            transfer_props["memo"].update({"from": from_memo, "to": to_memo, "nonce": nonce_memo, "message": message})
        else:
            transfer_props = self.get_operation_json("transfer_operation").copy()
        transfer_props["fee"].update({"amount": fee_amount, "asset_id": fee_asset_id})
        transfer_props.update({"from": from_account_id, "to": to_account_id})
        transfer_props["amount"].update({"amount": amount, "asset_id": amount_asset_id})
        if debug_mode:
            lcc.log_debug("Transfer operation: \n{}".format(json.dumps(transfer_props, indent=4)))
        return [operation_id, transfer_props]

    def get_create_contract_operation(self, echo, registrar, bytecode, fee_amount=0, fee_asset_id="1.3.0",
                                      value_amount=0, value_asset_id="1.3.0", supported_asset_id="1.3.0",
                                      eth_accuracy=False, debug_mode=False):
        operation_id = echo.config.operation_ids.CREATE_CONTRACT
        transfer_props = self.get_operation_json("create_contract_operation").copy()
        transfer_props["fee"].update({"amount": fee_amount, "asset_id": fee_asset_id})
        transfer_props.update({"registrar": registrar, "code": bytecode, "supported_asset_id": supported_asset_id,
                               "eth_accuracy": eth_accuracy})
        transfer_props["value"].update({"amount": value_amount, "asset_id": value_asset_id})
        if debug_mode:
            lcc.log_debug(
                "Create contract operation: \n{}".format(json.dumps([operation_id, transfer_props], indent=4)))
        return [operation_id, transfer_props]

    def get_call_contract_operation(self, echo, registrar, bytecode, callee, fee_amount=0, fee_asset_id="1.3.0",
                                    value_amount=0, value_asset_id="1.3.0", debug_mode=False):
        operation_id = echo.config.operation_ids.CALL_CONTRACT

        transfer_props = self.get_operation_json("call_contract_operation").copy()
        transfer_props["fee"].update({"amount": fee_amount, "asset_id": fee_asset_id})
        transfer_props.update({"registrar": registrar, "code": bytecode, "callee": callee})
        transfer_props["value"].update({"amount": value_amount, "asset_id": value_asset_id})
        if debug_mode:
            lcc.log_debug("Call contract operation: \n{}".format(json.dumps(transfer_props, indent=4)))
        return [operation_id, transfer_props]

    @staticmethod
    def broadcast(echo, list_operations, log_broadcast=True):
        tx = echo.create_transaction()
        if type(list_operations[0]) is int:
            list_operations = [list_operations]
        for i in range(len(list_operations)):
            tx.add_operation(name=list_operations[i][0], props=list_operations[i][1])
        tx.add_signer(PRIVATE_KEY)
        tx.sign()
        broadcast_result = tx.broadcast()
        if log_broadcast:
            lcc.log_info("Broadcast result: \n{}".format(json.dumps(broadcast_result, indent=4)))
        return broadcast_result
