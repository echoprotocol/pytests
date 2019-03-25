# Automated Tests for Echo 
The project is intended for testing Echo. Includes testing:
* [Api](https://echo-dev.io/developers/apis/)
* [Operations](https://echo-dev.io/developers/operations/)
* Testing according to specified scenarios

## Installation

### Manual installation:

    $ git clone https://gitlab.pixelplex.by/631_echo/pytests.git
    $ cd pytests
    $ virtualenv venv
    $ .\venv\Scripts\activate
    $ pip install -r requirements.txt

## Usage

    
**Filter**                       | **lcc commands**
---------------------------------|----------------------
Run all tests                    | `$ lcc run`
Run tests with special tag       | `$ lcc run -a tag_name`
Run tests with special property  | `$ lcc run -m priority_kind:property_name`
Run tests with special link      | `$ lcc run -l link_name`
Run only passed tests            | `$ lcc run --passed`
Run only failed tests            | `$ lcc run --failed`
Run only skipped tests           | `$ lcc run --skipped`
Run only non-passed tests        | `$ lcc run --non-passed`
Run only disabled tests          | `$ lcc run --disabled`
Run only enabled tests           | `$ lcc run --enabled`
Run tests from special report    | `$ lcc run --from-report path_to_report`

**_note:_** can combine run options, for example - `$ lcc run --failed --from-report reports/report-2`

## To Do Lists

### Apis:

* [Login API](docs/apis/LoginApi.md)
* [Asset API](docs/apis/AssetApi.md)
* [Database API](docs/apis/DatabaseApi.md)
* [History API](docs/apis/HistoryApi.md)
* [NetworkBroadcast API](docs/apis/NetworkBroadcastApi.md)
* [Registration API](docs/apis/RegistrationApi.md)

### Operations:

* [Account Management](docs/operations/AccountManagement.md)
* [Assert Conditions](docs/operations/AssertConditions.md)
* [Asset Management](docs/operations/AssetManagement.md)
* [Balance Object](docs/operations/BalanceObject.md)
* [For Committee Members](docs/operations/ForCommitteeMembers.md)
* [Confidential Operations](docs/operations/ConfidentialOperations.md)
* [Contract Operations](docs/operations/ContractOperations.md)
* [Custom Extension](docs/operations/CustomExtension.md)
* [FBA](docs/operations/FBA.md)
* [Assets Market](docs/operations/AssetsMarket.md)
* [Proposal Operations](docs/operations/ProposalOperations.md)
* [Asset Transfer](docs/operations/AssetTransfer.md)
* [Vesting Balances](docs/operations/VestingBalances.md)
* [Withdrawal Permissions](docs/operations/WithdrawalPermissions.md)
* [Witness Operations](docs/operations/WitnessOperations.md)
* [Worker Operations](docs/operations/WorkerOperations.md)