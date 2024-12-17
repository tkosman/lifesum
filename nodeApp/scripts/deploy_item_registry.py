from ape import accounts, project, networks

def main():
    account = accounts.load("accountNode")

    with networks.ethereum.sepolia.use_provider("infura"):
        contract = account.deploy(project.ItemRegistry)
        print(f"Contract deployed at: {contract.address}")