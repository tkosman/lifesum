# scripts/deploy_user_registry.py

import os
from dotenv import load_dotenv
from brownie import UserRegistry, accounts, network

def main():
    load_dotenv()
    dev = accounts.add(os.getenv('PRIVATE_KEY'))
    print(f"Deploying from account: {dev.address}")
    user_registry = UserRegistry.deploy({'from': dev})
    print(f"Contract deployed at: {user_registry.address}")