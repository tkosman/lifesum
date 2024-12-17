# scripts/deploy_user_registry.py

from ape import accounts, project, networks

def main():
    # Load the account using the alias 'myaccount'
    account = accounts.load("account")  # You will be prompted for the password

    # Use Infura's Sepolia provider as configured in ape-config.yaml
    with networks.ethereum.sepolia.use_provider("infura"):
        # Deploy the UserRegistry contract
        contract = account.deploy(project.UserRegistry)
        print(f"Contract deployed at: {contract.address}")
