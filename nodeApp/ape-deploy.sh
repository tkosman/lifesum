ape init
ape plugins install solidity
ape compile
ape plugins install infura
ape accounts import myaccount
ape run deploy_user_registry --network ethereum:sepolia:infura
