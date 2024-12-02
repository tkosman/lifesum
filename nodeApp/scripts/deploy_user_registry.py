from brownie import UserRegistry, accounts
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from the .env file

def main():
    # Load the deployer account using the private key
    private_key = os.getenv("PRIVATE_KEY")
    deployer = accounts.add(private_key)
    print(deployer)

    # Deploy the contract
    user_registry = UserRegistry.deploy({"from": deployer})

    # Print the contract address
    print(f"Contract deployed at: {user_registry.address}")
