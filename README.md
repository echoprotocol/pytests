# Automated Tests for Echo 
The project is intended for testing Echo project. Includes testing:
* [**Echo Node API**](https://docs.echo.org/api-reference/echo-node-api)
* [**Echo Operations**](https://docs.echo.org/api-reference/echo-operations)
* Testing according to specified scenarios

## Installation
### Windows
    $ git clone https://gitlab.pixelplex.by/631_echo/pytests.git
    $ cd pytests
    $ virtualenv venv
    $ .\venv\Scripts\activate
    $ pip install -r requirements.txt

### Linux
    $ git clone https://gitlab.pixelplex.by/631_echo/pytests.git
    $ cd pytests
    $ virtualenv venv
    $ source .\venv\bin\activate
    $ pip install -r requirements.txt
    
### Mac OS
*please see Linux installation*

## Usage
### Note:
##### Before running the tests, you should specify a environment variables: 
- *BASE_URL* - URL on which tests will be connected to the Echo node
- *ETHEREUM_URL* - URL on which tests will be connected to the Ethereum node
- *NATHAN_PK* - private key of "nathan" account
- *INIT0_PK* - private key of "init0" initial account

##### Optional:
- *ROPSTEN* - flag to run tests in the ropsten network (bool type)
- *DEBUG* - run tests with debug mode that log all in\out communication messages with Echo node (bool type)

##### for this you need, example:
* Linux OS: export BASE_URL=_[needed_url]()_
* Windows OS: set BASE_URL=_[needed_url]()_

### You can docker to run tests on the Echo and Ethereum nodes locally:
    $ cd pytests
    $ docker-compose pull
    $ docker-compose up build --no-cache
    $ docker-compose up migrate
    $ docker-compose up pytests

### To run tests you can use following commands in console:
    
Filter                           | lcc commands
---------------------------------|----------------------
Run all tests                    | `$ lcc run`
Run tests with special tag       | `$ lcc run -a tag_name`
Run tests with special property  | `$ lcc run -m property_kind:property_name`
Run tests with special link      | `$ lcc run -l link_name`
Run only passed tests            | `$ lcc run --passed`
Run only failed tests            | `$ lcc run --failed`
Run only skipped tests           | `$ lcc run --skipped`
Run only non-passed tests        | `$ lcc run --non-passed`
Run only disabled tests          | `$ lcc run --disabled`
Run only enabled tests           | `$ lcc run --enabled`
Run tests from special report    | `$ lcc run --from-report path_to_report`

_note:_ can combine run options, for example - `$ lcc run --failed --from-report reports/report-2`

## Project tree:
```
├── common
│   ├── base_test.py
│   ├── echo_operation.py
│   ├── ethereum_transaction.py
│   ├── receiver.py
│   ├── utils.py
│   └── validation.py
├── fixtures
│   └── base_fixtures.py
├── pre_run_scripts
│   └── pre_deploy.py
├── resources
│   ├── echo_contracts.json
│   ├── echo_operations.json
│   ├── ethereum_contracts.json
│   ├── ethereum_transactions.json
│   ├── private_keys.json (optional)
│   ├── urls.json
│   └── wallets.json (optional)
├── suites
│   ├── AssetApi
│   │   ├── GetAllAssetHolders.py
│   │   ├── GetAssetHolders.py
│   │   └── ...
│   ├── DatabaseApi
│   │   ├── CallContractNoChangingState.py
│   │   ├── CheckERC20Token.py
│   │   └── ...
│   ├── HistoryApi
│   │   ├── GetAccountHistory.py
│   │   ├── GetAccountHistoryOperations.py
│   │   └── ...
│   ├── Scenarios
│   │   ├── AssetInt.py
│   │   ├── BalanceObjectsInSubscribe.py
│   │   └── ...
│   ├── SideChain
│   │   ├── ERC20.py
│   │   └── Ethereum.py
│   ├── AssetApi.py
│   ├── DatabaseApi.py
│   ├── HistoryApi.py
│   ├── LoginApi.py
│   ├── NetworkBroadcastApi.py
│   ├── RegistrationApi.py
│   ├── Scenarios.py
│   └── SideChain.py
├── .env
├── .flake8
├── .gitignore
├── .gitlab-ci.yml
├── docker-compose.yml
├── Dockerfile
├── genesis.json
├── project.py
├── README.md
├── requirements.txt
└── test_runner.py
```

## To Do Lists

#### [Login API](https://echo-dev.io/developers/apis/login-api/#login-api)

- [x] [login](https://echo-dev.io/developers/apis/login-api/#loginstring-user-string-password)

#### [Asset API](https://echo-dev.io/developers/apis/asset-api/#asset-api)

- [x] [get_asset_holders](https://echo-dev.io/developers/apis/asset-api/#get_asset_holdersstring-asset_id-int-start-int-limit)
- [x] [get_asset_holders_count](https://echo-dev.io/developers/apis/asset-api/#get_asset_holders_countstring-asset_id)
- [x] [get_all_asset_holders](https://echo-dev.io/developers/apis/asset-api/#get_all_asset_holders)

#### [Database API](https://echo-dev.io/developers/apis/database-api/#database-api)

Objects: 
- [ ] [get_objects](https://echo-dev.io/developers/apis/database-api/#get_objectsarray-ids)  

Subscriptions:
- [x] [set_subscribe_callback](https://docs.echo.org/api-reference/echo-node-api/database-api#subscribe_contracts-contracts_ids)
- [x] [set_pending_transaction_callback](https://docs.echo.org/api-reference/echo-node-api/database-api#set_pending_transaction_callback-callback)
- [x] [set_block_applied_callback ](https://docs.echo.org/api-reference/echo-node-api/database-api#set_block_applied_callback-callback)
- [x] [cancel_all_subscriptions](https://docs.echo.org/api-reference/echo-node-api/database-api#set_block_applied_callback-callback)

Blocks and transactions:
- [x] [get_block_header](https://docs.echo.org/api-reference/echo-node-api/database-api#get_block_header-block_num)
- [x] [get_block_header_batch](https://docs.echo.org/api-reference/echo-node-api/database-api#get_block_header_batch-block_nums)
- [x] [get_block](https://docs.echo.org/api-reference/echo-node-api/database-api#get_block-block_num)
- [x] [get_block_tx_number](https://docs.echo.org/api-reference/echo-node-api/database-api#get_block_tx_number-id)
- [x] [get_block_virtual_ops](https://docs.echo.org/api-reference/echo-node-api/database-api#get_block_virtual_ops-block_num)
- [x] [get_transaction](https://docs.echo.org/api-reference/echo-node-api/database-api#get_transaction-block_num-trx_in_block)
- [x] [get_recent_transaction_by_id](https://docs.echo.org/api-reference/echo-node-api/database-api#get_recent_transaction_by_id-id)

Globals:
- [x] [get_chain_properties](https://docs.echo.org/api-reference/echo-node-api/database-api#get_chain_properties)
- [x] [get_global_properties](https://docs.echo.org/api-reference/echo-node-api/database-api#get_global_properties)
- [x] [get_config](https://docs.echo.org/api-reference/echo-node-api/database-api#get_config)
- [x] [get_chain_id](https://docs.echo.org/api-reference/echo-node-api/database-api#get_chain_id)
- [x] [get_dynamic_global_properties](https://docs.echo.org/api-reference/echo-node-api/database-api#get_dynamic_global_properties)

Keys:
- [x] [get_key_references](https://docs.echo.org/api-reference/echo-node-api/database-api#get_key_references-keys)
- [x] [is_public_key_registered](https://docs.echo.org/api-reference/echo-node-api/database-api#is_public_key_registered-public_key)

Accounts:
- [x] [get_accounts](https://docs.echo.org/api-reference/echo-node-api/database-api#get_accounts-account_ids)
- [x] [get_full_accounts](https://docs.echo.org/api-reference/echo-node-api/database-api#get_full_accounts-names_or_ids-subscribe)
- [x] [get_account_by_name](https://docs.echo.org/api-reference/echo-node-api/database-api#get_account_by_name-name)
- [x] [get_account_references](https://docs.echo.org/api-reference/echo-node-api/database-api#get_account_references-account_id)
- [x] [lookup_account_names](https://docs.echo.org/api-reference/echo-node-api/database-api#lookup_account_names-account_names)
- [x] [lookup_accounts](https://docs.echo.org/api-reference/echo-node-api/database-api#lookup_accounts-lower_bound_name-limit)
- [x] [get_account_addresses](https://docs.echo.org/api-reference/echo-node-api/database-api#get_account_addresses-account_id-from-limit)
- [x] [get_account_by_address](https://docs.echo.org/api-reference/echo-node-api/database-api#get_account_by_address-address)
- [x] [get_account_count](https://docs.echo.org/api-reference/echo-node-api/database-api#get_account_count)

Contracts:
- [x] [get_contract](https://docs.echo.org/api-reference/echo-node-api/database-api#get_contract-contract_id)
- [x] [get_contracts](https://docs.echo.org/api-reference/echo-node-api/database-api#get_contracts-contract_ids)
- [x] [get_contract_logs](https://docs.echo.org/api-reference/echo-node-api/database-api#get_contract_logs-contract_id-from-to)
- [x] [subscribe_contracts](https://docs.echo.org/api-reference/echo-node-api/database-api#subscribe_contracts-contracts_ids)
- [x] [subscribe_contract_logs](https://docs.echo.org/api-reference/echo-node-api/database-api#subscribe_contract_logs-callback-contract_id)
- [x] [get_contract_result](https://docs.echo.org/api-reference/echo-node-api/database-api#get_contract_result-id)
- [x] [call_contract_no_changing_state](https://docs.echo.org/api-reference/echo-node-api/database-api#call_contract_no_changing_state-contract_id-registrar_account-asset_type-code)

Balances:
- [x] [get_account_balances](https://docs.echo.org/api-reference/echo-node-api/database-api#get_account_balances-id-assets)
- [x] [get_contract_balances](https://docs.echo.org/api-reference/echo-node-api/database-api#get_contract_balances-contract_id)
- [x] [get_named_account_balances](https://docs.echo.org/api-reference/echo-node-api/database-api#get_named_account_balances-name-assets)
- [x] [get_balance_objects](https://docs.echo.org/api-reference/echo-node-api/database-api#get_balance_objects-keys)
- [x] [get_vested_balances](https://docs.echo.org/api-reference/echo-node-api/database-api#get_vested_balances-objs)
- [x] [get_vesting_balances](https://docs.echo.org/api-reference/echo-node-api/database-api#get_vesting_balances-account_id)
- [x] [get_frozen_balances](https://docs.echo.org/api-reference/echo-node-api/database-api#get_frozen_balances-account_id)
- [ ] [get_committee_frozen_balance]()

Assets:
- [x] [get_assets](https://docs.echo.org/v/feature%252Fwhtiepaper/api-reference/echo-node-api/asset-api#get_asset_holders_count-asset_id)
- [x] [list_assets](https://docs.echo.org/api-reference/echo-node-api/database-api#list_assets-lower_bound_symbol-limit)
- [x] [lookup_asset_symbols](https://docs.echo.org/api-reference/echo-node-api/database-api#list_assets-lower_bound_symbol-limit)

Committee members:
- [x] [get_committee_members](https://docs.echo.org/api-reference/echo-node-api/database-api#get_committee_members-committee_member_ids)
- [x] [get_committee_member_by_account](https://docs.echo.org/api-reference/echo-node-api/database-api#get_committee_member_by_account-account)
- [x] [lookup_committee_member_accounts](https://docs.echo.org/api-reference/echo-node-api/database-api#lookup_committee_member_accounts-lower_bound_name-limit)
- [x] [get_committee_count](https://docs.echo.org/api-reference/echo-node-api/database-api#get_committee_count)

Authority / validation:
- [x] [get_transaction_hex](https://docs.echo.org/api-reference/echo-node-api/database-api#get_transaction_hex-trx)
- [x] [get_required_signatures](https://docs.echo.org/api-reference/echo-node-api/database-api#get_required_signatures-ctrx-available_keys)
- [x] [get_potential_signatures](https://docs.echo.org/api-reference/echo-node-api/database-api#get_potential_signatures-ctrx)
- [x] [verify_authority](https://docs.echo.org/api-reference/echo-node-api/database-api#verify_authority-trx)
- [x] [verify_account_authority](https://docs.echo.org/api-reference/echo-node-api/database-api#verify_account_authority-name_or_id-signers)
- [x] [validate_transaction](https://docs.echo.org/api-reference/echo-node-api/database-api#validate_transaction-trx)
- [x] [get_required_fees](https://docs.echo.org/api-reference/echo-node-api/database-api#get_required_fees-ops-id)

Proposed transactions:
- [x] [get_proposed_transactions](https://docs.echo.org/api-reference/echo-node-api/database-api#get_proposed_transactions-id)

Sidechain:
- [x] [get_eth_address](https://docs.echo.org/api-reference/echo-node-api/database-api#get_eth_address-account)
- [x] [get_account_deposits](https://docs.echo.org/api-reference/echo-node-api/database-api#get_account_deposits-account)
- [x] [get_account_withdrawals](https://docs.echo.org/api-reference/echo-node-api/database-api#get_account_withdrawals-account)

Sidechain ERC20:
- [x] [get_erc20_token](https://docs.echo.org/api-reference/echo-node-api/database-api#get_erc-20-_token-eth_addr)
- [x] [get_erc20_account_deposits](https://docs.echo.org/api-reference/echo-node-api/database-api#get_erc-20-_account_deposits-account)
- [x] [get_erc20_account_withdrawals](https://docs.echo.org/api-reference/echo-node-api/database-api#get_erc-20-_account_withdrawals-account)
- [x] check_erc20_token

Contract Feepool:
- [x] [get_contract_pool_balance](https://docs.echo.org/api-reference/echo-node-api/database-api#get_contract_pool_balance-id)
- [x] [get_contract_pool_whitelist](https://docs.echo.org/api-reference/echo-node-api/database-api#get_contract_pool_whitelist-id)

#### [History API](https://echo-dev.io/developers/apis/history-api/#history-api)

- [x] [get_account_history](https://docs.echo.org/api-reference/echo-node-api/history-api#get_account_history-account-stop-limit-start)
- [x] [get_account_history_operations](https://docs.echo.org/api-reference/echo-node-api/history-api#get_account_history_operations-account-operation_id-start-stop-limit)
- [x] [get_relative_account_history](https://docs.echo.org/api-reference/echo-node-api/history-api#get_relative_account_history-account-stop-limit-start)
- [x] [get_contract_history](https://docs.echo.org/api-reference/echo-node-api/history-api#get_contract_history-contract-stop-limit-start)

#### [Network broadcast API](https://echo-dev.io/developers/apis/network-broadcast-api/#network-broadcast-api)
- [ ] [broadcast_transaction](https://docs.echo.org/api-reference/echo-node-api/network-broadcast-api#broadcast_transaction-trx)
- [ ] [broadcast_block](https://echo-dev.io/developers/apis/network-broadcast-api/#broadcast_block)
- [ ] [broadcast_transaction_with_callback](https://docs.echo.org/api-reference/echo-node-api/network-broadcast-api#broadcast_transaction_with_callback-cb-trx)
- [ ] [broadcast_transaction_synchronous ](https://docs.echo.org/api-reference/echo-node-api/network-broadcast-api#broadcast_transaction_synchronous-trx)
- [ ] [broadcast_block](https://docs.echo.org/api-reference/echo-node-api/network-broadcast-api#broadcast_block-signed_block)

#### [Registration API](https://echo-dev.io/developers/apis/registration-api/#registration-api)

- [ ] [request_registration_task](https://docs.echo.org/api-reference/echo-node-api/registration-api#request_registration_task)
- [ ] [submit_registration_solution](https://docs.echo.org/api-reference/echo-node-api/registration-api#submit_registration_solution-callback-name-active-echorand_key-nonce-rand_num)
- [ ] [get_registrar](https://docs.echo.org/api-reference/echo-node-api/registration-api#submit_registration_solution-callback-name-active-echorand_key-nonce-rand_num)


### Operations:

#### [List of Account Management Operations](https://echo-dev.io/developers/operations/#account-management)

- [ ] [account_create_operation](https://echo-dev.io/developers/operations/account_management/_account_create_operation/)
- [ ] [account_update_operation](https://echo-dev.io/developers/operations/account_management/_account_update_operation/)
- [ ] [account_whitelist_operation](https://echo-dev.io/developers/operations/account_management/_account_whitelist_operation/)
- [ ] [account_upgrade_operation](https://echo-dev.io/developers/operations/account_management/_account_upgrade_operation/)
- [ ] [account_transfer_operation](https://echo-dev.io/developers/operations/account_management/_account_transfer_operation/)
    
#### [List of Assert Conditions Operations](https://echo-dev.io/developers/operations/#assert-conditions)

- [ ] [assert_operation](https://echo-dev.io/developers/operations/assert_conditions/_assert_operation/)
    
#### [List of Asset Management Operations](https://echo-dev.io/developers/operations/#asset-management)

- [ ] [asset_create_operation](https://echo-dev.io/developers/operations/asset_management/_asset_create_operation/)
- [ ] [asset_global_settle_operation](https://echo-dev.io/developers/operations/asset_management/_asset_global_settle_operation/)
- [ ] [asset_settle_operation](https://echo-dev.io/developers/operations/asset_management/_asset_settle_operation/)
- [ ] [asset_settle_cancel_operation [VIRTUAL]](https://echo-dev.io/developers/operations/asset_management/_asset_settle_cancel_operation/)
- [ ] [asset_fund_fee_pool_operation](https://echo-dev.io/developers/operations/asset_management/_asset_fund_fee_pool_operation/)
- [ ] [asset_update_operation](https://echo-dev.io/developers/operations/asset_management/_asset_update_operation/)
- [ ] [asset_update_bitasset_operation](https://echo-dev.io/developers/operations/asset_management/_asset_update_bitasset_operation/)
- [ ] [asset_update_feed_producers_operation](https://echo-dev.io/developers/operations/asset_management/_asset_update_feed_producers_operation/)
- [ ] [asset_publish_feed_operation](https://echo-dev.io/developers/operations/asset_management/_asset_publish_feed_operation/)
- [ ] [asset_issue_operation](https://echo-dev.io/developers/operations/asset_management/_asset_issue_operation/)
- [ ] [asset_reserve_operation](https://echo-dev.io/developers/operations/asset_management/_asset_reserve_operation/)
- [ ] [asset_claim_fees_operation](https://echo-dev.io/developers/operations/asset_management/_asset_claim_fees_operation/)
    
#### [List of Balance Object Operations](https://echo-dev.io/developers/operations/#balance-object)

- [ ] [balance_claim_operation](https://echo-dev.io/developers/operations/balance_object/_balance_claim_operation/)

#### [List of For Committee Members Operations](https://echo-dev.io/developers/operations/#for-committee-members)

- [ ] [committee_member_create_operation](https://echo-dev.io/developers/operations/committee_member/_committee_member_create_operation/)
- [ ] [committee_member_update_operation](https://echo-dev.io/developers/operations/committee_member/_committee_member_update_operation/)
- [ ] [committee_member_update_global_parameters_operation](https://echo-dev.io/developers/operations/committee_member/_committee_member_update_global_parameters_operation/)
    
#### [List of Contract Operations](https://echo-dev.io/developers/operations/#contract-operations)

- [ ] [contract_create_operation](https://echo-dev.io/developers/operations/contracts/_create_contract_operation/)
- [ ] [contract_call_operation](https://echo-dev.io/developers/operations/contracts/_call_contract_operation/)
- [ ] [contract_transfer_operation [VIRTUAL]](https://echo-dev.io/developers/operations/contracts/_contract_transfer_operation/)
    
#### [List of Custom Extension Operations](https://echo-dev.io/developers/operations/#custom-extension)

- [ ] [custom_operation](https://echo-dev.io/developers/operations/custom/_custom_operation/)

#### [List of Assets Market Operations](https://echo-dev.io/developers/operations/#assets-market)

- [ ] [limit_order_create_operation](https://echo-dev.io/developers/operations/asset_market/_limit_order_create_operation/)
- [ ] [limit_order_cancel_operation](https://echo-dev.io/developers/operations/asset_market/_limit_order_cancel_operation/)
- [ ] [call_order_update_operation](https://echo-dev.io/developers/operations/asset_market/_call_order_update_operation/)
- [ ] [fill_order_operation [VIRTUAL]](https://echo-dev.io/developers/operations/asset_market/_fill_order_operation/)
- [ ] [bid_collateral_operation](https://echo-dev.io/developers/operations/asset_market/_bid_collateral_operation/)
- [ ] [execute_bid_operation [VIRTUAL]](https://echo-dev.io/developers/operations/asset_market/_execute_bid_operation/)

#### [List of Proposal Operations](https://echo-dev.io/developers/operations/#proposal-operations)

- [ ] [proposal_create_operation](https://echo-dev.io/developers/operations/proposals/_proposal_create_operation/)
- [ ] [proposal_update_operation](https://echo-dev.io/developers/operations/proposals/_proposal_update_operation/)
- [ ] [proposal_delete_operation](https://echo-dev.io/developers/operations/proposals/_proposal_delete_operation/)

#### [List of Asset Transfer Operations](https://echo-dev.io/developers/operations/#asset-transfer)

- [ ] [transfer_operation](https://echo-dev.io/developers/operations/asset_transfer/_transfer_operation/)
- [ ] [override_transfer_operation](https://echo-dev.io/developers/operations/asset_transfer/_override_transfer_operation/)
    
#### [List of Vesting Balances Operations](https://echo-dev.io/developers/operations/#vesting-balances)

- [ ] [vesting_balance_create_operation](https://echo-dev.io/developers/operations/vesting_balances/_vesting_balance_create_operation/)
- [ ] [vesting_balance_withdraw_operation](https://echo-dev.io/developers/operations/vesting_balances/_vesting_balance_withdraw_operation/)
    
#### [List of Withdrawal Permissions Operations](https://echo-dev.io/developers/operations/#withdrawal-permissions)

- [ ] [withdraw_permission_create_operation](https://echo-dev.io/developers/operations/withdraw_permission/_withdraw_permission_create_operation/)
- [ ] [withdraw_permission_update_operation](https://echo-dev.io/developers/operations/withdraw_permission/_withdraw_permission_update_operation/)
- [ ] [withdraw_permission_claim_operation](https://echo-dev.io/developers/operations/withdraw_permission/_withdraw_permission_claim_operation/)
- [ ] [withdraw_permission_delete_operation](https://echo-dev.io/developers/operations/withdraw_permission/_withdraw_permission_delete_operation/)
