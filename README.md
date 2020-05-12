# Automated Tests for Echo 
The project is intended for testing Echo project. Includes testing:
* [**Echo Node API**](https://docs.echo.org/api-reference/echo-node-api)
* [**Echo Operations**](https://docs.echo.org/api-reference/echo-operations)
* Testing according to specified scenarios


### Instalation:
Software Requirements: Python 3.7 or later 
##### Windows
    $ git clone https://github.com/echoprotocol/pytests.git
    $ cd pytests
    $ python3 -m pip install --user virtualenv
    $ virtualenv <ENVIRONMENT_NAME>
    $ .\<ENVIRONMENT_NAME>\Scripts\activate
    $ pip3 install -r requirements.txt
    $ export GENESIS_FILE=genesis.json

##### Linux
    $ git clone https://github.com/echoprotocol/pytests.git
    $ cd pytests
    $ virtualenv <ENVIRONMENT_NAME> -p python3.7
    $ source <ENVIRONMENT_NAME>/bin/activate
    $ pip3 install -r requirements.txt
    $ export GENESIS_FILE=genesis.json
    
##### Mac OS
*please see Linux installation*

## Usage
### Note:
##### Before running the tests, you should specify a environment variables: 
- *BASE_URL* - URL on which tests will be connected to the Echo node
- *ETHEREUM_URL* - URL on which tests will be connected to the Ethereum node
- *NATHAN_PK* - private key of "nathan" account
- *INIT0_PK* - private key of "init0" initial account
- *GENESIS_FILE* - Echo node genesis file

##### Optional:
- *ROPSTEN* - flag to run tests in the ropsten network (bool type)
- *DEBUG* - run tests with debug mode that log all in\out communication messages with Echo node (bool type)

##### for this you need, example:
* Linux OS: export BASE_URL=<BASE_URL>
* Windows OS: set BASE_URL=<BASE_URL>

### You can use docker-compose to run tests on the Echo and Ethereum nodes locally:
    $ cd pytests
    $ docker-compose pull
    $ docker-compose up build --no-cache
    $ docker-compose up migrate
    $ docker-compose up -d echo
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

Using `test_runner.py` script to run tests, you can specify a environment variable *PYTESTS_FILTERS* for filtering run command. </br>
Example: export PYTESTS_FILTERS=main:database_api</br>
For more information about filters see `test_runner.py` script.

## Project tree:
```
├── common
│   ├── base_test.py
│   ├── echo_operation.py
│   ├── ethereum_transaction.py
│   ├── object_validation.py
│   ├── receiver.py
│   ├── type_validation.py
│   └── utils.py
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
│   ├── AssetApi
│   │   ├── GetAllAssetHolders.py
│   │   ├── GetAssetHoldersCount.py
│   │   ├── GetAssetHolders.py
│   ├── DatabaseApi
│   │   ├── CallContractNoChangingState.py
│   │   ├── CheckERC20Token.py
│   │   └── ...
│   ├── DID Api
│   │   └── Get_did_object.py
│   ├── HistoryApi
│   │   ├── GetAccountHistory.py
│   │   ├── GetAccountHistoryOperations.py
│   │   ├── GetContractHistory.py
│   │   └── GetRelativeAccountHistory.py
│   ├── NetworkBroadcastApi
│   │   ├── BroadcastTransaction.py
│   │   ├── BroadcastTransactionSynchronous.py
│   │   └── BroadcastTransactionWithCallback.py
│   ├── Operations
│   │   ├── AccountManagement.py
│   │   ├── AssetManagement.py
│   │   └── ...
│   ├── RegistrationApi
│   │   ├── GetRegistrar.py
│   │   ├── RequestRegistrationTask.py
│   │   └── SubmitRegistrationSolution.py
│   ├── Scenarios
│   │   ├── AssetInt.py
│   │   ├── AssetUpdate.py
│   │   └── ...
│   ├── SideChain
│   │   ├── Bitcoin.py
│   │   ├── ERC20.py
│   │   └── Ethereum.py
│   ├── AssetApi.py
│   ├── DatabaseApi.py
│   ├── HistoryApi.py
│   ├── LoginApi.py
│   ├── NetworkBroadcastApi.py
│   ├── Operations.py
│   ├── RegistrationApi.py
│   ├── Scenarios.py
│   └── SideChain.py
├── .env
├── .flake8
├── .gitignore
├── .gitlab-ci.yml
├── .travis.yml
├── docker-compose.yml
├── Dockerfile
├── genesis.json
├── genesis_update_global_parameters.json
├── project.py
├── README.md
├── requirements.txt
└── test_runner.py
```

## To Do Lists

#### [Login API](https://docs.echo.org/api-reference/echo-node-api/login-api)

- [x] [login](https://docs.echo.org/api-reference/echo-node-api/login-api#login-user-password)

#### [Asset API](https://docs.echo.org/api-reference/echo-node-api/asset-api)

- [x] [get_asset_holders](https://docs.echo.org/api-reference/echo-node-api/asset-api#get_asset_holders-asset_id-start-limit)
- [x] [get_asset_holders_count](https://docs.echo.org/api-reference/echo-node-api/asset-api#get_asset_holders_count-asset_id)
- [x] [get_all_asset_holders](https://docs.echo.org/api-reference/echo-node-api/asset-api#get_all_asset_holders)

#### [Database API](https://docs.echo.org/api-reference/echo-node-api/database-api)

[Objects:](https://docs.echo.org/api-reference/echo-node-api/database-api#objects)
- [x] [get_objects](https://docs.echo.org/api-reference/echo-node-api/database-api#objects)  

[Subscriptions:](https://docs.echo.org/api-reference/echo-node-api/database-api#subscriptions)
- [x] [set_subscribe_callback](https://docs.echo.org/api-reference/echo-node-api/database-api#set_subscribe_callback-callback-clear_filter)
- [x] [set_pending_transaction_callback](https://docs.echo.org/api-reference/echo-node-api/database-api#set_pending_transaction_callback-callback)
- [x] [set_block_applied_callback ](https://docs.echo.org/api-reference/echo-node-api/database-api#set_block_applied_callback-callback)
- [x] [cancel_all_subscriptions](https://docs.echo.org/api-reference/echo-node-api/database-api#cancel_all_subscriptions)
- [ ] [unsubscribe_contract_logs](https://docs.echo.org/api-reference/echo-node-api/database-api#unsubscribe_contract_logs)

[Blocks and transactions:](https://docs.echo.org/api-reference/echo-node-api/database-api#blocks-and-transactions)
- [x] [get_block_header](https://docs.echo.org/api-reference/echo-node-api/database-api#get_block_header-block_num)
- [x] [get_block_header_batch](https://docs.echo.org/api-reference/echo-node-api/database-api#get_block_header_batch-block_nums)
- [x] [get_block](https://docs.echo.org/api-reference/echo-node-api/database-api#get_block-block_num)
- [x] [get_block_tx_number](https://docs.echo.org/api-reference/echo-node-api/database-api#get_block_tx_number-id)
- [x] [get_block_virtual_ops](https://docs.echo.org/api-reference/echo-node-api/database-api#get_block_virtual_ops-block_num)
- [x] [get_transaction](https://docs.echo.org/api-reference/echo-node-api/database-api#get_transaction-block_num-trx_in_block)
- [x] [get_recent_transaction_by_id](https://docs.echo.org/api-reference/echo-node-api/database-api#get_recent_transaction_by_id-id)

[Globals:](https://docs.echo.org/api-reference/echo-node-api/database-api#globals)
- [x] [get_chain_properties](https://docs.echo.org/api-reference/echo-node-api/database-api#get_chain_properties)
- [x] [get_global_properties](https://docs.echo.org/api-reference/echo-node-api/database-api#get_global_properties)
- [x] [get_config](https://docs.echo.org/api-reference/echo-node-api/database-api#get_config)
- [x] [get_chain_id](https://docs.echo.org/api-reference/echo-node-api/database-api#get_chain_id)
- [x] [get_dynamic_global_properties](https://docs.echo.org/api-reference/echo-node-api/database-api#get_dynamic_global_properties)

[Keys:](https://docs.echo.org/api-reference/echo-node-api/database-api#keys)
- [x] [get_key_references](https://docs.echo.org/api-reference/echo-node-api/database-api#get_key_references-keys)
- [x] [is_public_key_registered](https://docs.echo.org/api-reference/echo-node-api/database-api#is_public_key_registered-public_key)

[Accounts:](https://docs.echo.org/api-reference/echo-node-api/database-api#accounts)
- [x] [get_accounts](https://docs.echo.org/api-reference/echo-node-api/database-api#get_accounts-account_ids)
- [x] [get_full_accounts](https://docs.echo.org/api-reference/echo-node-api/database-api#get_full_accounts-names_or_ids-subscribe)
- [x] [get_account_by_name](https://docs.echo.org/api-reference/echo-node-api/database-api#get_account_by_name-name)
- [x] [get_account_references](https://docs.echo.org/api-reference/echo-node-api/database-api#get_account_references-account_id)
- [x] [lookup_account_names](https://docs.echo.org/api-reference/echo-node-api/database-api#lookup_account_names-account_names)
- [x] [lookup_accounts](https://docs.echo.org/api-reference/echo-node-api/database-api#lookup_accounts-lower_bound_name-limit)
- [x] [get_account_addresses](https://docs.echo.org/api-reference/echo-node-api/database-api#get_account_addresses-account_id-from-limit)
- [x] [get_account_by_address](https://docs.echo.org/api-reference/echo-node-api/database-api#get_account_by_address-address)
- [x] [get_account_count](https://docs.echo.org/api-reference/echo-node-api/database-api#get_account_count)

[Contracts:](https://docs.echo.org/api-reference/echo-node-api/database-api#contracts)
- [x] [get_contract](https://docs.echo.org/api-reference/echo-node-api/database-api#get_contract-contract_id)
- [x] [get_contracts](https://docs.echo.org/api-reference/echo-node-api/database-api#get_contracts-contract_ids)
- [x] [get_contract_logs](https://docs.echo.org/api-reference/echo-node-api/database-api#get_contract_logs-contract_logs_filter_options)
- [x] [subscribe_contracts](https://docs.echo.org/api-reference/echo-node-api/database-api#subscribe_contracts-contracts_ids)
- [x] [subscribe_contract_logs](https://docs.echo.org/api-reference/echo-node-api/database-api#subscribe_contract_logs-callback-contract_id)
- [x] [get_contract_result](https://docs.echo.org/api-reference/echo-node-api/database-api#get_contract_result-id)
- [x] [call_contract_no_changing_state](https://docs.echo.org/api-reference/echo-node-api/database-api#call_contract_no_changing_state-contract_id-caller-value-code)

[Contracts:](https://docs.echo.org/api-reference/echo-node-api/database-api#contracts)
- [x] [did_create]
- [x] [did_delete]
- [x] [did_update]

[Balances:](https://docs.echo.org/api-reference/echo-node-api/database-api#balances)
- [x] [get_account_balances](https://docs.echo.org/api-reference/echo-node-api/database-api#get_account_balances-id-assets)
- [x] [get_contract_balances](https://docs.echo.org/api-reference/echo-node-api/database-api#get_contract_balances-contract_id)
- [x] [get_named_account_balances](https://docs.echo.org/api-reference/echo-node-api/database-api#get_named_account_balances-name-assets)
- [x] [get_balance_objects](https://docs.echo.org/api-reference/echo-node-api/database-api#get_balance_objects-keys)
- [x] [get_vested_balances](https://docs.echo.org/api-reference/echo-node-api/database-api#get_vested_balances-objs)
- [x] [get_vesting_balances](https://docs.echo.org/api-reference/echo-node-api/database-api#get_vesting_balances-account_id)
- [x] [get_frozen_balances](https://docs.echo.org/api-reference/echo-node-api/database-api#get_frozen_balances-account_id)
- [x] [get_committee_frozen_balance](https://docs.echo.org/api-reference/echo-node-api/database-api#get_committee_frozen_balance-committee_member_id)

[Assets:](https://docs.echo.org/api-reference/echo-node-api/database-api#assets)
- [x] [get_assets](https://docs.echo.org/api-reference/echo-node-api/database-api#get_assets-asset_ids)
- [x] [list_assets](https://docs.echo.org/api-reference/echo-node-api/database-api#list_assets-lower_bound_symbol-limit)
- [x] [lookup_asset_symbols](https://docs.echo.org/api-reference/echo-node-api/database-api#lookup_asset_symbols-symbols_or_ids)

[Committee members:](https://docs.echo.org/api-reference/echo-node-api/database-api#committee-members)
- [x] [get_committee_members](https://docs.echo.org/api-reference/echo-node-api/database-api#get_committee_members-committee_member_ids)
- [x] [get_committee_member_by_account](https://docs.echo.org/api-reference/echo-node-api/database-api#get_committee_member_by_account-account)
- [x] [lookup_committee_member_accounts](https://docs.echo.org/api-reference/echo-node-api/database-api#lookup_committee_member_accounts-lower_bound_name-limit)
- [x] [get_committee_count](https://docs.echo.org/api-reference/echo-node-api/database-api#get_committee_count)

[Authority / validation:](https://docs.echo.org/api-reference/echo-node-api/database-api#authority-validation)
- [x] [get_transaction_hex](https://docs.echo.org/api-reference/echo-node-api/database-api#get_transaction_hex-trx)
- [x] [get_required_signatures](https://docs.echo.org/api-reference/echo-node-api/database-api#get_required_signatures-ctrx-available_keys)
- [x] [get_potential_signatures](https://docs.echo.org/api-reference/echo-node-api/database-api#get_potential_signatures-ctrx)
- [x] [verify_authority](https://docs.echo.org/api-reference/echo-node-api/database-api#verify_authority-trx)
- [x] [verify_account_authority](https://docs.echo.org/api-reference/echo-node-api/database-api#verify_account_authority-name_or_id-signers)
- [x] [validate_transaction](https://docs.echo.org/api-reference/echo-node-api/database-api#validate_transaction-trx)
- [x] [get_required_fees](https://docs.echo.org/api-reference/echo-node-api/database-api#get_required_fees-ops-id)

[Proposed transactions:](https://docs.echo.org/api-reference/echo-node-api/database-api#proposed-transactions)
- [x] [get_proposed_transactions](https://docs.echo.org/api-reference/echo-node-api/database-api#get_proposed_transactions-id)

[Sidechain:](https://docs.echo.org/api-reference/echo-node-api/database-api#sidechain)
- [x] [get_account_deposits](https://docs.echo.org/api-reference/echo-node-api/database-api#get_account_deposits-account-type)
- [x] [get_account_withdrawals](https://docs.echo.org/api-reference/echo-node-api/database-api#get_account_withdrawals-account-type)

[Sidechain Ethereum:](https://docs.echo.org/api-reference/echo-node-api/database-api#sidechain-ethereum)
- [x] [get_eth_address](https://docs.echo.org/api-reference/echo-node-api/database-api#get_eth_address-account)
- [x] [get_eth_sidechain_fees]

[Sidechain ERC20:](https://docs.echo.org/api-reference/echo-node-api/database-api#sidechain-erc20)
- [x] [get_erc20_token](https://docs.echo.org/api-reference/echo-node-api/database-api#get_erc-20-_token-eth_addr)
- [x] [check_erc20_token](https://docs.echo.org/api-reference/echo-node-api/database-api#check_erc-20-_token-id)
- [x] [get_erc20_account_deposits](https://docs.echo.org/api-reference/echo-node-api/database-api#get_erc-20-_account_deposits-account)
- [x] [get_erc20_account_withdrawals](https://docs.echo.org/api-reference/echo-node-api/database-api#get_erc-20-_account_withdrawals-account)

[Sidechain Bitcoin:](https://docs.echo.org/api-reference/echo-node-api/database-api#sidechain-bitcoin)
- [x] [get_btc_address](https://docs.echo.org/api-reference/echo-node-api/database-api#get_btc_address-account)
- [x] [get_btc_deposit_script](https://docs.echo.org/api-reference/echo-node-api/database-api#get_btc_deposit_script-address)
- [x] [get_btc_sidechain_fees]

[Contract Feepool:](https://docs.echo.org/api-reference/echo-node-api/database-api#contract-feepool)
- [x] [get_contract_pool_balance](https://docs.echo.org/api-reference/echo-node-api/database-api#get_contract_pool_balance-id)
- [x] [get_contract_pool_whitelist](https://docs.echo.org/api-reference/echo-node-api/database-api#get_contract_pool_whitelist-id)

#### [History API](https://docs.echo.org/api-reference/echo-node-api/history-api)

- [x] [get_account_history](https://docs.echo.org/api-reference/echo-node-api/history-api#get_account_history-account-stop-limit-start)
- [x] [get_account_history_operations](https://docs.echo.org/api-reference/echo-node-api/history-api#get_account_history_operations-account-operation_id-start-stop-limit)
- [x] [get_relative_account_history](https://docs.echo.org/api-reference/echo-node-api/history-api#get_relative_account_history-account-stop-limit-start)
- [x] [get_contract_history](https://docs.echo.org/api-reference/echo-node-api/history-api#get_contract_history-contract-stop-limit-start)

#### [Network broadcast API](https://docs.echo.org/api-reference/echo-node-api/network-broadcast-api)

- [x] [broadcast_transaction](https://docs.echo.org/api-reference/echo-node-api/network-broadcast-api#broadcast_transaction-trx)
- [x] [broadcast_transaction_with_callback](https://docs.echo.org/api-reference/echo-node-api/network-broadcast-api#broadcast_transaction_with_callback-cb-trx)
- [x] [broadcast_transaction_synchronous](https://docs.echo.org/api-reference/echo-node-api/network-broadcast-api#broadcast_transaction_synchronous-trx)
- [ ] [broadcast_block](https://docs.echo.org/api-reference/echo-node-api/network-broadcast-api#broadcast_block-signed_block)

#### [Registration API](https://docs.echo.org/api-reference/echo-node-api/registration-api)

- [x] [request_registration_task](https://docs.echo.org/api-reference/echo-node-api/registration-api#request_registration_task)
- [x] [submit_registration_solution](https://docs.echo.org/api-reference/echo-node-api/registration-api#submit_registration_solution-callback-name-active-echorand_key-nonce-rand_num)
- [x] [get_registrar](https://docs.echo.org/api-reference/echo-node-api/registration-api#get_registrar)


### [Operations:](https://docs.echo.org/api-reference/echo-operations)

#### [List of Account Management Operations](https://docs.echo.org/api-reference/echo-operations/account-management)

- [x] [account_create_operation](https://docs.echo.org/api-reference/echo-operations/account-management#account_create_operation)
- [x] [account_update_operation](https://docs.echo.org/api-reference/echo-operations/account-management#account_update_operation)
- [x] [account_whitelist_operation](https://docs.echo.org/api-reference/echo-operations/account-management#account_whitelist_operation)
- [x] [account_address_create_operation](https://docs.echo.org/api-reference/echo-operations/account-management#account_address_create_operation)
    
#### [List of Asset Management Operations](https://docs.echo.org/api-reference/echo-operations/asset-management)

- [x] [asset_create_operation](https://docs.echo.org/api-reference/echo-operations/asset-management#asset_create_operation)
- [x] [asset_update_operation](https://docs.echo.org/api-reference/echo-operations/asset-management#asset_update_operation)
- [x] [asset_update_bitasset_operation](https://docs.echo.org/api-reference/echo-operations/asset-management#asset_update_bitasset_operation)
- [x] [asset_update_feed_producers_operation](https://docs.echo.org/api-reference/echo-operations/asset-management#asset_update_feed_producers_operation)
- [x] [asset_issue_operation](https://docs.echo.org/api-reference/echo-operations/asset-management#asset_issue_operation)
- [x] [asset_reserve_operation](https://docs.echo.org/api-reference/echo-operations/asset-management#asset_reserve_operation)
- [x] [asset_fund_fee_pool_operation](https://docs.echo.org/api-reference/echo-operations/asset-management#asset_fund_fee_pool_operation)
- [x] [asset_publish_feed_operation](https://docs.echo.org/api-reference/echo-operations/asset-management#asset_publish_feed_operation)
- [x] [asset_claim_fees_operation](https://docs.echo.org/api-reference/echo-operations/asset-management#asset_claim_fees_operation)
    
#### [List of Balance Object Operations](https://docs.echo.org/api-reference/echo-operations/balance-object)

- [x] [balance_claim_operation](https://docs.echo.org/api-reference/echo-operations/balance-object#balance_claim_operation)
- [x] [balance_freeze_operation](https://docs.echo.org/api-reference/echo-operations/balance-object#balance_freeze_operation)
- [x] [balance_unfreeze_operation](https://docs.echo.org/api-reference/echo-operations/balance-object#balance_unfreeze_operation)

#### [List of For Committee Members Operations](https://docs.echo.org/api-reference/echo-operations/committee-member)

- [x] [committee_member_create_operation](https://docs.echo.org/api-reference/echo-operations/committee-member#committee_member_create_operation)
- [x] [committee_member_update_operation](https://docs.echo.org/api-reference/echo-operations/committee-member#committee_member_update_operation)
- [x] [committee_member_update_global_parameters_operation](https://docs.echo.org/api-reference/echo-operations/committee-member#committee_member_update_global_parameters_operation)
- [x] [committee_member_activate_operation](https://docs.echo.org/api-reference/echo-operations/committee-member#committee_member_activate_operation)
- [x] [committee_member_deactivate_operation](https://docs.echo.org/api-reference/echo-operations/committee-member#committee_member_deactivate_operation)
- [x] [committee_frozen_balance_deposit_operation](https://docs.echo.org/api-reference/echo-operations/committee-member#committee_frozen_balance_deposit_operation)
- [x] [committee_frozen_balance_withdraw_operation](https://docs.echo.org/api-reference/echo-operations/committee-member#committee_frozen_balance_withdraw_operation)

#### [List of Contract Operations](https://docs.echo.org/api-reference/echo-operations/contracts)

- [x] [contract_create_operation](https://docs.echo.org/api-reference/echo-operations/contracts#contract_create_operation)
- [x] [contract_call_operation](https://docs.echo.org/api-reference/echo-operations/contracts#contract_call_operation)
- [ ] [contract_internal_create_operation [VIRTUAL]](https://docs.echo.org/api-reference/echo-operations/contracts#contract_internal_create_operation)
- [ ] [contract_internal_call_operation [VIRTUAL]](https://docs.echo.org/api-reference/echo-operations/contracts#contract_internal_call_operation)
- [ ] [contract_selfdestruct_operation [VIRTUAL]](https://docs.echo.org/api-reference/echo-operations/contracts#contract_selfdestruct_operation)
- [x] [contract_update_operation](https://docs.echo.org/api-reference/echo-operations/contracts#contract_update_operation)
- [x] [contract_fund_pool_operation](https://docs.echo.org/api-reference/echo-operations/contracts#contract_fund_pool_operation)
- [x] [contract_whitelist_operation](https://docs.echo.org/api-reference/echo-operations/contracts#contract_whitelist_operation)

#### [List of Proposal Operations](https://docs.echo.org/api-reference/echo-operations/proposals)

- [x] [proposal_create_operation](https://docs.echo.org/api-reference/echo-operations/proposals#proposal_create_operation)
- [x] [proposal_update_operation](https://docs.echo.org/api-reference/echo-operations/proposals#proposal_update_operation)
- [x] [proposal_delete_operation](https://docs.echo.org/api-reference/echo-operations/proposals#proposal_delete_operation)

#### [List of Asset Transfer Operations](https://docs.echo.org/api-reference/echo-operations/asset-transfer)

- [x] [transfer_operation](https://docs.echo.org/api-reference/echo-operations/asset-transfer#transfer_operation)
- [x] [transfer_to_address_operation](https://docs.echo.org/api-reference/echo-operations/asset-transfer#transfer_to_address_operation)
- [x] [override_transfer_operation](https://docs.echo.org/api-reference/echo-operations/asset-transfer#override_transfer_operation)


#### [List of Sidechain Operations](https://docs.echo.org/api-reference/echo-operations/sidechain)

- [x] [sidechain_eth_create_address_operation](https://docs.echo.org/api-reference/echo-operations/sidechain#sidechain_eth_create_address_operation)
- [ ] [sidechain_eth_approve_address_operation [INTERNAL]](https://docs.echo.org/api-reference/echo-operations/sidechain#sidechain_eth_approve_address_operation)
- [ ] [sidechain_eth_deposit_operation [INTERNAL]](https://docs.echo.org/api-reference/echo-operations/sidechain#sidechain_eth_deposit_operation)
- [x] [sidechain_eth_withdraw_operation](https://docs.echo.org/api-reference/echo-operations/sidechain#sidechain_eth_withdraw_operation)
- [ ] [sidechain_eth_approve_withdraw_operation [INTERNAL]](https://docs.echo.org/api-reference/echo-operations/sidechain#sidechain_eth_approve_withdraw_operation)
- [ ] [sidechain_issue_operation [VIRTUAL]](https://docs.echo.org/api-reference/echo-operations/sidechain#sidechain_issue_operation)
- [ ] [sidechain_burn_operation [VIRTUAL]](https://docs.echo.org/api-reference/echo-operations/sidechain#sidechain_burn_operation)
- [x] [sidechain_erc20_register_token_operation](https://docs.echo.org/api-reference/echo-operations/sidechain#sidechain_erc-20-_register_token_operation)
- [ ] [sidechain_erc20_deposit_token_operation [INTERNAL]](https://docs.echo.org/api-reference/echo-operations/sidechain#sidechain_erc-20-_deposit_token_operation)
- [x] [sidechain_erc20_withdraw_token_operation](https://docs.echo.org/api-reference/echo-operations/sidechain#sidechain_erc-20-_withdraw_token_operation)
- [ ] [sidechain_erc20_approve_token_withdraw_operation [INTERNAL]](https://docs.echo.org/api-reference/echo-operations/sidechain#sidechain_erc-20-_approve_token_withdraw_operation)
- [ ] [sidechain_erc20_issue_operation [VIRTUAL]](https://docs.echo.org/api-reference/echo-operations/sidechain#sidechain_erc-20-_issue_operation)
- [ ] [sidechain_erc20_burn_operation [VIRTUAL]](https://docs.echo.org/api-reference/echo-operations/sidechain#sidechain_erc-20-_burn_operation)
- [x] [sidechain_btc_create_address_operation](https://docs.echo.org/api-reference/echo-operations/sidechain#sidechain_btc_create_address_operation)
- [ ] [sidechain_btc_create_intermediate_deposit_operation [INTERNAL]](https://docs.echo.org/api-reference/echo-operations/sidechain#sidechain_btc_create_intermediate_deposit_operation)
- [ ] [sidechain_btc_intermediate_deposit_operation [INTERNAL]](https://docs.echo.org/api-reference/echo-operations/sidechain#sidechain_btc_intermediate_deposit_operation)
- [ ] [sidechain_btc_deposit_operation [INTERNAL]](https://docs.echo.org/api-reference/echo-operations/sidechain#sidechain_btc_deposit_operation)
- [ ] [sidechain_btc_withdraw_operation](https://docs.echo.org/api-reference/echo-operations/sidechain#sidechain_btc_withdraw_operation)
- [ ] [sidechain_btc_aggregate_operation [INTERNAL]](https://docs.echo.org/api-reference/echo-operations/sidechain#sidechain_btc_aggregate_operation)
- [ ] [sidechain_btc_approve_aggregate_operation [INTERNAL]](https://docs.echo.org/api-reference/echo-operations/sidechain#sidechain_btc_approve_aggregate_operation)


#### [List of Vesting Balances Operations](https://docs.echo.org/api-reference/echo-operations/vesting-balances)

- [x] [vesting_balance_create_operation](https://docs.echo.org/api-reference/echo-operations/vesting-balances#vesting_balance_create_operation)
- [x] [vesting_balance_withdraw_operation](https://docs.echo.org/api-reference/echo-operations/vesting-balances#vesting_balance_withdraw_operation)
    

