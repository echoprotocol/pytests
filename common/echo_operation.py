import json
import os

import lemoncheesecake.api as lcc

from common.validation import Validator

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "..//resources")
OPERATIONS = json.load(open(os.path.join(RESOURCES_DIR, "echo_operations.json")))
WALLETS = os.path.join(RESOURCES_DIR, "wallets.json")


class EchoOperations(object):

    def __init__(self):
        super().__init__()
        self.validator = Validator()

    def get_signer(self, name_or_id):
        wallets = json.load(open(WALLETS))
        if self.validator.is_account_name(name_or_id):
            return wallets[name_or_id]["private_key"]
        if self.validator.is_account_id(name_or_id):
            wallets_keys = list(wallets.keys())
            for key in range(len(wallets_keys)):
                if wallets[wallets_keys[key]]["id"] == name_or_id:
                    return wallets[wallets_keys[key]]["private_key"]
        lcc.log_error("Try to get invalid signer, get: '{}'".format(name_or_id))
        raise Exception("Try to get invalid signer")

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
        return [operation_id, transfer_props, from_account_id]

    def get_create_contract_operation(self, echo, registrar, bytecode, fee_amount=0, fee_asset_id="1.3.0",
                                      value_amount=0, value_asset_id="1.3.0", supported_asset_id="1.3.0",
                                      eth_accuracy=False, debug_mode=False):
        operation_id = echo.config.operation_ids.CREATE_CONTRACT
        create_contract_props = self.get_operation_json("create_contract_operation").copy()
        create_contract_props["fee"].update({"amount": fee_amount, "asset_id": fee_asset_id})
        create_contract_props.update(
            {"registrar": registrar, "code": bytecode, "supported_asset_id": supported_asset_id,
             "eth_accuracy": eth_accuracy})
        create_contract_props["value"].update({"amount": value_amount, "asset_id": value_asset_id})
        if debug_mode:
            lcc.log_debug(
                "Create contract operation: \n{}".format(json.dumps([operation_id, create_contract_props], indent=4)))
        return [operation_id, create_contract_props, registrar]

    def get_call_contract_operation(self, echo, registrar, bytecode, callee, fee_amount=0, fee_asset_id="1.3.0",
                                    value_amount=0, value_asset_id="1.3.0", debug_mode=False):
        operation_id = echo.config.operation_ids.CALL_CONTRACT

        call_contract_props = self.get_operation_json("call_contract_operation").copy()
        call_contract_props["fee"].update({"amount": fee_amount, "asset_id": fee_asset_id})
        call_contract_props.update({"registrar": registrar, "code": bytecode, "callee": callee})
        call_contract_props["value"].update({"amount": value_amount, "asset_id": value_asset_id})
        if debug_mode:
            lcc.log_debug("Call contract operation: \n{}".format(json.dumps(call_contract_props, indent=4)))
        return [operation_id, call_contract_props, registrar]

    def broadcast(self, echo, list_operations, log_broadcast=True):
        tx = echo.create_transaction()
        if type(list_operations[0]) is int:
            list_operations = [list_operations]
        for i in range(len(list_operations)):
            tx.add_operation(name=list_operations[i][0], props=list_operations[i][1])
        for i in range(len(list_operations)):
            tx.add_signer(self.get_signer(list_operations[i][2]))
        tx.sign()
        broadcast_result = tx.broadcast()
        if log_broadcast:
            lcc.log_info("Broadcast result: \n{}".format(json.dumps(broadcast_result, indent=4)))
        return broadcast_result
