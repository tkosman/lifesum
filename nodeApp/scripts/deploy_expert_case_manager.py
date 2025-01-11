from ape import accounts, project, networks

def main():
    account = accounts.load("accountNode")

    reputation_manager_address = "0xFD96e13a1fE066B3C3F48013237B6b3CB084E345"
    user_registry_address = "0xEcF02e840D457edc1880B73FAcB4bCC7A2a9D3E7"
    item_registry_address = "0xd98974323547C3d2288ae63676539fD85748F10D"

    with networks.ethereum.sepolia.use_provider("infura"):
        contract = account.deploy(
            project.ExpertCaseManager,
            reputation_manager_address,
            user_registry_address,
            item_registry_address
        )
        print(f"ExpertCaseManager deployed at: {contract.address}")

if __name__ == "__main__":
    main()