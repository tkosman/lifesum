from ape import accounts, project, networks

def main():
    # load_dotenv()
    # Load the securely stored account
    account = accounts.load("myaccount")

    # Use the Sepolia network with Infura
    with networks.ethereum.sepolia.use_provider("infura"):
        contract = account.deploy(project.UserRegistry)
        print(f"Contract deployed at: {contract.address}")
