
from brownie import UserRegistry, accounts, network, config

def main():
    deployer_account = get_deployer_account()
    deploy_contract(deployer_account)

def get_deployer_account():
    if network.show_active() == 'development':
        return accounts[0]
    else:
        return accounts.add(config['wallets']['from_key'])

def deploy_contract(deployer_account):
    print(f"Deploying from account: {deployer_account.address}")
    user_registry = UserRegistry.deploy({'from': deployer_account})
    print(f"UserRegistry deployed at: {user_registry.address}")
