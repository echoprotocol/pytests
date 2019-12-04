# -*- coding: utf-8 -*-
import datetime
import math
import random
import time
from copy import deepcopy

import lemoncheesecake.api as lcc

from fixtures.base_fixtures import get_random_valid_asset_name
from project import GENESIS, BLOCKS_NUM_TO_WAIT


class Utils(object):

    def __init__(self):
        super().__init__()
        self.waiting_time_result = 0

    @staticmethod
    def add_balance_for_operations(base_test, account, operation, database_api_id, deposit_amount=0, operation_count=1,
                                   transfer_amount=0, only_in_history=False, get_only_fee=False, log_broadcast=False):
        if only_in_history:
            transfer_amount = operation_count * transfer_amount
        if get_only_fee:
            transfer_amount = 0
        fee_amount = base_test.get_required_fee(operation, database_api_id)["amount"]
        if type(fee_amount) is str:
            fee_amount = int(fee_amount)
        amount = operation_count * fee_amount + transfer_amount + deposit_amount
        transfer_amount_for_pay_fee_op = base_test.echo_ops.get_transfer_operation(echo=base_test.echo,
                                                                                   from_account_id=base_test.echo_acc0,
                                                                                   to_account_id=account, amount=amount)
        collected_operation = base_test.collect_operations(transfer_amount_for_pay_fee_op, database_api_id)
        return base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                            log_broadcast=log_broadcast)

    def get_nonexistent_asset_id(self, base_test, database_api_id, symbol="", list_asset_ids=None, return_symbol=False):
        if list_asset_ids is None:
            list_asset_ids = []
        max_limit = 100
        response_id = base_test.send_request(base_test.get_request("list_assets", [symbol, max_limit]), database_api_id)
        response = base_test.get_response(response_id)
        for asset in response["result"]:
            list_asset_ids.append(asset["id"])
        if len(response["result"]) == max_limit:
            return self.get_nonexistent_asset_id(base_test, database_api_id, symbol=list_asset_ids[-1],
                                                 list_asset_ids=list_asset_ids, return_symbol=return_symbol)
        sorted_list_asset_ids = sorted(list_asset_ids, key=base_test.get_value_for_sorting_func)
        asset_id = "{}{}".format(base_test.get_object_type(base_test.echo.config.object_types.ASSET),
                                 str(int(sorted_list_asset_ids[-1][4:]) + 1))
        if return_symbol:
            return asset_id, symbol
        return asset_id

    def get_nonexistent_asset_symbol(self, base_test, database_api_id, symbol="", list_asset_symbols=None):
        if list_asset_symbols is None:
            list_asset_symbols = []
        max_limit = 100
        response_id = base_test.send_request(base_test.get_request("list_assets", [symbol, max_limit]), database_api_id)
        response = base_test.get_response(response_id)
        for asset in response["result"]:
            list_asset_symbols.append(asset["symbol"])
        if len(response["result"]) == max_limit:
            return self.get_nonexistent_asset_symbol(base_test, database_api_id, symbol=list_asset_symbols[-1],
                                                     list_asset_symbols=list_asset_symbols)
        nonexistent_asset_symbol = list_asset_symbols[0]
        while nonexistent_asset_symbol in list_asset_symbols:
            nonexistent_asset_symbol = get_random_valid_asset_name()
        return nonexistent_asset_symbol

    def get_nonexistent_account_name(self, base_test, database_api_id, lower_bound_name="", list_account_names=None,
                                     committee_member=False):
        if list_account_names is None:
            list_account_names = []
        method_name = "lookup_accounts" if not committee_member else "lookup_committee_member_accounts"
        max_limit = 1000
        response_id = base_test.send_request(base_test.get_request(method_name, [lower_bound_name, max_limit]),
                                             database_api_id)
        response = base_test.get_response(response_id)
        for account in response["result"]:
            list_account_names.append(account[0])
        if len(response["result"]) == max_limit:
            return self.get_nonexistent_account_name(base_test, database_api_id,
                                                     lower_bound_name=list_account_names[-1],
                                                     list_account_names=list_account_names)
        account_names_count = len(list_account_names)
        result_lower_bound_name = list_account_names[len(list_account_names) // max_limit * max_limit] \
            if account_names_count > 1000 else lower_bound_name
        result_limit = account_names_count % max_limit + 1 if account_names_count > 1000 \
            else account_names_count + 1
        return result_lower_bound_name, result_limit

    @staticmethod
    def get_nonexistent_committee_member_id(base_test, database_api_id):
        response_id = base_test.send_request(base_test.get_request("get_committee_count"), database_api_id)
        committee_count = base_test.get_response(response_id)["result"]
        return "{}{}".format(base_test.get_object_type(base_test.echo.config.object_types.COMMITTEE_MEMBER),
                             committee_count)

    @staticmethod
    def get_nonexistent_vote_id(base_test, database_api_id):
        response_id = base_test.send_request(base_test.get_request("get_global_properties"), database_api_id)
        next_available_vote_id = base_test.get_response(response_id)["result"]["next_available_vote_id"]
        return "0:{}".format(next_available_vote_id)

    def get_contract_id(self, base_test, registrar, contract_bytecode, database_api_id, value_amount=0,
                        value_asset_id="1.3.0", supported_asset_id=None, eth_accuracy=False, get_only_fee=False,
                        need_broadcast_result=False, log_broadcast=False):
        operation = base_test.echo_ops.get_contract_create_operation(echo=base_test.echo, registrar=registrar,
                                                                     bytecode=contract_bytecode,
                                                                     value_amount=value_amount,
                                                                     value_asset_id=value_asset_id,
                                                                     supported_asset_id=supported_asset_id,
                                                                     eth_accuracy=eth_accuracy)
        if registrar != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            temp_operation[1]["registrar"] = base_test.echo_acc0
            broadcast_result = self.add_balance_for_operations(base_test, registrar, temp_operation, database_api_id,
                                                               transfer_amount=value_amount,
                                                               get_only_fee=get_only_fee,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        contract_result = base_test.get_operation_results_ids(broadcast_result)
        response_id = base_test.send_request(base_test.get_request("get_contract_result", [contract_result]),
                                             database_api_id)
        contract_id_16 = base_test.get_trx_completed_response(response_id)
        if not need_broadcast_result:
            return base_test.get_contract_id(contract_id_16)
        return {"contract_id": base_test.get_contract_id(contract_id_16), "broadcast_result": broadcast_result}

    def perform_contract_call_operation(self, base_test, registrar, method_bytecode, database_api_id,
                                        contract_id, operation_count=1, get_only_fee=False, log_broadcast=False):
        operation = base_test.echo_ops.get_contract_call_operation(echo=base_test.echo, registrar=registrar,
                                                                   bytecode=method_bytecode, callee=contract_id)
        if registrar != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, registrar, temp_operation, database_api_id,
                                                               operation_count=operation_count,
                                                               get_only_fee=get_only_fee,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        if operation_count == 1:
            broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                            log_broadcast=log_broadcast)
            return broadcast_result
        list_operations = []
        for i in range(operation_count):
            list_operations.append(collected_operation)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=list_operations,
                                                        log_broadcast=log_broadcast)
        return broadcast_result

    def perform_transfer_operations(self, base_test, account_1, account_2, database_api_id, transfer_amount=1,
                                    operation_count=1, only_in_history=False, amount_asset_id="1.3.0",
                                    get_only_fee=False, log_broadcast=False, broadcast_with_callback=False):
        add_balance_operation = 0
        operation = base_test.echo_ops.get_transfer_operation(echo=base_test.echo, from_account_id=account_1,
                                                              to_account_id=account_2, amount=transfer_amount,
                                                              amount_asset_id=amount_asset_id)
        if account_1 != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            temp_operation[1]["from_account_id"] = base_test.echo_acc0
            broadcast_result = self.add_balance_for_operations(base_test, account_1, temp_operation, database_api_id,
                                                               transfer_amount=transfer_amount,
                                                               operation_count=operation_count,
                                                               only_in_history=only_in_history,
                                                               get_only_fee=get_only_fee,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
            add_balance_operation = 1
        collected_operation = base_test.collect_operations(operation, database_api_id)
        if operation_count == 1:
            broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                            log_broadcast=log_broadcast,
                                                            broadcast_with_callback=broadcast_with_callback)
            return broadcast_result
        list_operations = []
        for i in range(operation_count - add_balance_operation):
            list_operations.append(collected_operation)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=list_operations,
                                                        log_broadcast=log_broadcast,
                                                        broadcast_with_callback=broadcast_with_callback)
        return broadcast_result

    def perform_transfer_to_address_operations(self, base_test, account_1, to_address, database_api_id,
                                               transfer_amount=1, amount_asset_id="1.3.0", operation_count=1,
                                               get_only_fee=False, log_broadcast=False):
        operation = base_test.echo_ops.get_transfer_to_address_operation(echo=base_test.echo, from_account_id=account_1,
                                                                         to_address=to_address, amount=transfer_amount,
                                                                         amount_asset_id=amount_asset_id)
        if account_1 != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            temp_operation[1]["from_account_id"] = base_test.echo_acc0
            broadcast_result = self.add_balance_for_operations(base_test, account_1, temp_operation, database_api_id,
                                                               transfer_amount=transfer_amount,
                                                               operation_count=operation_count,
                                                               get_only_fee=get_only_fee,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        if operation_count == 1:
            broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                            log_broadcast=log_broadcast)
            return broadcast_result
        list_operations = []
        for i in range(operation_count):
            list_operations.append(collected_operation)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=list_operations,
                                                        log_broadcast=log_broadcast)
        return broadcast_result

    @staticmethod
    def check_accounts_have_initial_balances(accounts):
        initial_accounts = {account["name"]: account["echorand_key"] for account in GENESIS["initial_accounts"]
                            if account["name"] in accounts}
        initial_balances_keys = [balance["owner"] for balance in GENESIS["initial_balances"]]
        initial_balances_keys = list(filter(lambda balance: balance in initial_accounts.values(),
                                            initial_balances_keys))
        if len(initial_balances_keys) < len(accounts):
            return False
        return True

    @staticmethod
    def get_account_id(base_test, account_names, account_keys, database_api_id, signer=None,
                       need_operations=False, log_broadcast=False):
        if signer is None:
            signer = base_test.echo_acc0
        if type(account_names) is str:
            operation = base_test.echo_ops.get_account_create_operation(echo=base_test.echo, name=account_names,
                                                                        active_key_auths=account_keys[1],
                                                                        echorand_key=account_keys[1],
                                                                        registrar=signer, signer=signer)
            collected_operation = base_test.collect_operations(operation, database_api_id)
            broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                            log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=1):
                raise Exception("Default accounts are not created")
            account_id = base_test.get_operation_results_ids(broadcast_result)
            if need_operations:
                return {"account_id": account_id, "operation": collected_operation}
            return account_id
        list_operations = []
        for i, account_name in enumerate(account_names):
            operation = base_test.echo_ops.get_account_create_operation(echo=base_test.echo, name=account_name,
                                                                        active_key_auths=account_keys[i][1],
                                                                        echorand_key=account_keys[i][1],
                                                                        registrar=signer, signer=signer)
            collected_operation = base_test.collect_operations(operation, database_api_id)
            list_operations.append(collected_operation)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=list_operations,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception("Default accounts are not created")
        operation_results = base_test.get_operation_results_ids(broadcast_result)
        accounts_ids = []
        for operation_result in operation_results:
            accounts_ids.append(operation_result[1])
        if need_operations:
            return {"accounts_ids": accounts_ids, "account_names": account_names, "list_operations": list_operations}
        return accounts_ids

    @staticmethod
    def get_asset_id(base_test, symbol, database_api_id, need_operation=False, log_broadcast=False):
        params = [symbol, 1]
        response_id = base_test.send_request(base_test.get_request("list_assets", params), database_api_id, )
        response = base_test.get_response(response_id)
        if not response["result"] or response["result"][0]["symbol"] != symbol:
            operation = base_test.echo_ops.get_asset_create_operation(echo=base_test.echo, issuer=base_test.echo_acc0,
                                                                      symbol=symbol)
            collected_operation = base_test.collect_operations(operation, database_api_id)
            broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                            log_broadcast=log_broadcast)
            asset_id = base_test.get_operation_results_ids(broadcast_result)
            if need_operation:
                return asset_id, collected_operation
            return asset_id
        return response["result"][0]["id"]

    @staticmethod
    def add_assets_to_account(base_test, value, asset_id, to_account, database_api_id, log_broadcast=False):
        operation = base_test.echo_ops.get_asset_issue_operation(echo=base_test.echo, issuer=base_test.echo_acc0,
                                                                 value_amount=value, value_asset_id=asset_id,
                                                                 issue_to_account=to_account)
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception(
                "Error: new asset holder '{}' not added, response:\n{}".format(to_account, broadcast_result))
        return broadcast_result

    def perform_account_address_create_operation(self, base_test, registrar, label, database_api_id,
                                                 operation_count=1, log_broadcast=False):
        operation = base_test.echo_ops.get_account_address_create_operation(echo=base_test.echo, owner=registrar,
                                                                            label=label)
        if registrar != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, registrar, temp_operation, database_api_id,
                                                               operation_count=operation_count,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        if operation_count == 1:
            broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                            log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=1):
                raise Exception("Error: new address of '{}' account is not created, "
                                "response:\n{}".format(registrar, broadcast_result))
            return broadcast_result
        list_operations = []
        for i in range(operation_count):
            list_operations.append(collected_operation)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=list_operations,
                                                        log_broadcast=log_broadcast)
        return broadcast_result

    @staticmethod
    def perform_sidechain_eth_create_address_operation(base_test, registrar, database_api_id, log_broadcast=False):
        operation = base_test.echo_ops.get_sidechain_eth_create_address_operation(echo=base_test.echo,
                                                                                  account=registrar)
        # todo: uncomment if fee != 0
        # if registrar != base_test.echo_acc0:
        #     temp_operation = deepcopy(operation)
        #     broadcast_result = base_test.utils.add_balance_for_operations(base_test, registrar, temp_operation,
        #                                                             database_api_id, log_broadcast=log_broadcast)
        #     if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
        #         raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception(
                "Error: new eth address of '{}' account is not created, response:\n{}".format(registrar,
                                                                                              broadcast_result))
        return broadcast_result

    @staticmethod
    def perform_sidechain_eth_withdraw_operation(base_test, registrar, eth_addr, value, database_api_id,
                                                 log_broadcast=False):
        if eth_addr[:2] == "0x":
            eth_addr = eth_addr[2:]
        operation = base_test.echo_ops.get_sidechain_eth_withdraw_operation(echo=base_test.echo, account=registrar,
                                                                            eth_addr=eth_addr, value=value)
        # todo: uncomment if fee != 0
        # if registrar != base_test.echo_acc0:
        #     temp_operation = deepcopy(operation)
        #     broadcast_result = base_test.utils.add_balance_for_operations(base_test, registrar, temp_operation,
        #                                                                   database_api_id,log_broadcast=log_broadcast)
        #     if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
        #         raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception(
                "Error: withdraw ethereum from '{}' account is not performed, response:\n{}".format(registrar,
                                                                                                    broadcast_result))
        return broadcast_result

    @staticmethod
    def cancel_all_subscriptions(base_test, database_api_id):
        response_id = base_test.send_request(base_test.get_request("cancel_all_subscriptions"), database_api_id)
        response = base_test.get_response(response_id)
        if "result" not in response or response["result"] is not None:
            raise Exception("Can't cancel all cancel_all_subscriptions, got:\n{}".format(str(response)))

    def set_timeout_until_num_blocks_released(self, base_test, database_api_id, wait_block_count=1, print_log=True):
        self.waiting_time_result = base_test.convert_time_in_seconds(base_test.get_time())
        callback, current_block = random.randrange(100), None
        response_id = base_test.send_request(base_test.get_request("set_block_applied_callback", [callback]),
                                             database_api_id)
        response = base_test.get_response(response_id)
        if "result" not in response or response["result"] is not None:
            raise Exception("Can't subscribe to release of blocks, got:\n{}".format(response))
        for block_count in range(wait_block_count):
            new_block = base_test.get_notice(callback, log_response=False)
            if not current_block != new_block:
                raise Exception("Released blocks have the same hash")
            current_block = new_block
        self.waiting_time_result = base_test.convert_time_in_seconds(base_test.get_time()) - self.waiting_time_result
        if print_log:
            lcc.log_info("Waited for release of '{}' block(s). Wait time: '{}' seconds"
                         "".format(wait_block_count, self.waiting_time_result))
        self.cancel_all_subscriptions(base_test, database_api_id)
        return self.waiting_time_result

    def get_eth_address(self, base_test, account_id, database_api_id, wait_time=0, temp_count=0):
        response_id = base_test.send_request(base_test.get_request("get_eth_address", [account_id]), database_api_id)
        response = base_test.get_response(response_id)
        if "result" in response and response["result"]:
            lcc.log_info("Waited for release of '{}' block(s). Wait time: '{}' seconds".format(temp_count, wait_time))
            return response
        temp_count += 1
        if temp_count <= BLOCKS_NUM_TO_WAIT:
            import time
            time.sleep(1)
            return self.get_eth_address(base_test, account_id, database_api_id, wait_time, temp_count=temp_count)
        raise Exception(
            "No ethereum address of '{}' account. Waiting time result='{}'".format(account_id, wait_time))

    @staticmethod
    def get_account_balances(base_test, account, database_api_id, assets=None):
        if assets is None:
            assets = [base_test.echo_asset]
        elif base_test.validator.is_asset_id(assets):
            assets = [assets]
        params = [account, assets]
        response_id = base_test.send_request(base_test.get_request("get_account_balances", params), database_api_id)
        if len(assets) == 1:
            return base_test.get_response(response_id)["result"][0]
        return base_test.get_response(response_id)["result"]

    def get_eth_balance(self, base_test, account_id, database_api_id, previous_balance=None, wait_time=0, temp_count=0):
        current_balance = self.get_account_balances(base_test, account_id, database_api_id, base_test.eth_asset)[
            "amount"]
        if previous_balance is None and current_balance != 0:
            lcc.log_info("Waited for release of '{}' block(s). Wait time: '{}' seconds".format(temp_count, wait_time))
            return current_balance
        if previous_balance and previous_balance != current_balance:
            lcc.log_info("Waited for release of '{}' block(s). Wait time: '{}' seconds".format(temp_count, wait_time))
            return current_balance
        temp_count += 1
        if temp_count <= BLOCKS_NUM_TO_WAIT:
            wait_time += self.set_timeout_until_num_blocks_released(base_test, database_api_id, print_log=False)
            return self.get_eth_balance(base_test, account_id, database_api_id, previous_balance=previous_balance,
                                        wait_time=wait_time, temp_count=temp_count)
        if previous_balance:
            raise Exception(
                "Ethereum balance of '{}' account not updated. Waited for release of '{}' block(s). Wait time: '{}' "
                "seconds".format(account_id, temp_count, wait_time))
        raise Exception(
            "Ethereum balance of '{}' account not updated. Waiting time result='{}'".format(account_id, wait_time))

    def get_updated_address_balance_in_eth_network(self, base_test, account_address, previous_balance, database_api_id,
                                                   wait_time=0, currency="ether", temp_count=0):
        current_balance = base_test.eth_trx.get_address_balance_in_eth_network(base_test.web3, account_address,
                                                                               currency=currency)
        if previous_balance != current_balance:
            lcc.log_info("Waited for release of '{}' block(s). Wait time: '{}' seconds".format(temp_count, wait_time))
            return current_balance
        temp_count += 1
        if temp_count <= BLOCKS_NUM_TO_WAIT:
            wait_time += self.set_timeout_until_num_blocks_released(base_test, database_api_id, print_log=False)
            return self.get_updated_address_balance_in_eth_network(base_test, account_address, previous_balance,
                                                                   database_api_id, wait_time, currency=currency,
                                                                   temp_count=temp_count)
        raise Exception(
            "Ethereum balance of '{}' account not updated. Waiting time result='{}'".format(account_address, wait_time))

    @staticmethod
    def convert_ethereum_to_eeth(value):
        return math.floor((value * 10 ** 6))

    @staticmethod
    def convert_eeth_to_currency(value, currency="wei"):
        if currency == "wei":
            return value * 10 ** 12
        if currency == "ether":
            return value / 10 ** 6

    def perform_vesting_balance_create_operation(self, base_test, creator, owner, amount, database_api_id,
                                                 amount_asset_id="1.3.0", begin_timestamp="1970-01-01T00:00:00",
                                                 cliff_seconds=0, duration_seconds=0, log_broadcast=False):
        operation = base_test.echo_ops.get_vesting_balance_create_operation(echo=base_test.echo, creator=creator,
                                                                            owner=owner, amount=amount,
                                                                            amount_asset_id=amount_asset_id,
                                                                            begin_timestamp=begin_timestamp,
                                                                            vesting_cliff_seconds=cliff_seconds,
                                                                            vesting_duration_seconds=duration_seconds)
        if creator != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, creator, temp_operation, database_api_id,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception(
                "Error: vesting balance of '{}' account is not withdrawn, response:\n{}".format(owner,
                                                                                                broadcast_result))
        return broadcast_result

    def perform_vesting_balance_withdraw_operation(self, base_test, vesting_balance, owner, amount, database_api_id,
                                                   amount_asset_id="1.3.0", log_broadcast=False):
        operation = base_test.echo_ops.get_vesting_balance_withdraw_operation(echo=base_test.echo,
                                                                              vesting_balance=vesting_balance,
                                                                              owner=owner, amount=amount,
                                                                              amount_asset_id=amount_asset_id)
        if owner != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, owner, temp_operation, database_api_id,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception(
                "Error: vesting balance of '{}' account is not withdrawn, response:\n{}".format(owner,
                                                                                                broadcast_result))
        return broadcast_result

    @staticmethod
    def set_datetime_variable(dt, year=0, month=0, day=0, hours=0, minutes=0, seconds=0):
        ts = time.mktime(datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S").timetuple())
        ts = ts + seconds + minutes * 60 + hours * 3600 + day * 86400 + month * 2592000 + year * 31104000
        ts = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%dT%H:%M:%S")
        return ts

    def get_account_history_operations(self, base_test, account_id, operation_id, history_api_id, database_api_id,
                                       limit, wait_time=0, start="1.6.0", stop="1.6.0", temp_count=0):
        params = [account_id, operation_id, start, stop, limit]
        response_id = base_test.send_request(base_test.get_request("get_account_history_operations", params),
                                             history_api_id)
        # todo: remove debug_mode and error block. Bug: "ECHO-1128"
        response = base_test.get_response(response_id)
        if "error" in response:
            if temp_count <= BLOCKS_NUM_TO_WAIT:
                wait_time += self.set_timeout_until_num_blocks_released(base_test, database_api_id, print_log=False)
                return self.get_account_history_operations(base_test, account_id, operation_id, history_api_id,
                                                           database_api_id, limit, wait_time, start=start,
                                                           stop=stop, temp_count=temp_count)
        if "result" in response and len(response["result"]) == limit:
            lcc.log_info("Waited for release of '{}' block(s). Wait time: '{}' seconds".format(temp_count, wait_time))
            return response
        temp_count += 1
        if temp_count <= BLOCKS_NUM_TO_WAIT:
            wait_time += self.set_timeout_until_num_blocks_released(base_test, database_api_id, print_log=False)
            return self.get_account_history_operations(base_test, account_id, operation_id, history_api_id,
                                                       database_api_id, limit, wait_time, start=start, stop=stop,
                                                       temp_count=temp_count)
        raise Exception(
            "No needed operation (id='{}') in '{}' account history. Waiting time result='{}'"
            "".format(operation_id, account_id, wait_time))

    def perform_contract_fund_pool_operation(self, base_test, sender, contract, value_amount, database_api_id,
                                             value_asset_id="1.3.0", log_broadcast=False):
        operation = base_test.echo_ops.get_contract_fund_pool_operation(echo=base_test.echo, sender=sender,
                                                                        contract=contract, value_amount=value_amount,
                                                                        value_asset_id=value_asset_id)
        if sender != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, sender, temp_operation, database_api_id,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception(
                "Error: fund pool from '{}' account is not performed, response:\n{}".format(sender, broadcast_result))
        return broadcast_result

    def perform_contract_whitelist_operation(self, base_test, sender, contract, database_api_id, add_to_whitelist=None,
                                             remove_from_whitelist=None, add_to_blacklist=None,
                                             remove_from_blacklist=None, log_broadcast=False):
        operation = base_test.echo_ops.get_contract_whitelist_operation(echo=base_test.echo, sender=sender,
                                                                        contract=contract,
                                                                        add_to_whitelist=add_to_whitelist,
                                                                        remove_from_whitelist=remove_from_whitelist,
                                                                        add_to_blacklist=add_to_blacklist,
                                                                        remove_from_blacklist=remove_from_blacklist)
        if sender != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, sender, temp_operation, database_api_id,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception(
                "Error: fund pool from '{}' account is not performed, response:\n{}".format(sender, broadcast_result))
        return broadcast_result

    def perform_committee_member_create_operation(self, base_test, account_id, eth_address, btc_public_key,
                                                  database_api_id, deposit_amount, url="", log_broadcast=False):
        operation = base_test.echo_ops.get_committee_member_create_operation(echo=base_test.echo,
                                                                             committee_member_account=account_id,
                                                                             eth_address=eth_address,
                                                                             btc_public_key=btc_public_key, url=url,
                                                                             deposit_amount=deposit_amount)
        if account_id != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, account_id, temp_operation, database_api_id,
                                                               deposit_amount, log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception(
                "Error: '{}' account did not become new committee member, response:\n{}".format(account_id,
                                                                                                broadcast_result))
        return broadcast_result

    def perform_committee_member_update_operation(self, base_test, committee_member, committee_member_account,
                                                  database_api_id, new_eth_address=None, new_btc_public_key=None,
                                                  new_url=None, log_broadcast=False):
        operation = \
            base_test.echo_ops.get_committee_member_update_operation(echo=base_test.echo,
                                                                     committee_member=committee_member,
                                                                     committee_member_account=committee_member_account,
                                                                     new_eth_address=new_eth_address,
                                                                     new_btc_public_key=new_btc_public_key,
                                                                     new_url=new_url)
        if committee_member_account != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, committee_member_account, temp_operation,
                                                               database_api_id, log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception("Error: '{}' committee member did not updated, response:\n{}"
                            "".format(committee_member_account, broadcast_result))
        return broadcast_result

    def perform_committee_member_activate_operation(self, base_test, committee_member, committee_member_account,
                                                    database_api_id, signer=None, log_broadcast=False):
        operation = \
            base_test.echo_ops.get_committee_member_activate_operation(echo=base_test.echo,
                                                                       committee_member=committee_member,
                                                                       committee_member_account=committee_member_account,
                                                                       signer=signer)
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception("Error: '{}' committee member did not activate, response:\n{}"
                            "".format(committee_member, broadcast_result))
        return broadcast_result

    def perform_account_update_operation(self, base_test, account_id, account_info, database_api_id,
                                         log_broadcast=False):
        active, echorand_key, options = account_info["active"], account_info["echorand_key"], account_info["options"]
        operation = base_test.echo_ops.get_account_update_operation(echo=base_test.echo, account=account_id,
                                                                    weight_threshold=active["weight_threshold"],
                                                                    account_auths=active["account_auths"],
                                                                    key_auths=active["key_auths"],
                                                                    echorand_key=echorand_key,
                                                                    delegating_account=options["delegating_account"])
        if account_id != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, account_id, temp_operation, database_api_id,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception(
                "Error: '{}' account did not update, response:\n{}".format(account_id, broadcast_result))
        return broadcast_result

    def perform_contract_update_operation(self, base_test, sender, contract, database_api_id, new_owner=None,
                                          log_broadcast=False):
        operation = base_test.echo_ops.get_contract_update_operation(echo=base_test.echo, sender=sender,
                                                                     contract=contract, new_owner=new_owner)
        if sender != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, sender, temp_operation, database_api_id,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))

        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception("Error: '{}' contract did not update, response:\n{}".format(contract, broadcast_result))
        return broadcast_result

    def perform_sidechain_erc20_register_token_operation(self, base_test, account, eth_addr, name, symbol,
                                                         database_api_id, decimals=0, log_broadcast=False):
        if eth_addr[:2] == "0x":
            eth_addr = eth_addr[2:]
        operation = base_test.echo_ops.get_sidechain_erc20_register_token_operation(echo=base_test.echo,
                                                                                    account=account, eth_addr=eth_addr,
                                                                                    name=name, symbol=symbol,
                                                                                    decimals=decimals)
        if account != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, account, temp_operation, database_api_id,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception("Error: ERC20 token did not register, response:\n{}".format(broadcast_result))
        return broadcast_result

    @staticmethod
    def perform_sidechain_erc20_withdraw_token_operation(base_test, account, to, erc20_token, value, database_api_id,
                                                         log_broadcast=False):
        if to[:2] == "0x":
            to = to[2:]
        operation = base_test.echo_ops.get_sidechain_erc20_withdraw_token_operation(echo=base_test.echo,
                                                                                    account=account, to=to,
                                                                                    erc20_token=erc20_token,
                                                                                    value=value)
        # todo: add when would added fee for this operation
        # if account != base_test.echo_acc0:
        #     temp_operation = deepcopy(operation)
        #     broadcast_result = self.add_balance_for_operations(base_test, account, temp_operation, database_api_id,
        #                                                        log_broadcast=log_broadcast)
        #     if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
        #         raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception("Error: ERC20 token did not withdrew, response:\n{}".format(broadcast_result))
        return broadcast_result

    def get_erc20_account_deposits(self, base_test, account_id, database_api_id, wait_time=0,
                                   previous_account_deposits=None, temp_count=0):
        response_id = base_test.send_request(base_test.get_request("get_erc20_account_deposits", [account_id]),
                                             database_api_id)
        response = base_test.get_response(response_id)
        if response["result"] and response["result"] != previous_account_deposits:
            if False not in [False for deposit in response["result"] if not deposit["is_approved"]]:
                lcc.log_info(
                    "Waited for release of '{}' block(s). Wait time: '{}' seconds".format(temp_count, wait_time))
                return response
        temp_count += 1
        if temp_count <= BLOCKS_NUM_TO_WAIT:
            wait_time += self.set_timeout_until_num_blocks_released(base_test, database_api_id, print_log=False)
            return self.get_erc20_account_deposits(base_test, account_id, database_api_id, wait_time,
                                                   previous_account_deposits=previous_account_deposits,
                                                   temp_count=temp_count)
        raise Exception(
            "No needed '{}' account erc20 deposits. Waiting time result='{}'".format(account_id, wait_time))

    def get_erc20_account_withdrawals(self, base_test, account_id, database_api_id, wait_time=0,
                                      previous_account_withdrawals=None, temp_count=0):
        response_id = base_test.send_request(base_test.get_request("get_erc20_account_withdrawals", [account_id]),
                                             database_api_id)
        response = base_test.get_response(response_id)
        if response["result"] and response["result"] != previous_account_withdrawals:
            if False not in [False for withdrawal in response["result"] if not withdrawal["is_approved"]]:
                return response
            lcc.log_info("Waited for release of '{}' block(s). Wait time: '{}' seconds".format(temp_count, wait_time))
        temp_count += 1
        if temp_count <= BLOCKS_NUM_TO_WAIT:
            wait_time += self.set_timeout_until_num_blocks_released(base_test, database_api_id, print_log=False)
            return self.get_erc20_account_withdrawals(base_test, account_id, database_api_id, wait_time,
                                                      previous_account_withdrawals=previous_account_withdrawals,
                                                      temp_count=temp_count)
        raise Exception(
            "No needed '{}' account erc20 withdrawals. Waiting time result='{}'".format(account_id, wait_time))

    def get_updated_account_erc20_balance_in_eth_network(self, base_test, contract_instance, eth_account,
                                                         previous_balance, database_api_id, wait_time=0, temp_count=0):
        current_balance = base_test.eth_trx.get_balance_of(contract_instance, eth_account)
        if previous_balance != current_balance:
            lcc.log_info("Waited for release of '{}' block(s). Wait time: '{}' seconds".format(temp_count, wait_time))
            return current_balance
        temp_count += 1
        if temp_count <= BLOCKS_NUM_TO_WAIT:
            wait_time += self.set_timeout_until_num_blocks_released(base_test, database_api_id, print_log=False)
            return self.get_updated_account_erc20_balance_in_eth_network(base_test, contract_instance, eth_account,
                                                                         previous_balance, database_api_id, wait_time,
                                                                         temp_count=temp_count)
        raise Exception(
            "ERC20 balance of '{}' account not updated. Waiting time result='{}'".format(eth_account, wait_time))

    def get_erc20_token_balance_in_echo(self, base_test, account_id, balance_of_method, contract_id, database_api_id,
                                        previous_balance=None, wait_time=0, temp_count=0):
        argument = base_test.get_byte_code_param(account_id)
        operation = base_test.echo_ops.get_contract_call_operation(base_test.echo, account_id,
                                                                   bytecode=balance_of_method + argument,
                                                                   callee=contract_id)
        if account_id != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, account_id, temp_operation, database_api_id)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=False)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception(
                "Error: Can't call method 'balanceOf' of '{}' contract, response:\n{}".format(contract_id,
                                                                                              broadcast_result))
        contract_result = base_test.get_contract_result(broadcast_result, database_api_id)
        balance = base_test.get_contract_output(contract_result, output_type=int)

        if balance != previous_balance:
            lcc.log_info("Waited for release of '{}' block(s). Wait time: '{}' seconds".format(temp_count, wait_time))
            return balance
        temp_count += 1
        if temp_count <= BLOCKS_NUM_TO_WAIT:
            base_test.produce_block(database_api_id)
            return self.get_erc20_token_balance_in_echo(base_test, account_id, balance_of_method, contract_id,
                                                        database_api_id, previous_balance=previous_balance,
                                                        wait_time=wait_time, temp_count=temp_count)
        raise Exception(
            "ERC20 balance of '{}' account not updated. Waiting time result='{}'".format(account_id, wait_time))

    def get_verifiers_account_ids(self, prev_signatures):
        verifers_account_ids = []
        for signature in prev_signatures:
            if signature["_fallback"] == 0:
                verifers_account_ids.append("1.2." + str(signature["_producer"]))
        return verifers_account_ids

    def get_account_block_reward(self, base_test, account_ids, block_number, database_api_id):
        total_verifiers_balance, reward, total_verifiers_reward, delegate_reward, account_reward = 0, 0, 0, 0, 0
        verifiers_balances, rewards = [], {}
        verifiers_rewards, producer_rewards = {}, {}
        verifier, producer = False, False

        lcc.set_step("Get block with operation")
        response_id = base_test.send_request(base_test.get_request("get_block", [block_number]),
                                             database_api_id)
        result = base_test.get_response(response_id)["result"]
        block_producer = result["account"]
        fee_amount = result["transactions"][0]["fees_collected"]
        prev_signatures = result["cert"]
        lcc.log_info("Block producer: '{}' account".format(block_producer))
        verifiers_account_ids = self.get_verifiers_account_ids(prev_signatures)
        lcc.log_info("Block verifiers: {}".format(verifiers_account_ids))

        lcc.set_step("Check account ids in block verifiers")
        for account_id in account_ids:
            if account_id in verifiers_account_ids:
                verifier = True
                lcc.log_info("'{}' account in block verifiers".format(account_id))

        if verifier:
            lcc.set_step("Get verifiers total balance")
            params = [[verifiers_account_id, [base_test.echo_asset]] for verifiers_account_id in verifiers_account_ids]
            for param in params:
                response_id = base_test.send_request(base_test.get_request("get_account_balances", param),
                                                     database_api_id)
                verifiers_balance = base_test.get_response(response_id)["result"][0]["amount"]
                total_verifiers_balance += int(verifiers_balance)
                verifiers_balances.append(verifiers_balance)
            lcc.log_info("Verifiers total balance: {}".format(total_verifiers_balance))

            lcc.set_step("Get next block after block with operation")
            next_block_num = block_number + 1
            base_test.produce_block(database_api_id)
            response_id = base_test.send_request(base_test.get_request("get_block", [next_block_num]), database_api_id)
            prev_signatures = base_test.get_response(response_id)["result"]["prev_signatures"]

            lcc.set_step("Calculate verifiers reward")
            lcc.log_info("fee_amount: " + str(fee_amount))
            for i, verifier_balance in enumerate(verifiers_balances):
                verifier_reward_calculation = int(verifier_balance) * (fee_amount / 2)
                verifier_reward = int(verifier_reward_calculation / total_verifiers_balance)
                total_verifiers_reward += verifier_reward
                if prev_signatures[i]["_delegate"] != 0:
                    delegate_reward = int(verifier_reward * 0.2)
                    verifier_reward = verifier_reward - delegate_reward
                verifiers_rewards[verifiers_account_ids[i]] = int(verifier_reward)
                lcc.log_info(
                    "Added reward for verifier '{}' account: '{}'".format(verifiers_account_ids[i], verifier_reward))
            lcc.log_info("Verifiers rewards: {}".format(verifiers_rewards))

        lcc.set_step("Check account ids is block producer")
        for account_id in account_ids:
            if account_id == block_producer:
                producer = True
                lcc.log_info("'{}' account is block producer".format(account_id))
        if producer:
            fee_verifiers_rest = int(fee_amount / 2) - total_verifiers_reward
            total_producer_reward = int(fee_amount / 2) + fee_verifiers_rest
            if result["account"] != "":
                delegate_reward = int(total_producer_reward * 0.2)
            producer_reward = total_producer_reward - delegate_reward
            producer_rewards[block_producer] = producer_reward

        lcc.set_step("Confirm account ids rewards")
        for i, acc_id in enumerate(account_ids):
            if verifier:
                if verifiers_rewards.get(acc_id) is not None:
                    account_reward += verifiers_rewards[acc_id]
            if producer:
                if producer_rewards.get(acc_id) is not None:
                    account_reward += producer_rewards[acc_id]
            if verifier or producer:
                rewards[acc_id] = account_reward
            else:
                rewards[acc_id] = 0
        lcc.log_info("'{}' account got '{}' reward".format(account_id, rewards[account_id]))
        return rewards[account_id]
