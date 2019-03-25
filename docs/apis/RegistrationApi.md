# To Do List **Registration API**

## [Registration API](https://echo-dev.io/developers/apis/registration-api/#registration-api)

![](https://img.shields.io/badge/coverage-1_method(s)-red.svg?style=for-the-badge)
![](https://img.shields.io/badge/WIP-YES-informational.svg?style=for-the-badge)

#### Methods:
1) **[register_account](https://echo-dev.io/developers/apis/registration-api/#register_accountname-owner_key-active_key-memo_key-echorand_key)**  
![](https://img.shields.io/badge/1_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/7_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ##### Positive:
    - [x] registration with valid credential
    ##### Negative:
    - [x] registration with empty account name
    - [x] registration with account name length longer than 63
    - [x] registration with account name start with digit
    - [x] registration with account name is digits
    - [x] registration with account name with a special character, not hyphen
    - [x] registration with account name end with a special character
    - [x] registration with account name is uppercase
    - [ ] registration with not valid: owner ECDSA key, active ECDSA key, memo ECDSA key, ed25519 key for echorand