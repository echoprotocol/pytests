# -*- coding: utf-8 -*-
import re

from project import BASE_ASSET_SYMBOL

NAME_MIN_LENGTH = 1
NAME_MAX_LENGTH = 63


class TypeValidator(object):
    id_regex = re.compile(r"^(0|([1-9]\d*\.)){2}(0|([1-9]\d*))$")
    account_id_regex = re.compile(r"^1\.2\.(0|[1-9]\d*)$")
    asset_id_regex = re.compile(r"^1\.3\.(0|[1-9]\d*)$")
    eth_asset_id_regex = re.compile(r"^1.3.1$")
    btc_asset_id_regex = re.compile(r"^1.3.2$")
    committee_member_id_regex = re.compile(r"^1\.4\.(0|[1-9]\d*)$")
    proposal_id_regex = re.compile(r"^1\.5\.(0|[1-9]\d*)$")
    operation_history_id_regex = re.compile(r"^1\.6\.(0|[1-9]\d*)$")
    vesting_balance_id_regex = re.compile(r"^1\.7\.(0|[1-9]\d*)$")
    balance_id_regex = re.compile(r"^1\.8\.(0|[1-9]\d*)$")
    frozen_balance_id_regex = re.compile(r"^1\.9\.(0|[1-9]\d*)$")
    committee_frozen_balance_id_regex = re.compile(r"^1\.10\.(0|[1-9]\d*)$")
    contract_id_regex = re.compile(r"^1\.11\.(0|[1-9]\d*)$")
    contract_result_id_regex = re.compile(r"^1\.12\.(0|[1-9]\d*)$")
    block_id_regex = re.compile(r"^1\.13\.(0|[1-9]\d*)$")
    eth_address_id_regex = re.compile(r"^1\.13\.(0|[1-9]\d*)$")
    deposit_eth_id_regex = re.compile(r"^1\.14\.(0|[1-9]\d*)$")
    withdraw_eth_id_regex = re.compile(r"^1\.15\.(0|[1-9]\d*)$")
    erc20_object_id_regex = re.compile(r"^1\.16\.(0|[1-9]\d*)$")
    deposit_erc20_id_regex = re.compile(r"^1\.17\.(0|[1-9]\d*)$")
    withdraw_erc20_id_regex = re.compile(r"^1\.18\.(0|[1-9]\d*)$")
    btc_address_id_regex = re.compile(r"^1\.19\.(0|[1-9]\d*)$")
    btc_intermediate_deposit_id_regex = re.compile(r"^1\.20\.(0|[1-9]\d*)$")
    btc_deposit_id_regex = re.compile(r"^1\.21\.(0|[1-9]\d*)$")
    btc_withdraw_id_regex = re.compile(r"^1\.22\.(0|[1-9]\d*)$")
    btc_aggregating_id_regex = re.compile(r"^1\.23\.(0|[1-9]\d*)$")

    global_object_id_regex = re.compile(r"^2.0.0$")
    dynamic_global_object_id_regex = re.compile(r"^2.1.0$")
    dynamic_asset_data_id_regex = re.compile(r"^2\.2\.(0|[1-9]\d*)$")
    bitasset_id_regex = re.compile(r"^2\.3\.(0|[1-9]\d*)$")
    account_balance_id_regex = re.compile(r"^2\.4\.(0|[1-9]\d*)$")
    account_statistics_id_regex = re.compile(r"^2\.5\.(0|[1-9]\d*)$")
    transaction_id_regex = re.compile(r"^2\.6\.(0|[1-9]\d*)$")
    block_summary_id_regex = re.compile(r"^2\.7\.(0|[1-9]\d*)$")
    account_transaction_history_id_regex = re.compile(r"^2\.8\.(0|[1-9]\d*)$")
    chain_property_object_id_regex = re.compile(r"^2.9.0$")
    special_authority_id_regex = re.compile(r"^2\.10\.(0|[1-9]\d*)$")
    contract_balance_id_regex = re.compile(r"^2\.11\.(0|[1-9]\d*)$")
    contract_history_id_regex = re.compile(r"^2\.12\.(0|[1-9]\d*)$")
    contract_statistics_id_regex = re.compile(r"^2\.13\.(0|[1-9]\d*)$")
    account_address_id_regex = re.compile(r"^2\.14\.(0|[1-9]\d*)$")
    contract_pool_id_regex = re.compile(r"^2\.15\.(0|[1-9]\d*)$")
    malicious_committeemen_id_regex = re.compile(r"^2\.16\.(0|[1-9]\d*)$")
    hex_regex = re.compile("^[0-9a-fA-F]+")
    bytecode_regex = re.compile(r"^[\da-fA-F]{8}([\da-fA-F]{64})*$")
    vote_id_type_regex = re.compile(r"^[0-3]:[0-9]+")
    iso8601_regex = re.compile(r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01]"
                               r"[0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$")
    base58_regex = re.compile(r"^[1-9A-HJ-NP-Za-km-z]+$")
    wif_regex = re.compile(r"^5[HJK][1-9A-Za-z][^OIl]{48}$")

    def __init__(self):
        super().__init__()

    def is_object_id(self, value):
        return bool(self.id_regex.match(value) and len(value.split(".")) == 3)

    @staticmethod
    def is_string(value):
        if not isinstance(value, str):
            return False
        return True

    @staticmethod
    def is_int(value, x):
        try:
            value = abs(int(value))
            if value > 2 ** x:
                raise Exception("Entered value is greater than this type may contain")
            else:
                return True
        except ValueError:
            "Value is not integer"

    @staticmethod
    def is_uint(value, x):
        try:
            value = int(value)
            if value < 0 or value >= 2 ** x:
                raise Exception("Entered value is greater than this type may contain")
            else:
                return True
        except ValueError:
            "Value is not integer"

    def is_hex(self, value):
        if self.is_string(value):
            return bool(self.hex_regex.match(value))

    def is_bytecode(self, value):
        if self.is_string(value):
            return bool(self.bytecode_regex.match(value))

    def is_bytes(self, value, length):
        return self.is_hex(value) and len(value) == length * 2

    def is_account_id(self, value):
        if self.is_string(value):
            return bool(self.account_id_regex.match(value))

    def is_block_id(self, value):
        if self.is_string(value):
            return bool(self.block_id_regex.match(value))

    def is_asset_id(self, value):
        if self.is_string(value):
            return bool(self.asset_id_regex.match(value))

    def is_eth_asset_id(self, value):
        if self.is_string(value):
            return bool(self.eth_asset_id_regex.match(value))

    def is_btc_asset_id(self, value):
        if self.is_string(value):
            return bool(self.btc_asset_id_regex.match(value))

    def is_committee_member_id(self, value):
        if self.is_string(value):
            return bool(self.committee_member_id_regex.match(value))

    def is_proposal_id(self, value):
        if self.is_string(value):
            return bool(self.proposal_id_regex.match(value))

    def is_operation_history_id(self, value):
        if self.is_string(value):
            return bool(self.operation_history_id_regex.match(value))

    def is_vesting_balance_id(self, value):
        if self.is_string(value):
            return bool(self.vesting_balance_id_regex.match(value))

    def is_balance_id(self, value):
        if self.is_string(value):
            return bool(self.balance_id_regex.match(value))

    def is_frozen_balance_id(self, value):
        if self.is_string(value):
            return bool(self.frozen_balance_id_regex.match(value))

    def is_committee_frozen_balance_id(self, value):
        if self.is_string(value):
            return bool(self.committee_frozen_balance_id_regex.match(value))

    def is_contract_id(self, value):
        if self.is_string(value):
            return bool(self.contract_id_regex.match(value))

    def is_contract_result_id(self, value):
        if self.is_string(value):
            return bool(self.contract_result_id_regex.match(value))

    def is_eth_address_id(self, value):
        if self.is_string(value):
            return bool(self.eth_address_id_regex.match(value))

    def is_deposit_eth_id(self, value):
        if self.is_string(value):
            return bool(self.deposit_eth_id_regex.match(value))

    def is_withdraw_eth_id(self, value):
        if self.is_string(value):
            return bool(self.withdraw_eth_id_regex.match(value))

    def is_erc20_object_id(self, value):
        if self.is_string(value):
            return bool(self.erc20_object_id_regex.match(value))

    def is_deposit_erc20_id(self, value):
        if self.is_string(value):
            return bool(self.deposit_erc20_id_regex.match(value))

    def is_withdraw_erc20_id(self, value):
        if self.is_string(value):
            return bool(self.withdraw_erc20_id_regex.match(value))

    def is_btc_address_id(self, value):
        if self.is_string(value):
            return bool(self.btc_address_id_regex.match(value))

    def is_btc_intermediate_deposit_id(self, value):
        if self.is_string(value):
            return bool(self.btc_intermediate_deposit_id_regex.match(value))

    def is_deposit_id(self, value):
        if self.is_string(value):
            return bool(self.btc_deposit_id_regex.match(value))

    def is_btc_withdraw_id(self, value):
        if self.is_string(value):
            return bool(self.btc_withdraw_id_regex.match(value))

    def is_btc_aggregating_id(self, value):
        if self.is_string(value):
            return bool(self.btc_aggregating_id_regex.match(value))

    def is_global_object_id(self, value):
        if self.is_string(value):
            return bool(self.global_object_id_regex.match(value))

    def is_dynamic_global_object_id(self, value):
        if self.is_string(value):
            return bool(self.dynamic_global_object_id_regex.match(value))

    def is_dynamic_asset_data_id(self, value):
        if self.is_string(value):
            return bool(self.dynamic_asset_data_id_regex.match(value))

    def is_bitasset_id(self, value):
        if self.is_string(value):
            return bool(self.bitasset_id_regex.match(value))

    def is_account_balance_id(self, value):
        if self.is_string(value):
            return bool(self.account_balance_id_regex.match(value))

    def is_account_statistics_id(self, value):
        if self.is_string(value):
            return bool(self.account_statistics_id_regex.match(value))

    def is_transaction_id(self, value):
        if self.is_string(value):
            return bool(self.transaction_id_regex.match(value))

    def is_block_summary_id(self, value):
        if self.is_string(value):
            return bool(self.block_summary_id_regex.match(value))

    def is_account_transaction_history_id(self, value):
        if self.is_string(value):
            return bool(self.account_transaction_history_id_regex.match(value))

    def is_chain_property_object_id(self, value):
        if self.is_string(value):
            return bool(self.chain_property_object_id_regex.match(value))

    def is_special_authority_object_id(self, value):
        if self.is_string(value):
            return bool(self.special_authority_id_regex.match(value))

    def is_contract_balance_object_id(self, value):
        if self.is_string(value):
            return bool(self.contract_balance_id_regex.match(value))

    def is_contract_history_id(self, value):
        if self.is_string(value):
            return bool(self.contract_history_id_regex.match(value))

    def is_contract_statistics_id(self, value):
        if self.is_string(value):
            return bool(self.contract_statistics_id_regex.match(value))

    def is_account_address_id(self, value):
        if self.is_string(value):
            return bool(self.account_address_id_regex.match(value))

    def is_contract_pool_id(self, value):
        if self.is_string(value):
            return bool(self.contract_pool_id_regex.match(value))

    def is_malicious_committeemen_id(self, value):
        if self.is_string(value):
            return bool(self.malicious_committeemen_id_regex.match(value))

    def is_vote_id(self, value):
        if self.is_string(value):
            return bool(self.vote_id_type_regex.match(value))

    def is_uint8(self, value):
        return self.is_uint(value, 8)

    def is_uint16(self, value):
        return self.is_uint(value, 16)

    def is_uint32(self, value):
        return self.is_uint(value, 32)

    def is_uint64(self, value):
        return self.is_uint(value, 64)

    def is_uint256(self, value):
        return self.is_int(value, 256)

    @staticmethod
    def is_asset_name(value):
        return bool(value is not None and len(value.split(".")) <= 2 and 3 <= len(value) <= 16 and re.match(
            r"^[A-Z][A-Z\d.]*[A-Z]$", value))

    def is_account_name(self, value):
        if not self.is_string(value):
            return False
        if value is None:
            return False
        if len(value) < NAME_MIN_LENGTH or len(value) > NAME_MAX_LENGTH:
            return False

        ref = value.split(".")

        for label in ref:
            if not bool(re.match(r"^[a-z][a-z0-9-]*[a-z\d]$", label)) or bool(re.match(r".*--.*", label)):
                return False
        return True

    def is_ripemd160(self, value):
        return self.is_hex(value) and len(value) == 40

    @staticmethod
    def check_account_name(value):
        if value is None or len(value) == 0:
            raise ValueError("Account name should not be empty.")
        if len(value) < NAME_MIN_LENGTH or len(value) > NAME_MAX_LENGTH:
            raise ValueError("Account name should be from 3 to 63.")
        for label in range(value.split(".")):
            if not re.match(r"^[~a-z]", str(label)):
                raise ValueError("Each account segment should start with a letter.")
            if not re.match(r"^[~a-z0-9-]*$", str(label)):
                raise ValueError("Each account segment should have only letter, digits or dashes.")
            if re.match(r".*--.*", str(label)):
                raise ValueError("Each account segment should have only one dash in a row.")
            if not re.match(r"[a-z0-9]$", str(label)):
                raise ValueError("Each account segment should end with a letter or digit.")
            if len(str(label)) < NAME_MIN_LENGTH:
                raise ValueError("Each account segment should be longer.")
        return True

    def is_operation_id(self, value):
        return self.is_uint8(value) and value < 49

    def is_base58(self, value):
        return bool(self.base58_regex.match(value))

    def is_wif(self, value):
        return bool(self.wif_regex.match(value))

    def is_echorand_key(self, value, address_prefix=BASE_ASSET_SYMBOL):
        if value[:len(address_prefix)] != address_prefix:
            return False
        key = value[len(address_prefix):]
        if not self.is_base58(key) or 44 + len(address_prefix) < len(value) or len(value) < 43 + len(address_prefix):
            return False
        return True

    def is_iso8601(self, value):
        if self.is_string(value):
            return bool(self.iso8601_regex.match(value))

    def is_eth_address(self, value):
        if not self.is_hex(value):
            return False
        if value[:2] == "0x":
            return len(value) == 42
        else:
            return len(value) == 40

    def is_btc_public_key(self, value):
        if not self.is_hex(value):
            return False
        if len(value) == 66:
            return True

    def is_digit(self, value):
        if type(value) is int:
            return True
        elif type(value) is str:
            boolean = value.isdigit()
            return boolean
        else:
            return False

