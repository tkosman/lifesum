from ape import accounts, project, networks

def main():
    account = accounts.load("accountNode")

    reputation_manager_address = "0xFD96e13a1fE066B3C3F48013237B6b3CB084E345"
    user_registry_address = "0xc406212e17e862c285386406c1307d34cd26d50D"

    with networks.ethereum.sepolia.use_provider("infura"):
        contract = account.deploy(
            project.ExpertCaseManager,
            reputation_manager_address,
            user_registry_address
        )
        print(f"ExpertCaseManager deployed at: {contract.address}")

if __name__ == "__main__":
    main()